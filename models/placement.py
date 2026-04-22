from . import db
from datetime import datetime

class PlacementDrive(db.Model):
    drive_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id', ondelete='CASCADE'), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    
    # Eligibility Criteria
    eligible_branch = db.Column(db.String(100), nullable=True) # e.g., 'CSE', 'All'
    cgpa_required = db.Column(db.Float, default=0.0)           # Renamed
    eligible_year = db.Column(db.Integer, nullable=True)       # e.g., 2026
    
    application_deadline = db.Column(db.DateTime, nullable=True) # Flexible for testing
    status = db.Column(db.String(20), default='pending') 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='drive', cascade="all, delete-orphan")

    ALLOWED_FIELDS = {
        'job_title', 'job_description', 
        'eligible_branch', 'cgpa_required', 'eligible_year', 
        'application_deadline', 'status', 'company_name'
    }

    def to_dict(self):
        return {
            'drive_id': self.drive_id,
            'company_id': self.company_id,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'job_description': self.job_description,
            'eligible_branch': self.eligible_branch,
            'cgpa_required': self.cgpa_required,
            'eligible_year': self.eligible_year,
            'deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

    def updateData(self, data):
        for key, value in data.items():
            if key in PlacementDrive.ALLOWED_FIELDS:
                if key == 'application_deadline' and isinstance(value, str):
                    value = datetime.fromisoformat(value)
                setattr(self, key, value)
        db.session.commit()
        return True