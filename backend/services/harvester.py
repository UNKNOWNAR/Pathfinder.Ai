import logging
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from models import db
from models.job import Job, HarvestLog
from services.utils import make_job_hash, is_fresher_role, get_day_based_toggle

# ── Configuration & Logging ────────────────────────────────────────────────────

logger = logging.getLogger(__name__)

# Base roles if none are provided
DEFAULT_ROLES = ["software engineer", "data engineer", "machine learning engineer"]
DEFAULT_LOCATIONS = ["India", "United States", "Remote"]

# Source Registry: Centralizing URLs, hosts, and mapping logic
SOURCES = {
    "Remotive": {
        "url": "https://remotive.com/api/remote-jobs",
        "params": {"search": "junior entry level fresher"},
        "type": "direct",
        "mapping": {
            "title": "title",
            "company": "company_name",
            "location": "candidate_required_location",
            "description": "description",
            "url": "url"
        }
    },
    "Arbeitnow": {
        "url": "https://arbeitnow.com/api/job-board-api",
        "type": "direct",
        "mapping": {
            "title": "title",
            "company": "company_name",
            "location": "location",
            "description": "description",
            "url": "url"
        },
        "filter_fresher": True
    },
    "LinkedIn": {
        "url": "https://jsearch.p.rapidapi.com/search",
        "host": "jsearch.p.rapidapi.com",
        "type": "rapidapi",
        "config_key": "JSEARCH_API_KEY",
        "timeout": 60,
        "mapping": {
            "title": "job_title",
            "company": "employer_name",
            "location": lambda item: item.get("job_city") or item.get("job_country") or "Remote",
            "description": "job_description",
            "url": "job_apply_link"
        }
    },
    "Internships": {
        "url": "https://internships-api.p.rapidapi.com/active-jb-7d",
        "host": "internships-api.p.rapidapi.com",
        "type": "rapidapi",
        "config_key": "INTERNSHIPS_API_KEY",
        "mapping": {
            "title": "title",
            "company": "organization",
            "location": lambda item: (item.get("locations_derived") or ["Remote"])[0],
            "description": "description_text",
            "url": "url"
        }
    },
    "GoogleJobs": {
        "url": "https://google-jobs-api.p.rapidapi.com/google-jobs",
        "host": "google-jobs-api.p.rapidapi.com",
        "type": "rapidapi",
        "config_key": "GOOGLE_JOBS_API_KEY",
        "mapping": {
            "title": "title",
            "company": "company",
            "location": "location",
            "description": "snippet",
            "url": "link"
        }
    },
}

# ── Fetching Logic ─────────────────────────────────────────────────────────────

def _get_headers(source_conf, api_key):
    headers = {"Accept": "application/json"}
    if source_conf["type"].startswith("rapidapi"):
        headers.update({
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": source_conf["host"]
        })
    return headers

def _fetch_source_raw(source_id, app_config, roles=None, locations=None):
    """Fetches raw data from a source, generating dynamic queries based on inputs."""
    conf = SOURCES[source_id]
    api_key = app_config.get(conf.get("config_key", ""), "") if conf.get("config_key") else None

    if conf.get("config_key") and not api_key:
        logger.warning(f"{conf['config_key']} not set — skipping {source_id}.")
        return [], 0 # return jobs and api_calls made

    headers = _get_headers(conf, api_key)
    timeout = conf.get("timeout", 30)
    raw_jobs = []
    api_calls = 0

    # Use provided roles/locations or fallback to defaults
    active_roles = roles if roles and len(roles) > 0 else DEFAULT_ROLES
    active_locations = locations if locations and len(locations) > 0 else DEFAULT_LOCATIONS

    try:
        if source_id == "GoogleJobs":
            for loc in active_locations:
                for role in active_roles:
                    q = f"{role} fresher entry level"
                    try:
                        res = requests.get(conf["url"], headers=headers, params={
                            "query": q, "location": loc, "experience": "Entry",
                            "language": "English", "pageSize": 10
                        }, timeout=timeout)
                        api_calls += 1
                        res.raise_for_status()
                        raw_jobs.extend(res.json().get("jobs", []))
                        time.sleep(1) # Safety delay for Rate Limits (429)
                    except Exception as e:
                        logger.error(f"Google Jobs sub-query '{q}' at '{loc}' failed: {e}")

        elif source_id == "LinkedIn":
            for loc in active_locations:
                for role in active_roles:
                    q = f"entry level junior fresher {role} {loc}"
                    try:
                        res = requests.get(conf["url"], headers=headers, params={
                            "query": q,
                            "num_pages": "1",
                            "page": "1",
                            "date_posted": "week" # Changed from month to week for fresher jobs
                        }, timeout=timeout)
                        api_calls += 1
                        res.raise_for_status()
                        data = res.json()
                        raw_jobs.extend(data.get("data", []))
                        time.sleep(1)
                    except Exception as e:
                        logger.error(f"LinkedIn sub-query '{q}' failed: {e}")

        elif source_id == "Internships":
            # Internships API doesn't take complex query strings as easily, just title filter
            for offset in [0, 10]:
                res = requests.get(conf["url"], headers=headers, params={
                    "title_filter": "intern OR internship", "description_type": "text", "offset": offset
                }, timeout=timeout)
                api_calls += 1
                res.raise_for_status()
                batch = res.json()
                if not batch: break
                raw_jobs.extend(batch)

        else:
            # Standard GET request for public APIs
            # We can try to append roles to the search param for remotive
            params = conf.get("params", {}).copy()
            if "search" in params and active_roles:
                params["search"] = f"junior entry level fresher {active_roles[0]}"

            res = requests.get(conf["url"], headers=headers, params=params, timeout=timeout)
            api_calls += 1
            res.raise_for_status()
            data = res.json()
            raw_jobs = data.get("jobs") or data.get("data") or (data if isinstance(data, list) else [])

    except Exception as e:
        logger.error(f"Fetch failed for {source_id}: {e}")
        return raw_jobs, api_calls

    return raw_jobs, api_calls

