from . import db
from datetime import datetime

class Application(db.Model):
    application_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.user_id', ondelete='CASCADE'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.drive_id', ondelete='CASCADE'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Not Applied') # Not Applied, Applied, Shortlisted, Selected, Rejected
    
    # Enforce uniqueness at DB level to prevent race conditions (Double applications)
    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='_student_drive_uc'),)
    def to_dict(self):
        return {
            'application_id': self.application_id,
            'student_id': self.student_id,
            'drive_id': self.drive_id,
            'job_title': self.drive.job_title if self.drive else 'N/A',
            'company_name': self.drive.company_name if self.drive else 'N/A',
            'date': self.application_date.isoformat(),
            'status': self.status,
        }

    def updateStatus(self, new_status):
        self.status = new_status
        db.session.commit()
        return True
