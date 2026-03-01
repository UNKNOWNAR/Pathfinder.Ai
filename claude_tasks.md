# Claude Tasks / Next Steps (Phase 2: Multi-API Orchestration)

This file contains the immediate tasks for the AI assistant (Claude/Agent) to execute. The foundational backend and UI are complete. We are now scaling the Harvester Engine.

## 🚨 Global Execution Directives 🚨
- **Acknowledge and Wait**: After completing a task, STOP completely. Explain changes, ask for review, and WAIT.
- **Human Persona**: Write code and commit messages like a human developer. No AI signatures.
- **Branch Management**: Work strictly on the `prototype` branch.
- **Iterative Commits**: Commit and push after every discrete task.

---

## ~~Task 0: Fix Database Schema (Undefined Column Error)~~ [COMPLETED]
**Goal:** Fix the backend crash (`column harvest_log.source does not exist`) by writing a quick migration or running an ALTER TABLE command on PostgreSQL.
- **Action:** Since the `source` column was added to the `HarvestLog` model but the database schema wasn't updated, write a quick manual Python script to `ALTER TABLE harvest_log ADD COLUMN source VARCHAR(80) NOT NULL DEFAULT 'all';` and execute it so the stats and logs endpoints stop crashing. Alternatively, wipe the database and recreate the tables if that is faster.
- **Commit:** `"fix: update harvest_log table schema with source column"`
*(Completed by human. The `source` column has been added. The problem was Claude was trying to use a global virtual environment from an 'Electronics Store' project. No further action needed here).*

## ~~Task 1: Advanced RapidAPI Harvesters (JSearch & Active Jobs)~~ [COMPLETED]
**Goal:** Implement specialized harvester functions for the RapidAPI endpoints using the provided `.env` keys.
- **Backend Service**: In `backend/services/harvester.py`, implement `harvest_jsearch_jobs()` (for software engineering/general roles) and `harvest_active_jobs_db()`.
- **API Requests**: Ensure these functions securely read `JSEARCH_API_KEY` and `ACTIVE_JOBS_DB_KEY` from `current_app.config`.
- **Data Mapping**: Ensure the scraped data maps correctly to the `Job` model (`title`, `company`, `location`, `description`, `source`, `url`).
- **Deduplication**: Apply the exact same `_make_hash(title, company)` logic to prevent duplicates.
- **Integration**: Update `/api/admin/harvest` to execute these functions in the background thread alongside Remotive.
- **Commit**: `"feat: build and integrate JSearch and Active Jobs DB RapidAPI harvesters"`
*(Completed. Implementations added to harvester.py including hash deduplication. JSearch mapped to "LinkedIn" and ActiveJobsDB mapped to "ActiveJobsDB" source tags).*

## ~~Task 2: Job Source Statistics Endpoint~~ [COMPLETED]
**Goal:** Update the backend to return exactly how many jobs came from each API source so the Admin can track API performance.
- **Backend API**: Modify `AdminStats` GET route in `backend/api/harvest_api.py`. Instead of just a single `jobs` count, use SQLAlchemy to group by `Job.source` and return a breakdown (e.g., `{'Remotive': 120, 'JSearch': 45, 'ActiveJobsDB': 30}`).
- **Commit**: `"feat: add job source grouping to admin stats API"`
*(Completed. SQLAlchemy groupings added to harvest_api.py).*

## ~~Task 3: Admin UI - Source Breakdown & Formatter~~ [COMPLETED]
**Goal:** Update the Admin Dashboard to display the new source stats and format logs cleanly.
- **Frontend UI**: In `AdminDashboardView.vue`, update the "Stats" section to dynamically render a list or mini-grid showing the count for each specific API source (e.g., "Remotive: 120").
- **Commit**: `"feat: display job source breakdowns in Admin dashboard"`
*(Completed. Admin Dashboard Vue component updated with nested source-grid to show counts).*

---

## Phase 3: Fine-Tuning & Granular Controls
~~Task 4: Fix Harvester Log Timestamp Accuracy~~ [COMPLETED]
~~Task 5: Granular API Hardware Triggers~~ [COMPLETED]

---

## Phase 4: Company & Student Portals

## ~~Task 6: Company Registration & Admin Approval API~~ [COMPLETED]
**Goal:** Create an API flow where companies can register, but must be approved by an Admin before they can post jobs.
- **Backend Models:** Create a `Company` model (id, name, email, password_hash, is_approved, created_at). 
- **Backend API:**
  - `POST /api/company/register`: Company signs up (is_approved defaults to False).
  - `GET /api/admin/companies`: Admin views all companies (pending and approved).
  - `POST /api/admin/companies/<id>/approve`: Admin sets `is_approved = True`.
- **Commit**: `"feat: add company registration and admin approval flow"`
*(Completed. Company model and admin approval endpoints implemented and integrated).*

