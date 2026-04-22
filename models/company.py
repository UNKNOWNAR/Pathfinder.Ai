from . import db

class Company(db.Model):
    company_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(20), default='pending') # pending, approved, blacklisted

    def __repr__(self):
        return f'<Company {self.name}>'

    def to_dict(self):
        return {
            'company_id': self.company_id,
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'status': self.status
        }

    # Only allow updates to relevant fields
    ALLOWED_FIELDS = {'name', 'email', 'status'}

    def updateData(self, data):
        for key, value in data.items():
            if key in Company.ALLOWED_FIELDS:
                setattr(self, key, value)
        db.session.commit()
        return True