import csv
import os
from celery import shared_task
from datetime import datetime
from flask_mail import Message
from models import db, Student, Company, PlacementDrive, Application, mail

# Base directory for saving exports
EXPORT_DIR = os.path.join("static", "exports")
if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)


# ═══════════════════════════════════════════════════
# TASK 1: Admin/Company CSV Export (User Triggered)
# ═══════════════════════════════════════════════════
@shared_task(ignore_result=False)
def export_resource_csv(resource_type, to_email, drive_id=None):
    """
    Background task for Admin/Company CSV generation + Gmail delivery.
    Types: 'students', 'companies', 'applicants'
    """
    filename = f"{resource_type}_export.csv"
    filepath = os.path.join(EXPORT_DIR, filename)

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)

        if resource_type == 'students':
            writer.writerow(['ID', 'Name', 'Email', 'Branch', 'CGPA'])
            data = Student.query.all()
            for s in data:
                writer.writerow([s.user_id, s.name, s.email, s.branch, s.cgpa])

        elif resource_type == 'companies':
            writer.writerow(['ID', 'Name', 'Email', 'Status'])
            data = Company.query.all()
            for c in data:
                writer.writerow([c.user_id, c.name, c.email, c.status])

        elif resource_type == 'applicants' and drive_id:
            writer.writerow(['Student Name', 'Email', 'Status', 'Date'])
            apps = Application.query.filter_by(drive_id=drive_id).all()
            for a in apps:
                student = Student.query.get(a.student_id)
                writer.writerow([student.name, student.email, a.status, a.application_date])

    try:
        subject = f"Placement Portal Export: {resource_type.capitalize()}"
        msg = Message(subject, recipients=[to_email])
        msg.body = f"Attached is the requested CSV report for {resource_type}."
        with open(filepath, "rb") as f:
            msg.attach(filename, "text/csv", f.read())
        mail.send(msg)
        return f"Export sent to {to_email}"
    except Exception as e:
        print(f"[ERROR] Mail failed: {str(e)}")
        return f"CSV saved at {filepath}, but mail failed."


