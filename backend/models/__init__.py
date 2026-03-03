from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.profile import Profile
from models.job import Job, HarvestLog
from models.company import Company
from models.company_question import CompanyQuestion
from models.interview_topic import InterviewTopic
from models.interview_session import InterviewSession
from models.interview_question import InterviewQuestion
from models.interview_evaluation import InterviewEvaluation