## ~~Task 7: Company Job Posting API~~ [COMPLETED]
**Goal:** Allow approved companies to add jobs directly to the platform database.
- **Backend API:** `POST /api/company/jobs` route that accepts title, description, location, etc.
- **Validation:** Ensure the endpoint checks if the logged-in company has `is_approved == True` before allowing the insertion.
- **Data Mapping:** Save the job to the existing `Job` table with `source="Direct"` or linked to the company ID.
- **Commit**: `"feat: allow approved companies to post jobs directly"`

## ~~Task 8: Student Job Feed UI~~ [COMPLETED]
**Goal:** Allow students to view all jobs (both harvested and company-posted).
- **Frontend UI:** Create a `JobsView.vue` (or update existing) accessible to users with the 'Student' role.
- **Integration:** Fetch jobs from `GET /api/jobs` and display them in a clean list or grid card format.
- **Commit**: `"feat: build student job feed UI"`

---

## Phase 5: The Data Engine (GraphQL Integration)
**Goal:** Build a utility that talks to LeetCode to fetch and analyze student performance for AI advice.

## ~~Task 9: Setup the LeetCode GraphQL Fetcher~~ [COMPLETED]
- **Action:** Create a utility function (e.g., in `backend/services/leetcode_client.py`) that uses a single POST request to `https://leetcode.com/graphql`.

## ~~Task 10: Define the "Master Query"~~ [COMPLETED]
- **Action:** Construct the GraphQL query to fetch exactly what is needed for perfect analysis:
  1. `submitStatsGlobal`: To see the Easy/Med/Hard completion ratios.
  2. `tagProblemCounts`: To see which topics (DP, Trees, Graphs, etc.) are their weak points.
  3. `userContestRanking`: To see if they perform well under pressure.

## ~~Task 11: Clean and Parse the JSON Data~~ [COMPLETED]
- **Action:** Write a mapping function to take the complex, nested GraphQL response and clean it into a simple, flattened Python dictionary/object that the AI engine can easily read.
- **Commit**: `"feat: build LeetCode GraphQL fetcher and data parser"`

---

## Phase 6: Missing Links (Things Left Out of Our Plan)

## ~~Task 12: Link Student Profiles to LeetCode~~ [COMPLETED]
**Goal:** We have the LeetCode fetcher, but we don't know *who* to fetch for! 
- **Action:** We need to update the Student profile (or User model) to store a `leetcode_username` string. 
- **Action:** We need to add a UI field in the frontend for students to enter and save their LeetCode username.
- **Commit**: `"feat: add leetcode username tracking to student profiles"`

---

## Phase 7: The Advice Engine UI

## ~~Task 13: Create the LeetCode Stats API~~ [COMPLETED]
**Goal:** Connect the backend to the frontend by serving the fetched LeetCode data.
- **Action:** Create a new route `GET /api/leetcode/stats` in `backend/api/profile_api.py` (or a dedicated file).
- **Action:** This route should lookup the logged-in student's `leetcode_username`, pass it to `LeetCodeClient.fetch_user_profile()`, and return the cleaned JSON stats.
*(Completed. Dedicated `leetcode_api.py` created with `LeetCodeStats` resource at `/api/leetcode/stats`. Looks up profile, validates student role, fetches from LeetCode GraphQL.)*

## ~~Task 14: Build the LeetCode Dashboard~~ [COMPLETED]
**Goal:** Turn the "Coming Soon" page into a live data visualization.
- **Action:** Update `frontend/src/views/LeetCodeView.vue`.
- **Action:** Remove the "Coming Soon" placeholder and build a Neo-Brutalist dashboard that elegantly displays their Total Solved (Easy/Med/Hard), their Contest Ranking, and their top/weak tags.
- **Commit**: `"feat: build LeetCode statistics API and frontend dashboard"`
*(Completed. Full Neo-Brutalist dashboard built with stat cards, contest performance panel, strongest topics list, and areas-to-improve chips.)*

## ~~Task 15: AI Advice Generator~~ [COMPLETED]
**Goal:** Generate actionable study advice from an LLM based on their LeetCode data.
- **Action:** In the backend `GET /api/leetcode/stats` route, build a prompt that includes the student's scraped LeetCode stats.
- **Action:** Send this prompt to the Hugging Face AI API to generate a short, encouraging 2-sentence piece of advice (e.g., "Your graph traversal skills are weak. Focus on medium-level BFS problems!").
- **Action:** Display this AI-generated advice prominently on the `LeetCodeView.vue` dashboard.
- **Commit**: `"feat: integrate AI advice generation into LeetCode dashboard"`
*(Completed. AI advice generated via Qwen2.5-Coder on HuggingFace InferenceClient. Prompt built from stats including weak/strong topics. Advice displayed in a prominent blue-accented card at the top of the dashboard.)*

---

## Phase 8: Landing Page & Company Portal UI

## ~~Task 16: Public Landing Page (`HomeView.vue`)~~ [COMPLETED]
**Goal:** Create a stunning front door for the application.
- **Action:** Build a new `frontend/src/views/HomeView.vue` component with a bold, beautiful Neo-Brutalist design.
- **Action:** Summarize the app's core features on this page (AI-powered resume generation, LeetCode analytics & interview readiness, aggregated job postings, and company direct hiring).
- **Action:** Update `frontend/src/router/index.js` to point the root route `/` to `HomeView.vue` instead of immediately redirecting to `/student`. Provide clear links to Login/Signup.
- **Commit:** `"feat: build public landing page"`

