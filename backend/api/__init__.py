from api.auth_apis import LoginUser, SignUpUser, LogoutUser
from api.profile_api import ProfileAPI
from api.generate_resume import GenerateResume


def init_routes(api):
    api.add_resource(LoginUser, '/login')
    api.add_resource(SignUpUser, '/signup')
    api.add_resource(LogoutUser, '/logout')
    api.add_resource(ProfileAPI, '/profile')
    api.add_resource(GenerateResume, '/generate-resume')