# ═══════════════════════════════════════════════════
# TASK 2: Student History Export (User Triggered)
# ═══════════════════════════════════════════════════
@shared_task(ignore_result=False)
def export_student_history(student_id, to_email):
    """
    Student clicks 'Export My History' -> CSV of their applications is emailed.
    """
    filename = f"student_{student_id}_history.csv"
    filepath = os.path.join(EXPORT_DIR, filename)

    apps = Application.query.filter_by(student_id=student_id).all()

    with open(filepath, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Application ID', 'Company Name', 'Job Title', 'Status', 'Applied Date'])
        for a in apps:
            drive = PlacementDrive.query.get(a.drive_id)
            writer.writerow([
                a.application_id,
                drive.company_name if drive else 'N/A',
                drive.job_title if drive else 'N/A',
                a.status,
                a.application_date
            ])

    try:
        msg = Message("Your Placement History Export", recipients=[to_email])
        msg.body = "Hi! Attached is your complete placement application history."
        with open(filepath, "rb") as f:
            msg.attach(filename, "text/csv", f.read())
        mail.send(msg)
        return f"History sent to {to_email}"
    except Exception as e:
        print(f"[ERROR] Student export mail failed: {str(e)}")
        return f"CSV saved at {filepath}, but mail failed."


# ═══════════════════════════════════════════════════
# TASK 3: Monthly HTML Report (Scheduled - 1st of Month)
# ═══════════════════════════════════════════════════
@shared_task
def monthly_report_task():
    """
    Generates an HTML report of monthly placement activity and emails it to Admin.
    Runs on the 1st of every month via Celery Beat.
    """
    from models.user import User

    # Gather stats
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_drives = PlacementDrive.query.count()
    approved_drives = PlacementDrive.query.filter_by(status='approved').count()
    total_applications = Application.query.count()
    selected_count = Application.query.filter_by(status='Selected').count()
    shortlisted_count = Application.query.filter_by(status='Shortlisted').count()
    rejected_count = Application.query.filter_by(status='Rejected').count()

    # Build HTML report
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background: #f8f9fa; padding: 40px;">
        <div style="max-width: 600px; margin: 0 auto; background: #fff; border: 1px solid #dee2e6; border-radius: 8px; overflow: hidden;">
            <div style="background: #0d6efd; color: #fff; padding: 24px; text-align: center;">
                <h1 style="margin: 0;">Pathfinder.Ai</h1>
                <p style="margin: 4px 0 0; opacity: 0.9;">Monthly Placement Activity Report</p>
            </div>
            <div style="padding: 32px;">
                <h3 style="color: #333;">Platform Overview</h3>
                <table style="width: 100%; border-collapse: collapse; margin-top: 16px;">
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 12px 8px; font-weight: bold;">Total Students</td>
                        <td style="padding: 12px 8px; text-align: right; color: #0d6efd; font-weight: bold;">{total_students}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 12px 8px; font-weight: bold;">Total Companies</td>
                        <td style="padding: 12px 8px; text-align: right; color: #ffc107; font-weight: bold;">{total_companies}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 12px 8px; font-weight: bold;">Total Drives</td>
                        <td style="padding: 12px 8px; text-align: right; color: #198754; font-weight: bold;">{total_drives}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 12px 8px; font-weight: bold;">Approved Drives</td>
                        <td style="padding: 12px 8px; text-align: right;">{approved_drives}</td>
                    </tr>
                </table>

                <h3 style="color: #333; margin-top: 24px;">Application Statistics</h3>
                <table style="width: 100%; border-collapse: collapse; margin-top: 16px;">
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 12px 8px; font-weight: bold;">Total Applications</td>
                        <td style="padding: 12px 8px; text-align: right; font-weight: bold;">{total_applications}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 12px 8px; font-weight: bold;">Selected</td>
                        <td style="padding: 12px 8px; text-align: right; color: #198754; font-weight: bold;">{selected_count}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 12px 8px; font-weight: bold;">Shortlisted</td>
                        <td style="padding: 12px 8px; text-align: right; color: #ffc107; font-weight: bold;">{shortlisted_count}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px 8px; font-weight: bold;">Rejected</td>
                        <td style="padding: 12px 8px; text-align: right; color: #dc3545; font-weight: bold;">{rejected_count}</td>
                    </tr>
                </table>
            </div>
            <div style="background: #f8f9fa; padding: 16px; text-align: center; color: #6c757d; font-size: 12px;">
                Auto-generated by Pathfinder.Ai Placement Portal
            </div>
        </div>
    </body>
    </html>
    """

    # Send to admin
    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        from models.user import User

        admin = User.query.filter_by(role='admin').first()
        admin_email = admin.email if admin else "admin@example.com"

        # Generate PDF
        pdf_filename = f"monthly_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        pdf_path = os.path.join(EXPORT_DIR, pdf_filename)
        
        with open(pdf_path, "w+b") as result_file:
            pisa_status = pisa.CreatePDF(html_body, dest=result_file)
            
        if pisa_status.err:
            return "PDF generation failed"

        msg = Message("Monthly Placement Analytics [PDF]", recipients=[admin_email])
        msg.body = "Hi Admin! Attached is your professional PDF report containing this month's placement portal analytics."
        
        with open(pdf_path, "rb") as f:
            msg.attach("monthly_report.pdf", "application/pdf", f.read())
            
        mail.send(msg)
        return f"Monthly PDF report sent to {admin_email}"
    except Exception as e:
        print(f"[ERROR] Monthly report PDF failed: {str(e)}")
        return f"Report generation failed: {str(e)}"


@shared_task
def daily_reminder_task():
    """
    Finds students who haven't applied to approved drives with upcoming deadlines.
    Runs daily via Celery Beat.
    """
    from datetime import datetime, timedelta
    from models import Student, PlacementDrive, Application, mail, Company
    from models.user import User

    # 1. Get drives closing in the next 3 days
    now = datetime.utcnow()
    deadline_threshold = now + timedelta(days=3)
    upcoming_drives = PlacementDrive.query.filter(
        PlacementDrive.status == 'approved',
        PlacementDrive.application_deadline > now,
        PlacementDrive.application_deadline <= deadline_threshold
    ).all()

    if not upcoming_drives:
        return "No upcoming deadlines to notify."

    reminders_sent = 0
    for drive in upcoming_drives:
        # SECURITY FIX: Check if the owning company is still active
        company = Company.query.get(drive.company_id)
        if not company: continue
        company_user = User.query.get(company.user_id)
        if not company_user or not company_user.active:
            continue

        # 2. Find eligible students who HAVEN'T applied to this specific drive
        students = Student.query.all()
        for s in students:
            # Skip if already applied
            already_applied = Application.query.filter_by(student_id=s.user_id, drive_id=drive.drive_id).first()
            if already_applied:
                continue
            
            # ELIGIBILITY FIX: Check Branch, CGPA, AND Batch Year
            if drive.eligible_branch and drive.eligible_branch != 'All' and drive.eligible_branch != s.branch:
                continue
            if s.cgpa < drive.cgpa_required:
                continue
            if drive.eligible_year and drive.eligible_year != s.batch_year:
                continue

            # 3. Send the reminder
            try:
                msg = Message(
                    f"Action Required: Deadline Approaching for {drive.job_title}",
                    recipients=[s.email]
                )
                msg.body = (
                    f"Hi {s.name},\n\n"
                    f"The application deadline for {drive.job_title} at {drive.company_name} is approaching on {drive.application_deadline.strftime('%d %b, %Y')}.\n\n"
                    f"You are eligible for this role but haven't applied yet! Log in to Pathfinder.Ai to submit your application before it's too late.\n\n"
                    f"Best regards,\nPathfinder.Ai Team"
                )
                mail.send(msg)
                reminders_sent += 1
            except Exception as e:
                print(f"[ERROR] Reminder failed: {str(e)}")

    return f"Sent {reminders_sent} targeted deadline reminders."


@shared_task(ignore_result=False)
def send_offer_letter(student_name, student_email, job_title, company_name):
    """
    Background task to generate and send a PDF Offer Letter to a selected student.
    """
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 50px; line-height: 1.6;">
        <div style="text-align: center; border-bottom: 3px solid #323232; padding-bottom: 20px;">
            <h1 style="margin: 0; color: #323232;">OFFER LETTER</h1>
            <h3 style="margin: 5px 0; color: #2d8cf0;">{company_name}</h3>
        </div>
        
        <div style="margin-top: 50px;">
            <p><strong>Date:</strong> {datetime.now().strftime('%d %b, %Y')}</p>
            <p><strong>To,</strong><br>{student_name}</p>
        </div>

        <div style="margin-top: 30px;">
            <p>Dear {student_name},</p>
            
            <p>We are pleased to offer you the position of <strong>{job_title}</strong> at <strong>{company_name}</strong>. 
            We were very impressed with your academic performance and your interview results.</p>
            
            <p>This offer is contingent upon your successful completion of your academic degree and your acceptance 
            of the terms and conditions of our organization.</p>
            
            <p>We look forward to having you on our team!</p>
        </div>

        <div style="margin-top: 60px;">
            <p>Sincerely,</p>
            <p><strong>Human Resources Team</strong><br>{company_name}</p>
        </div>
        
        <div style="margin-top: 100px; text-align: center; font-size: 10px; color: #666;">
            Auto-generated by Pathfinder.Ai Placement Portal
        </div>
    </body>
    </html>
    """

    filename = f"OfferLetter_{student_name.replace(' ', '_')}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)

    try:
        from xhtml2pdf import pisa
        with open(filepath, "w+b") as result_file:
            pisa.CreatePDF(html_body, dest=result_file)

        msg = Message(f"Congratulations! Offer Letter from {company_name}", recipients=[student_email])
        msg.body = f"Hi {student_name},\n\nCongratulations! We are delighted to attach your official offer letter for the {job_title} position at {company_name}.\n\nPlease find the PDF attached."
        
        with open(filepath, "rb") as f:
            msg.attach(filename, "application/pdf", f.read())
            
        mail.send(msg)
        return f"Offer letter sent to {student_email}"
    except Exception as e:
        print(f"[ERROR] Offer Letter failed: {str(e)}")
        return f"Failed: {str(e)}"