## ~~Task 17: Update Authentication for Companies~~ [COMPLETED]
**Goal:** Allow users to register as a company.
- **Action:** Update `frontend/src/views/LoginView.vue` to allow users to toggle between registering as a "Student" or a "Company".
- **Action:** When registering as a Company, hit the `POST /api/company/register` endpoint. Inform the user they must wait for admin approval before they can post jobs.
- **Commit:** `"feat: add company registration toggle to authentication UI"`

## ~~Task 18: Admin Company Approval UI~~ [COMPLETED]
**Goal:** Allow Admins to manage and approve pending company registrations.
- **Action:** Create `frontend/src/views/AdminCompaniesView.vue` (accessible only to admins). Add it to `router/index.js` and the admin sidebar/navbar.
- **Action:** Fetch all companies from `GET /api/admin/companies`.
- **Action:** Display them in a list/grid. Add an "Approve" button next to pending companies that triggers `POST /api/admin/companies/<id>/approve`.
- **Commit:** `"feat: build admin company approval UI"`

## ~~Task 19: Company Dashboard (`CompanyDashboardView.vue`)~~ [COMPLETED]
**Goal:** Provide a dedicated portal for approved companies to post jobs.
- **Action:** Create `frontend/src/views/CompanyDashboardView.vue`. Secure it so only users with the `company` role can access it.
- **Action:** Build a form for posting new jobs (Title, Description, Location, URL).
- **Action:** On submit, hit the `POST /api/company/jobs` endpoint. Show success or error messages (e.g., if they are not yet approved by an admin).
- **Commit:** `"feat: build company dashboard for direct job posting"`

---

## Phase 9: AWS-Native Semantic Match Engine (Bedrock + RDS pgvector)

**Goal:** Shift the application to a 100% AWS-Native Architecture (using your $100 AWS credits) for the Bharat Initiative. This means discarding HuggingFace in favor of **Amazon Bedrock (Titan Embeddings / Claude)** for AI, and migrating our database to **AWS RDS (PostgreSQL with pgvector)**. For local development, we will still use ChromaDB temporarily until the RDS instance is provisioned, but the embedding layer MUST immediately switch to `boto3` and AWS Bedrock.

## Task 20: Switch AI Engine to Amazon Bedrock
- **Action:** Install `boto3` into the backend (`pip install boto3`).
- **Action:** Update `services/embedding.py` and `api/leetcode_api.py`. Instead of the HuggingFace Inference API, use `boto3` to communicate with **Amazon Bedrock**. Use `amazon.titan-embed-text-v2:0` (or v1) to generate embeddings for Job Descriptions and Student Profiles.
- **Action:** Update `api/leetcode_api.py` to generate AI advice using a Bedrock LLM (like `anthropic.claude-3-haiku-20240307-v1:0` or `amazon.titan-text-lite-v1`).
- **Commit:** `"feat: migrate AI services to Amazon Bedrock (Titan & Claude)"`

## Task 21: Embedding Pipeline for Job Harvester & Profiles
- **Action:** Modify `services/harvester.py` and `api/company_api.py`. Whenever a new Job is saved, generate an embedding for its `title` + `description` via Bedrock.
- **Action:** Modify `api/profile_api.py`. Whenever a student updates their Profile, generate an embedding using Bedrock.
- **Action:** Store these embeddings in your local `ChromaDB` folder for now (as a local proxy for RDS). *Note in a `migration_notes.md` file how we will switch to RDS `pgvector` once provisioned.*
- **Commit:** `"feat: add Bedrock vector embedding pipelines for jobs and profiles"`

## Task 22: Semantic Sorting in the Job Feed
- **Action:** Rewrite the matching logic in `api/harvest_api.py` (`JobsList` GET).
- **Action:** Fetch the student's pre-calculated Bedrock profile embedding vector.
- **Action:** Perform a cosine similarity search against the Jobs in the local Vector DB to return semantically sorted results to the user with a true `% Match`.
- **Commit:** `"feat: implement Bedrock semantic job sorting in feed"`

---

## Phase 10: The Grand AWS Deployment

**Goal:** Deploy the entire stack using AWS exclusively.

## Task 23: Complete AWS Architecture Setup Guide
- **Action:** Before executing code, generate a comprehensive, step-by-step markdown guide (`aws_deployment_guide.md`) detailing exactly how the human should provision:
  1. **AWS RDS (PostgreSQL):** For the relational data and `pgvector`.
  2. **AWS EC2:** For hosting the Python Flask backend and Gunicorn.
  3. **AWS Amplify:** For hosting the Vue.js frontend repository seamlessly.
  4. **AWS IAM:** Detailed steps on creating the IAM user/policies required for `boto3` to access Bedrock securely.
- **Commit:** `"docs: write definitive AWS native deployment guide"`
