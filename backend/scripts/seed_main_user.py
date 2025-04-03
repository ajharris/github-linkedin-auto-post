import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.models import db, User

def seed_main_user(app=None):
    if app is None:
        from backend.app import create_app
        app = create_app()

    github_id = os.getenv("SEED_GITHUB_ID", "7585359")
    github_username = os.getenv("SEED_GITHUB_USERNAME", "ajharris")
    github_token = os.getenv("SEED_GITHUB_TOKEN", "placeholder_github_token")
    linkedin_id = os.getenv("SEED_LINKEDIN_ID", "1485595039")
    linkedin_token = os.getenv("SEED_LINKEDIN_TOKEN", "placeholder_linkedin_token")

    with app.app_context():
        user = User.query.filter_by(github_id=github_id).first()

        if user:
            print(f"⚠️ User with github_id={github_id} already exists — updating values.")
            user.github_username = github_username
            user.github_token = github_token
            user.linkedin_id = linkedin_id
            user.linkedin_token = linkedin_token
        else:
            print(f"➕ Creating new user with github_id={github_id}")
            user = User(
                github_id=github_id,
                github_username=github_username,
                github_token=github_token,
                linkedin_id=linkedin_id,
                linkedin_token=linkedin_token
            )
            db.session.add(user)

        db.session.commit()
        print(f"✅ Seeded user with github_id={github_id}")

if __name__ == "__main__":
    seed_main_user()
