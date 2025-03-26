import os
from backend.models import db, User

def seed_main_user(app=None):
    from backend.app import create_app  # local import to avoid circular dependency unless needed

    if app is None:
        app = create_app()

    github_id = os.getenv("SEED_GITHUB_ID", "7585359")
    github_token = os.getenv("SEED_GITHUB_TOKEN", "placeholder_github_token")
    linkedin_token = os.getenv("SEED_LINKEDIN_TOKEN", "placeholder_linkedin_token")

    with app.app_context():
        user = User.query.filter_by(github_id=github_id).first()
        if user:
            print(f"ℹ️ User with github_id={github_id} already exists.")
            return

        user = User(
            github_id=github_id,
            github_token=github_token,
            linkedin_token=linkedin_token
        )
        db.session.add(user)
        db.session.commit()
        print(f"✅ Seeded user with github_id={github_id}")

if __name__ == "__main__":
    seed_main_user()
