from app import create_app
from models import db
from models.profile import Profile

app, _ = create_app()

def clear_all_resumes():
    with app.app_context():
        print("Clearing all resume links from all profiles...")
        profiles = Profile.query.all()
        count = 0
        for profile in profiles:
            if profile.resumes:
                profile.resumes = []
                count += 1

        db.session.commit()
        print(f"Successfully cleared resume history for {count} profiles.")

if __name__ == "__main__":
    clear_all_resumes()
