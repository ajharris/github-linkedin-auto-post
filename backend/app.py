from flask import Flask
from auth import linkedin_oauth
from github_webhook import handle_github_event

app = Flask(__name__)

# LinkedIn OAuth Routes
app.register_blueprint(linkedin_oauth, url_prefix="/auth")

# GitHub Webhook Route
@app.route('/webhook/github', methods=['POST'])
def webhook():
    return handle_github_event()

if __name__ == "__main__":
    app.run(debug=True)
