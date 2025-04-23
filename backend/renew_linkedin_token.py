from dotenv import load_dotenv
import os
import requests
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

# Load environment variables from .env file
load_dotenv()

class LinkedInAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if "code" in self.path:
            auth_code = self.path.split("code=")[1].split("&")[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization code received. You can close this window.")
            self.server.auth_code = auth_code
        elif "error" in self.path:
            error_description = self.path.split("error_description=")[-1].replace("+", " ")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error occurred during authorization. Check the logs for details.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization code not found.")

def get_authorization_code():
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI")
    scope = "w_member_social"
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?response_type=code"
        f"&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"
    )
    webbrowser.open(auth_url)

    server_address = ("", 8080)
    httpd = HTTPServer(server_address, LinkedInAuthHandler)
    httpd.handle_request()
    return httpd.auth_code

def renew_linkedin_access_token(auth_code):
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    payload = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": os.getenv("LINKEDIN_REDIRECT_URI"),
        "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET"),
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        new_token = response.json().get("access_token")
    else:
        pass

if __name__ == "__main__":
    auth_code = get_authorization_code()
    renew_linkedin_access_token(auth_code)