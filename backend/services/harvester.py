import hashlib
import threading
import requests
from models import db
from models.job import Job, HarvestLog

REMOTIVE_URL  = "https://remotive.com/api/remote-jobs"
ARBEITNOW_URL = "https://arbeitnow.com/api/job-board-api"
JSEARCH_URL   = "https://jsearch.p.rapidapi.com/search"
JSEARCH_HOST  = "jsearch.p.rapidapi.com"

# --- Glassdoor mock (no public API) ---
GLASSDOOR_MOCK = [
    {"title": "Senior Software Engineer",       "company": "Stripe",         "location": "San Francisco, CA"},
    {"title": "Backend Engineer (Python)",       "company": "Notion",         "location": "New York, NY"},
    {"title": "Full Stack Developer",            "company": "Figma",          "location": "Remote"},
    {"title": "Machine Learning Engineer",       "company": "OpenAI",         "location": "San Francisco, CA"},
    {"title": "DevOps Engineer",                 "company": "HashiCorp",      "location": "Remote"},
    {"title": "Data Engineer",                   "company": "Databricks",     "location": "Amsterdam, NL"},
    {"title": "Frontend Engineer (Vue/React)",   "company": "Linear",         "location": "Remote"},
    {"title": "Cloud Infrastructure Engineer",  "company": "Cloudflare",     "location": "Austin, TX"},
    {"title": "Site Reliability Engineer",       "company": "PagerDuty",      "location": "Remote"},
    {"title": "iOS Engineer",                    "company": "Duolingo",       "location": "Pittsburgh, PA"},
    {"title": "Android Engineer",                "company": "Discord",        "location": "Remote"},
    {"title": "Security Engineer",               "company": "Crowdstrike",    "location": "Sunnyvale, CA"},
    {"title": "Platform Engineer",               "company": "Vercel",         "location": "Remote"},
    {"title": "Staff Engineer, Infrastructure", "company": "Shopify",        "location": "Remote"},
    {"title": "Engineering Manager",            "company": "Atlassian",      "location": "Sydney, AU"},
    {"title": "Product Engineer",                "company": "Loom",           "location": "Remote"},
    {"title": "Distributed Systems Engineer",   "company": "Cockroach Labs", "location": "New York, NY"},
    {"title": "API Platform Engineer",          "company": "Twilio",         "location": "Remote"},
    {"title": "Data Scientist",                 "company": "Spotify",        "location": "Stockholm, SE"},
    {"title": "Software Engineer, Payments",    "company": "Brex",           "location": "Remote"},
]


# ── Shared utilities ───────────────────────────────────────────────────────────

def _make_hash(title: str, company: str) -> str:
    raw = f"{title.strip().lower()}|{company.strip().lower()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _insert_job(title, company, location, description, source, url):
    if not title or not company:
        return 0
    job_hash = _make_hash(title, company)
    if Job.query.filter_by(hash=job_hash).first():
        return 0
    db.session.add(Job(
        title=title, company=company, location=location,
        description=description, source=source, url=url, hash=job_hash,
    ))
    return 1


# ── Per-source fetch functions ─────────────────────────────────────────────────

def _fetch_remotive() -> list:
    res = requests.get(REMOTIVE_URL, timeout=15)
    res.raise_for_status()
    return res.json().get("jobs", [])


def _fetch_arbeitnow() -> list:
    res = requests.get(ARBEITNOW_URL, timeout=15)
    res.raise_for_status()
    return res.json().get("data", [])


def _fetch_jsearch(api_key: str) -> list:
    if not api_key:
        print("[Harvester] JSEARCH_API_KEY not set — skipping LinkedIn source.")
        return []
    res = requests.get(
        JSEARCH_URL,
        headers={"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": JSEARCH_HOST},
        params={"query": "software engineer", "num_pages": "2", "page": "1", "date_posted": "month"},
        timeout=15,
    )
    res.raise_for_status()
    return res.json().get("data", [])


# ── Source processors ──────────────────────────────────────────────────────────

def _process_remotive():
    count = 0
    for item in _fetch_remotive():
        count += _insert_job(
            title       = (item.get("title") or "").strip(),
            company     = (item.get("company_name") or "").strip(),
            location    = item.get("candidate_required_location") or "Remote",
            description = item.get("description") or "",
            source      = "Remotive",
            url         = item.get("url") or "",
        )
    return count


def _process_arbeitnow():
    count = 0
    for item in _fetch_arbeitnow():
        count += _insert_job(
            title       = (item.get("title") or "").strip(),
            company     = (item.get("company_name") or "").strip(),
            location    = item.get("location") or "Remote",
            description = item.get("description") or "",
            source      = "Arbeitnow",
            url         = item.get("url") or "",
        )
    return count


def _process_glassdoor():
    count = 0
    for item in GLASSDOOR_MOCK:
        count += _insert_job(
            title=item["title"], company=item["company"],
            location=item["location"], description="",
            source="Glassdoor", url="https://glassdoor.com",
        )
    return count


def _process_linkedin(jsearch_key):
    count = 0
    for item in _fetch_jsearch(jsearch_key):
        count += _insert_job(
            title       = (item.get("job_title") or "").strip(),
            company     = (item.get("employer_name") or "").strip(),
            location    = item.get("job_city") or item.get("job_country") or "Remote",
            description = item.get("job_description") or "",
            source      = "LinkedIn",
            url         = item.get("job_apply_link") or "",
        )
    return count


# ── Core runner (supports single source or all) ────────────────────────────────

SOURCE_MAP = {
    "Remotive":  _process_remotive,
    "Arbeitnow": _process_arbeitnow,
    "Glassdoor": _process_glassdoor,
}


def _run_harvest(app, source="all"):
    with app.app_context():
        log = HarvestLog(source=source, status="running", jobs_added=0)
        db.session.add(log)
        db.session.commit()

        try:
            jobs_added = 0
            jsearch_key = app.config.get("JSEARCH_API_KEY", "")

            if source == "all":
                jobs_added += _process_remotive()
                jobs_added += _process_arbeitnow()
                jobs_added += _process_glassdoor()
                jobs_added += _process_linkedin(jsearch_key)
            elif source == "LinkedIn":
                jobs_added += _process_linkedin(jsearch_key)
            elif source in SOURCE_MAP:
                jobs_added += SOURCE_MAP[source]()
            else:
                raise ValueError(f"Unknown source: {source}")

            db.session.commit()
            log.status     = "completed"
            log.jobs_added = jobs_added
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            log.status = "failed"
            db.session.commit()
            print(f"[Harvester] '{source}' harvest failed: {e}")


# ── Public entry points ────────────────────────────────────────────────────────

def harvest_all(app):
    thread = threading.Thread(target=_run_harvest, args=(app, "all"), daemon=True)
    thread.start()
    return thread


def harvest_source(app, source: str):
    thread = threading.Thread(target=_run_harvest, args=(app, source), daemon=True)
    thread.start()
    return thread
