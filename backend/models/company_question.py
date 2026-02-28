from . import db


class CompanyQuestion(db.Model):
    __tablename__ = 'company_question'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False, index=True)
    problem_title = db.Column(db.String(255), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    frequency = db.Column(db.Float, nullable=True)
    acceptance_rate = db.Column(db.Float, nullable=True)
    leetcode_url = db.Column(db.String(512), nullable=True)
    topics = db.Column(db.JSON, nullable=True)
    time_window = db.Column(db.String(50), nullable=False, default='all')

    def __repr__(self):
        return f'<CompanyQuestion {self.problem_title} @ {self.company_name}>'