# ── Processing & Orchestration ─────────────────────────────────────────────────

def _process_job_items(source_id, raw_items, existing_hashes):
    """Maps raw items to Job models and returns a list of new Job instances."""
    conf = SOURCES[source_id]
    mapping = conf["mapping"]
    new_jobs = []

    for item in raw_items:
        try:
            fields = {}
            for target, source in mapping.items():
                fields[target] = source(item) if callable(source) else item.get(source)

            title = (fields["title"] or "").strip()
            company = (fields["company"] or "").strip()

            if not title or not company or company.lower() == "unknown":
                continue

            if conf.get("filter_fresher") and not is_fresher_role(title):
                continue

            job_hash = make_job_hash(title, company)
            if job_hash in existing_hashes:
                continue

            new_jobs.append(Job(
                title=title,
                company=company,
                location=fields.get("location") or "Remote",
                description=fields.get("description") or "",
                source=source_id,
                url=fields.get("url") or "",
                hash=job_hash
            ))
            existing_hashes.add(job_hash) # Local dedup within the run
        except Exception:
            continue

    return new_jobs

def _run_harvest(app, source="all", roles=None, locations=None):
    """Core harvest loop. Can be run for a single source or all."""
    with app.app_context():
        log = HarvestLog(source=source, status="running", jobs_added=0, api_calls=0)
        db.session.add(log)
        db.session.commit()

        try:
            logger.info("Pre-fetching existing job hashes...")
            existing_hashes = {h[0] for h in db.session.query(Job.hash).all()}
            total_added = 0
            total_api_calls = 0

            sources_to_run = list(SOURCES.keys()) if source == "all" else ([source] if source in SOURCES else [])
            if not sources_to_run:
                raise ValueError(f"Unknown source: {source}")

            # Note: We run fetches in sequence when using custom parameters to avoid
            # blowing through rate limits entirely in a few seconds.
            # However, for pure speed, we can keep the ThreadPool.
            def fetch_and_map(name):
                raw, calls = _fetch_source_raw(name, app.config, roles, locations)
                return name, raw, calls

            if source == "all":
                logger.info(f"Starting parallel fetch for {len(sources_to_run)} sources...")
                with ThreadPoolExecutor(max_workers=len(sources_to_run)) as executor:
                    futures = {executor.submit(fetch_and_map, name): name for name in sources_to_run}

                    for future in as_completed(futures):
                        name, raw_data, calls = future.result()
                        total_api_calls += calls
                        new_jobs = _process_job_items(name, raw_data, existing_hashes)

                        added = len(new_jobs)
                        if added > 0:
                            db.session.bulk_save_objects(new_jobs)
                            db.session.commit()
                            total_added += added
                        logger.info(f"Completed {name}: added {added} jobs from {calls} API calls.")
            else:
                raw_data, calls = _fetch_source_raw(source, app.config, roles, locations)
                total_api_calls += calls
                new_jobs = _process_job_items(source, raw_data, existing_hashes)
                total_added = len(new_jobs)
                if total_added > 0:
                    db.session.bulk_save_objects(new_jobs)
                    db.session.commit()
                logger.info(f"Completed {source}: added {total_added} jobs from {calls} API calls.")

            log.status = "completed"
            log.jobs_added = total_added
            log.api_calls = total_api_calls
            db.session.commit()
            logger.info(f"Total jobs added: {total_added}")

        except Exception as e:
            db.session.rollback()
            log.status = "failed"
            db.session.commit()
            logger.error(f"'{source}' harvest failed: {e}")

# ── Public Entry Points ────────────────────────────────────────────────────────

def harvest_all(app, roles=None, locations=None):
    thread = threading.Thread(target=_run_harvest, args=(app, "all", roles, locations), daemon=True)
    thread.start()
    return thread

def harvest_source(app, source: str, roles=None, locations=None):
    thread = threading.Thread(target=_run_harvest, args=(app, source, roles, locations), daemon=True)
    thread.start()
    return thread
