from . import db
from datetime import datetime, timezone


class InterviewEvaluation(db.Model):
    evaluation_id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('interview_question.question_id'), nullable=False, unique=True)
    voice_answer = db.Column(db.Text, nullable=True)
    code_answer = db.Column(db.Text, nullable=True)
    score = db.Column(db.Integer, nullable=False, default=0)  # 0-100
    strengths = db.Column(db.Text, nullable=True)
    improvements = db.Column(db.Text, nullable=True)
    ideal_answer = db.Column(db.Text, nullable=True)
    evaluated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<InterviewEvaluation {self.evaluation_id}>'

    def to_dict(self):
        return {
            'evaluation_id': self.evaluation_id,
            'question_id': self.question_id,
            'voice_answer': self.voice_answer,
            'code_answer': self.code_answer,
            'score': self.score,
            'strengths': self.strengths,
            'improvements': self.improvements,
            'ideal_answer': self.ideal_answer,
            'evaluated_at': self.evaluated_at.isoformat(),
        }
