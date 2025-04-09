from dotenv import load_dotenv
import os
import requests
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

# Load environment variables from .env file
load_dotenv()

class LinkedInAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"Redirected Path: {self.path}")  # Log the full redirected path
        if "code" in self.path:
            auth_code = self.path.split("code=")[1].split("&")[0]
            print(f"Authorization Code: {auth_code}")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authorization code received. You can close this window.")
            self.server.auth_code = auth_code
        elif "error" in self.path:
            error_description = self.path.split("error_description=")[-1].replace("+", " ")
            print(f"Error: {error_description}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error occurred during authorization. Check the logs for details.")
        else:
            print("Error: Authorization code not found.")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization code not found.")

def get_authorization_code():
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI")
    scope = "r_emailaddress w_member_social"  # Update scopes to match your app's permissions
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?response_type=code"
        f"&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"
    )
    print(f"Opening browser for authorization: {auth_url}")
    webbrowser.open(auth_url)

    server_address = ("", 8080)
    httpd = HTTPServer(server_address, LinkedInAuthHandler)
    print("Waiting for authorization code...")
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
        print(f"New LinkedIn Access Token: {new_token}")
    else:
        print(f"Failed to renew token: {response.status_code}")
        print(f"Response: {response.text}")  # Log the full response for debugging

if __name__ == "__main__":
    auth_code = get_authorization_code()
    renew_linkedin_access_token(auth_code)