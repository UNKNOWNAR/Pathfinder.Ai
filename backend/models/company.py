from . import db
from datetime import datetime


class Company(db.Model):
    __tablename__ = 'company'

    company_id  = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.user_id'), unique=True, nullable=False)
    name        = db.Column(db.String(200), nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    created_at  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Company {self.name}>'
