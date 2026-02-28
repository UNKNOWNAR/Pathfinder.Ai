from api.auth_apis import LoginUser, SignUpUser, LogoutUser
from api.profile_api import ProfileAPI
from api.generate_resume import GenerateResume
from api.harvest_api import AdminStats, AdminHarvest, AdminLogs, AdminJobsList, JobsList
from api.company_api import CompanyRegister, AdminCompanies, AdminCompanyApprove, CompanyJobs


def init_routes(api):
    api.add_resource(LoginUser,    '/login')
    api.add_resource(SignUpUser,   '/signup')
    api.add_resource(LogoutUser,   '/logout')
    api.add_resource(ProfileAPI,   '/profile')
    api.add_resource(GenerateResume, '/generate-resume')
    api.add_resource(AdminStats,   '/admin/stats')
    api.add_resource(AdminHarvest, '/admin/harvest')
    api.add_resource(AdminLogs,    '/admin/logs')
    api.add_resource(AdminJobsList, '/admin/jobs')
    api.add_resource(CompanyRegister, '/company/register')
    api.add_resource(AdminCompanies, '/admin/companies')
    api.add_resource(AdminCompanyApprove, '/admin/companies/<int:company_id>/approve')
    api.add_resource(CompanyJobs, '/company/jobs')
    api.add_resource(JobsList, '/jobs')
