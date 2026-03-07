from api.auth_apis import LoginUser, SignUpUser, LogoutUser
from api.profile_api import ProfileAPI
from api.generate_resume import GenerateResume
from api.harvest_api import AdminStats, AdminHarvest, AdminLogs, AdminJobsList, JobsList, AdminQuotas
from api.company_api import CompanyRegister, AdminCompanies, AdminCompanyApprove, CompanyJobs
from api.leetcode_api import LeetCodeStats
from api.readiness_api import JobReadiness
from api.interview_api import (
    InterviewTopicList, InterviewSessionCreate, InterviewSessionDetail,
    InterviewQuestionGenerate, InterviewAnswerSubmit, InterviewQuestionAudio, seed_interview_topics,
)


def init_routes(api):
    api.add_resource(LoginUser,    '/login')
    api.add_resource(SignUpUser,   '/signup')
    api.add_resource(LogoutUser,   '/logout')
    api.add_resource(ProfileAPI,   '/profile')
    api.add_resource(GenerateResume, '/generate-resume')
    api.add_resource(AdminStats,   '/admin/stats')
    api.add_resource(AdminHarvest, '/admin/harvest')
    api.add_resource(AdminQuotas,  '/admin/quotas')
    api.add_resource(AdminLogs,    '/admin/logs')
    api.add_resource(AdminJobsList, '/admin/jobs')
    api.add_resource(CompanyRegister, '/company/register')
    api.add_resource(AdminCompanies, '/admin/companies')
    api.add_resource(AdminCompanyApprove, '/admin/companies/<int:company_id>/approve')
    api.add_resource(CompanyJobs, '/company/jobs')
    api.add_resource(JobsList, '/api/jobs')
    api.add_resource(LeetCodeStats, '/api/leetcode/stats')
    api.add_resource(JobReadiness, '/api/jobs/<int:job_id>/readiness')

    # Interview
    api.add_resource(InterviewTopicList,        '/api/interview/topics')
    api.add_resource(InterviewSessionCreate,    '/api/interview/sessions')
    api.add_resource(InterviewSessionDetail,    '/api/interview/sessions/<int:session_id>')
    api.add_resource(InterviewQuestionGenerate, '/api/interview/sessions/<int:session_id>/questions')
    api.add_resource(InterviewQuestionAudio,    '/api/interview/questions/<int:question_id>/audio')
    api.add_resource(GhostInterviewStep,        '/api/interview/ghost_step') # New Ghost Recruiter endpoint
    api.add_resource(InterviewAnswerSubmit,     '/api/interview/questions/<int:question_id>/answer')