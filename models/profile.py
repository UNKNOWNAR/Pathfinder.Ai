from . import db

class Profile(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    headline = db.Column(db.String(255), nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(255), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    github = db.Column(db.String(255), nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    portfolio = db.Column(db.String(255), nullable=True)
    skills = db.Column(db.JSON, nullable=True)
    experience = db.Column(db.JSON, nullable=True)
    education = db.Column(db.JSON, nullable=True)
    projects = db.Column(db.JSON, nullable=True)
    achievements = db.Column(db.JSON, nullable=True)
    
    def __repr__(self):
        return f'<Profile {self.name}>'

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'headline': self.headline,
            'photo': self.photo,
            'location': self.location,
            'phone': self.phone,
            'summary': self.summary,
            'github': self.github,
            'linkedin': self.linkedin,
            'portfolio': self.portfolio,
            'skills': self.skills,
            'experience': self.experience,
            'education': self.education,
            'projects': self.projects,
            'achievements': self.achievements
        }

    ALLOWED_FIELDS = {'name', 'headline', 'photo', 'location', 'phone', 
                  'summary', 'github', 'linkedin', 'portfolio',
                  'skills', 'experience', 'education', 'projects', 'achievements'}

    def updateData(self, data):
        for key, value in data.items():
            if key in Profile.ALLOWED_FIELDS:
                setattr(self, key, value)#update all the data from the payload as per the allowed fields
        return self

