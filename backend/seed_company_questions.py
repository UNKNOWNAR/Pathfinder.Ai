"""
Seed script to import LeetCode company-tagged interview questions.

Downloads the liquidslr/interview-company-wise-problems GitHub repo as a ZIP,
extracts it, parses company CSV files, and loads them into the CompanyQuestion table.

Usage:
    cd backend
    python seed_company_questions.py
"""

import os
import sys
import csv
import io
import zipfile
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

REPO_ZIP_URL = "https://github.com/liquidslr/interview-company-wise-problems/archive/refs/heads/main.zip"

# Map CSV filenames to time window labels
TIME_WINDOW_MAP = {
    "1. Thirty Days.csv": "30days",
    "2. Three Months.csv": "3months",
    "3. Six Months.csv": "6months",
    "4. More Than Six Months.csv": "6months_plus",
    "5. All.csv": "all",
}


def download_and_extract(url):
    """Download the repo ZIP and extract to memory."""
    logger.info("Downloading repo ZIP from GitHub (this may take a minute)...")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    logger.info(f"Downloaded {len(resp.content) / 1024 / 1024:.1f} MB")
    return zipfile.ZipFile(io.BytesIO(resp.content))


def parse_csv_content(csv_text):
    """Parse a single CSV file's text content into a list of row dicts."""
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = []
    for row in reader:
        topics_raw = row.get("Topics", "")
        topics_list = [t.strip() for t in topics_raw.split(",") if t.strip()]

        freq = row.get("Frequency", "0")
        accept = row.get("Acceptance Rate", "0")

        try:
            freq = float(freq)
        except (ValueError, TypeError):
            freq = 0.0

        try:
            accept = float(accept)
        except (ValueError, TypeError):
            accept = 0.0

        rows.append({
            "problem_title": row.get("Title", "").strip(),
            "difficulty": row.get("Difficulty", "").strip().upper(),
            "frequency": freq,
            "acceptance_rate": accept,
            "leetcode_url": row.get("Link", "").strip(),
            "topics": topics_list,
        })
    return rows


def seed_database(zf):
    """Walk the extracted ZIP and insert company questions into the DB."""
    from app import app
    from models import db
    from models.company_question import CompanyQuestion

    # Find the root folder inside the ZIP (e.g., "interview-company-wise-problems-main/")
    top_dirs = set()
    for name in zf.namelist():
        parts = name.split("/")
        if len(parts) > 1:
            top_dirs.add(parts[0])
    repo_root = list(top_dirs)[0] if top_dirs else ""

    # Gather all company directories
    companies = set()
    for name in zf.namelist():
        parts = name.replace(repo_root + "/", "", 1).split("/")
        if len(parts) == 2 and parts[1] in TIME_WINDOW_MAP:
            companies.add(parts[0])

    logger.info(f"Found {len(companies)} companies in the dataset.")

    with app.app_context():
        # Clear existing data for a clean seed
        existing = CompanyQuestion.query.count()
        if existing > 0:
            logger.info(f"Clearing {existing} existing records...")
            CompanyQuestion.query.delete()
            db.session.commit()

        total_inserted = 0
        batch = []

        for company_name in sorted(companies):
            # Only import "5. All.csv" for the comprehensive dataset
            csv_path = f"{repo_root}/{company_name}/5. All.csv"

            if csv_path not in zf.namelist():
                continue

            try:
                csv_text = zf.read(csv_path).decode("utf-8")
            except Exception as e:
                logger.warning(f"Could not read CSV for {company_name}: {e}")
                continue

            rows = parse_csv_content(csv_text)

            for row in rows:
                if not row["problem_title"]:
                    continue

                batch.append(CompanyQuestion(
                    company_name=company_name,
                    problem_title=row["problem_title"],
                    difficulty=row["difficulty"],
                    frequency=row["frequency"],
                    acceptance_rate=row["acceptance_rate"],
                    leetcode_url=row["leetcode_url"],
                    topics=row["topics"],
                    time_window="all",
                ))

            # Batch insert every 500 records
            if len(batch) >= 500:
                db.session.bulk_save_objects(batch)
                db.session.commit()
                total_inserted += len(batch)
                batch = []

        # Flush remaining
        if batch:
            db.session.bulk_save_objects(batch)
            db.session.commit()
            total_inserted += len(batch)

        logger.info(f"Seeding complete! Inserted {total_inserted} questions across {len(companies)} companies.")


def main():
    zf = download_and_extract(REPO_ZIP_URL)
    seed_database(zf)
    zf.close()


if __name__ == "__main__":
    main()
