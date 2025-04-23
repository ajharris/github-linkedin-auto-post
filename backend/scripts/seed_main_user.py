import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.models import db, User


def seed_main_user(app=None):
    if app is None:
        from backend.app import create_app

        app = create_app()

    SECRET_GITHUB_id = os.getenv("SEED_GITHUB_ID", "7585359")
    SECRET_GITHUB_username = os.getenv("SEED_GITHUB_USERNAME", "ajharris")
    SECRET_GITHUB_TOKEN = os.getenv("SEED_GITHUB_TOKEN", "placeholderGITHUB_TOKEN")
    linkedin_id = os.getenv("SEED_LINKEDIN_ID", "1485595039")
    linkedin_token = os.getenv("SEED_LINKEDIN_TOKEN", "placeholder_linkedin_token")

    with app.app_context():
        user = User.query.filter_by(SECRET_GITHUB_id=SECRET_GITHUB_id).first()

        if user:
            print(
                f"⚠️ User with SECRET_GITHUB_id={SECRET_GITHUB_id} already exists — updating values."
            )
            user.SECRET_GITHUB_username = SECRET_GITHUB_username
            user.SECRET_GITHUB_TOKEN = SECRET_GITHUB_TOKEN
            user.linkedin_id = linkedin_id
            user.linkedin_token = linkedin_token
        else:
            print(f"➕ Creating new user with SECRET_GITHUB_id={SECRET_GITHUB_id}")
            user = User(
                SECRET_GITHUB_id=SECRET_GITHUB_id,
                SECRET_GITHUB_username=SECRET_GITHUB_username,
                SECRET_GITHUB_TOKEN=SECRET_GITHUB_TOKEN,
                linkedin_id=linkedin_id,
                linkedin_token=linkedin_token,
            )
            db.session.add(user)

        db.session.commit()
        print(f"✅ Seeded user with SECRET_GITHUB_id={SECRET_GITHUB_id}")


if __name__ == "__main__":
    seed_main_user()
