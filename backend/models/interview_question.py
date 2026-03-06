from . import db


class InterviewQuestion(db.Model):
    question_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('interview_session.session_id'), nullable=False)
    order_index = db.Column(db.Integer, nullable=False, default=0)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(30), nullable=False, default='conceptual')  # conceptual, coding, behavioral
    starting_code = db.Column(db.Text, nullable=True)

    evaluation = db.relationship('InterviewEvaluation', backref='question', uselist=False, lazy=True)

    def __repr__(self):
        return f'<InterviewQuestion {self.question_id}>'

    def to_dict(self):
        return {
            'question_id': self.question_id,
            'session_id': self.session_id,
            'order_index': self.order_index,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'starting_code': self.starting_code,
            'evaluation': self.evaluation.to_dict() if self.evaluation else None,
        }
