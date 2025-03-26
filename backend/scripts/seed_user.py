import os
from backend.models import db, User
from backend.app import create_app

# Create the app using your factory
app = create_app()

def seed_main_user():
    github_id = "7585359"
    github_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "placeholder_github_token")
    linkedin_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "placeholder_linkedin_token")

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
