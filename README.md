# Pathfinder.Ai | Placement Portal V2

Pathfinder.Ai is a robust, high-performance web application designed to manage the end-to-end campus recruitment lifecycle. It provides specialized portals for Administrators (Institute), Companies, and Students, streamlining everything from job drive approvals to automated offer letter generation.

---

## 🚀 Key Features

### **1. Role-Based Governance**
*   **Admin Dashboard**: Centralized command center with real-time analytics, company vetting, and student eligibility management.
*   **Company Portal**: Recruitment CRM where companies manage drives, shortlist candidates, and track hiring stats.
*   **Student Hub**: Personalized job discovery with eligibility-aware filtering (CGPA/Branch/Batch) and application history.

### **2. Automation & Reporting (Batch Jobs)**
*   **Automated Offer Letters**: Instant PDF generation and email delivery upon candidate selection (via Celery).
*   **Monthly Performance Reports**: Scheduled background tasks (Celery Beat) that generate high-fidelity PDF reports for the Admin.
*   **Async Data Exports**: Large-scale student and company data exports delivered as CSV files via email to prevent UI blocking.

### **3. Performance & Security**
*   **Redis Caching**: Aggressive caching of recruitment drives to ensure sub-second response times for students.
*   **Server-Side Validation**: Strict multi-factor eligibility enforcement at the API level (preventing request injection).
*   **Data Integrity**: Database-level UniqueConstraints and ON DELETE CASCADE triggers to prevent race conditions and orphaned data.

---

## 🛠️ Technology Stack

*   **Backend**: Flask (Python) with RESTful APIs.
*   **Frontend**: VueJS 3 (Vite) with a high-contrast Neubrutalist UI.
*   **Database**: SQLite (SQLAlchemy ORM).
*   **Task Queue**: Celery with Redis (Broker/Backend).
*   **Caching**: Redis.
*   **Styling**: Bootstrap 5 + Custom Modern CSS.
*   **Reporting**: xhtml2pdf for high-fidelity document generation.

---

## 📥 Installation

1.  **Clone & Extract**: Unzip the project folder.
2.  **Environment Setup**:
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Environment Variables**: Create a `.env` file in the root with your Gmail credentials:
    ```env
    MAIL_USERNAME=your-email@gmail.com
    MAIL_PASSWORD=your-app-password
    ```

---

## 🏃 Running the Application

### **The Easy Way (Recommended)**
Use the included automation script to launch everything (Redis must be installed on your system):
```powershell
.\manage.ps1 start
```

### **The Manual Way (4 Terminals)**
1.  **Flask API**: `python app.py`
2.  **Celery Worker**: `celery -A app.celery_app worker --loglevel=info`
3.  **Celery Beat**: `celery -A app.celery_app beat --loglevel=info`
4.  **Vue Frontend**: `cd pathfinder-frontend && npm run dev`

---

## 🧪 Seeding Sample Data
To populate the application with a pre-configured Admin, Students, and Companies for your demonstration:
```powershell
python seed_db.py
```

*   **Admin**: `admin / admin`
*   **Student**: `john_doe / password123`
*   **Company**: `google / password123`

---

## 📂 Project Structure
*   `app.py`: Main Flask entry point and service initialization.
*   `/api`: RESTful controllers for all platform features.
*   `/models`: Database schema and relationship definitions.
*   `/services`: Background tasks and reporting logic.
*   `/pathfinder-frontend`: Modern VueJS UI source code.
*   `api.yaml`: Official OpenAPI/Swagger documentation.

---

**Developed for IIT Madras MAD-2 Project.**