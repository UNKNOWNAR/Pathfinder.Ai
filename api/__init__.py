from .auth_apis import LoginUser, SignUpUser, LogoutUser
from .student_api import StudentAPI, StudentStatsAPI, StudentApplicationsAPI, StudentExportAPI
from .admin_api import AdminStatsAPI, AdminApproveCompanyAPI, AdminCompaniesAPI, AdminStudentsAPI, AdminPendingDrivesAPI, AdminExportAPI, AdminToggleUserStatusAPI, AdminMonthlyReportAPI
from .placement_drive_api import CreateDriveAPI, StudentDrivesAPI, ApplicationStatusAPI, AdminDriveAPI, CompanyExportAPI, CompanyProfileAPI, CompanyStatsAPI, CompanyAllApplicantsAPI

def init_api(api):
    api.add_resource(LoginUser, '/login')
    api.add_resource(SignUpUser, '/signup')
    api.add_resource(LogoutUser, '/logout')
    api.add_resource(StudentAPI, '/student/profile')
    api.add_resource(StudentStatsAPI, '/student/stats')
    api.add_resource(StudentApplicationsAPI, '/student/applications')
    api.add_resource(StudentExportAPI, '/student/export')
    api.add_resource(AdminStatsAPI, '/admin/stats')
    api.add_resource(AdminMonthlyReportAPI, '/admin/monthly-report')
    api.add_resource(AdminApproveCompanyAPI, '/admin/approve-company/<int:company_id>')
    api.add_resource(AdminCompaniesAPI, '/admin/companies')
    api.add_resource(AdminStudentsAPI, '/admin/students')
    api.add_resource(AdminToggleUserStatusAPI, '/admin/toggle-status/<int:user_id>')
    api.add_resource(AdminPendingDrivesAPI, '/admin/all-drives')
    api.add_resource(AdminExportAPI, '/admin/export/<string:target>')
    api.add_resource(CreateDriveAPI,'/company/drive', '/company/drive/<int:drive_id>')
    api.add_resource(StudentDrivesAPI, '/student/drives')
    api.add_resource(ApplicationStatusAPI, '/company/application/<int:application_id>')
    api.add_resource(AdminDriveAPI, '/admin/drive/<int:drive_id>')
    api.add_resource(CompanyExportAPI, '/company/export/drive/<int:drive_id>')
    api.add_resource(CompanyStatsAPI, '/company/stats')
    api.add_resource(CompanyAllApplicantsAPI, '/company/applicants')
    api.add_resource(CompanyProfileAPI, '/company/profile')
    return api