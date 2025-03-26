from backend.models import db, User
from backend.scripts.seed_user import seed_main_user

def test_seed_main_user(app, monkeypatch):
    monkeypatch.setenv("SEED_GITHUB_ID", "test-user-123")
    monkeypatch.setenv("SEED_GITHUB_TOKEN", "test_gh_token")
    monkeypatch.setenv("SEED_LINKEDIN_TOKEN", "test_li_token")

    # Clear just in case
    with app.app_context():
        User.query.filter_by(github_id="test-user-123").delete()
        db.session.commit()

    # 🔥 Pass in the app here!
    seed_main_user(app)

    with app.app_context():
        user = User.query.filter_by(github_id="test-user-123").first()
        assert user is not None
        assert user.github_token == "test_gh_token"
        assert user.linkedin_token == "test_li_token"


