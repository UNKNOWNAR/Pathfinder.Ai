from . import db


class InterviewTopic(db.Model):
    topic_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), nullable=False, default='technical')  # 'technical' or 'behavioral'

    sessions = db.relationship('InterviewSession', backref='topic', lazy=True)

    def __repr__(self):
        return f'<InterviewTopic {self.name}>'

    def to_dict(self):
        return {
            'topic_id': self.topic_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
        }
