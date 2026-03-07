from . import db
from datetime import datetime, timezone


class InterviewSession(db.Model):
    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('interview_topic.topic_id'), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False, default='medium')  # easy, medium, hard
    status = db.Column(db.String(20), nullable=False, default='active')  # active, completed
    greeting_text = db.Column(db.Text, nullable=True) # Personalized AI welcome
    greeting_audio_key = db.Column(db.Text, nullable=True) # S3 Key for the synthesized intro
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    questions = db.relationship('InterviewQuestion', backref='session', lazy=True, order_by='InterviewQuestion.order_index')

    def __repr__(self):
        return f'<InterviewSession {self.session_id}>'

    def to_dict(self):
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'topic_id': self.topic_id,
            'difficulty': self.difficulty,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'topic': self.topic.to_dict() if self.topic else None,
            'questions': [q.to_dict() for q in self.questions],
        }
