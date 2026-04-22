import random
from app import create_app, init_db
from models import db, User, Student, Company, PlacementDrive, Application, user_datastore
from flask_security.utils import hash_password
from datetime import datetime, timedelta

app, _ = create_app()

def seed_data():
    with app.app_context():
        # Clearing existing data (keep admin)
        Application.query.delete()
        PlacementDrive.query.delete()
        Student.query.delete()
        Company.query.delete()
        User.query.filter(User.role != 'admin').delete()
        db.session.commit()

        # 1. Create Students
        branches = ['Computer Science', 'Information Technology', 'Electronics', 'Mechanical', 'Civil']
        student_data = [
            ('john_doe', 'john@example.com'), ('alice_smith', 'alice@example.com'),
            ('bob_jones', 'bob@example.com'), ('charlie_brown', 'charlie@example.com'),
            ('david_wilson', 'david@example.com'), ('emma_davis', 'emma@example.com'),
            ('frank_miller', 'frank@example.com'), ('grace_hopper', 'grace@example.com'),
            ('henry_ford', 'henry@example.com'), ('isabella_ross', 'isabella@example.com')
        ]

        students = []
        for username, email in student_data:
            user = user_datastore.create_user(
                username=username,
                email=email,
                password=hash_password('password123'),
                role='student',
                active=True
            )
            db.session.flush() # Ensure user.user_id is populated
            student = Student(
                user_id=user.user_id,
                name=username.replace('_', ' ').title(),
                email=email,
                branch=random.choice(branches),
                batch_year=random.choice([2024, 2025]),
                cgpa=round(random.uniform(7.0, 9.8), 2)
            )
            db.session.add(student)
            students.append(student)
        
        # 2. Create Companies
        company_metadata = [
            ('Google', 'hr@google.com', 'https://google.com', 'approved'),
            ('Microsoft', 'careers@microsoft.com', 'https://microsoft.com', 'approved'),
            ('Amazon', 'hiring@amazon.com', 'https://amazon.jobs', 'approved'),
            ('Tesla', 'talent@tesla.com', 'https://tesla.com', 'pending'),
            ('Netflix', 'jobs@netflix.com', 'https://netflix.com', 'approved')
        ]

        companies = []
        for name, email, web, status in company_metadata:
            username = name.lower()
            user = user_datastore.create_user(
                username=username,
                email=email,
                password=hash_password('password123'),
                role='company',
                active=(status == 'approved')
            )
            db.session.flush() # Ensure user.user_id is populated
            company = Company(
                user_id=user.user_id,
                name=name,
                email=email,
                status=status
            )
            db.session.add(company)
            if status == 'approved':
                companies.append(company)

        db.session.commit()
        print(f"Created {len(students)} students and {len(company_metadata)} companies.")

        # 3. Create Placement Drives
        job_titles = [
            'Software Engineer', 'Data Analyst', 'Product Manager', 
            'System Architect', 'Frontend Developer', 'Mechanical Engineer',
            'SRE Intern', 'Machine Learning Engineer'
        ]

        drives = []
        for i in range(8):
            comp = random.choice(companies)
            title = random.choice(job_titles)
            branch = random.choice(branches)
            drive = PlacementDrive(
                company_id=comp.company_id,
                company_name=comp.name,
                job_title=f"{title} - {comp.name}",
                job_description=f"Exciting opportunity to join the {title} team at {comp.name}. Looking for passionate individuals.",
                eligible_branch=branch,
                cgpa_required=7.5,
                eligible_year=2025,
                application_deadline=datetime.now() + timedelta(days=random.randint(5, 30)),
                status='approved'
            )
            db.session.add(drive)
            drives.append(drive)

        db.session.commit()
        print(f"Created {len(drives)} approved placement drives.")

        # 4. Create Applications (Random)
        print("Creating random applications...")
        for s in students:
            # Each student applies to 1-3 random drives
            applied_drives = random.sample(drives, k=random.randint(1, 3))
            for d in applied_drives:
                status = random.choice(['Applied', 'Shortlisted', 'Selected', 'Rejected'])
                app_entry = Application(
                    student_id=s.user_id,
                    drive_id=d.drive_id,
                    status=status
                )
                db.session.add(app_entry)

        db.session.commit()
        print("--- Database successfully seeded! ---")
        print("Admin: admin/admin")
        print("Sample Student: john_doe/password123")
        print("Sample Company: google/password123")

if __name__ == "__main__":
    seed_data()
