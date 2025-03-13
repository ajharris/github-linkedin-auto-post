GitHub to LinkedIn Auto-Post
Automatically share your GitHub repository updates to LinkedIn using this Flask + React app.  
No manual setup required—just sign in with LinkedIn and connect your GitHub repositories.

Features:
- Auto-post to LinkedIn whenever you push to GitHub  
- Secure OAuth authentication for LinkedIn and GitHub  
- Custom post templates for your updates  
- Toggle repositories to control which ones post updates  

Project Structure:
github-linkedin-auto-post/
│── backend/           # Flask API
│   │── app.py         # Main Flask app
│   │── auth.py        # LinkedIn OAuth handling
│   │── github_webhook.py  # GitHub event processing
│   │── .env           # Environment variables
│   │── requirements.txt  # Python dependencies
│── frontend/          # React Frontend
│   │── src/           # React app source code
│   │── tailwind.config.js  # TailwindCSS config
│   │── package.json   # Frontend dependencies
│── README.md          # Project documentation
│── setup_github_linkedin.sh  # Automated setup script

Installation:
1. Automatic Setup:
   Run the setup script to install everything automatically:
   chmod +x setup_github_linkedin.sh
   ./setup_github_linkedin.sh

2. Manual Setup:

   Backend Setup (Flask):
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # (Windows: venv\\Scripts\\activate)
   pip install -r requirements.txt

   Frontend Setup (React + Vite):
   cd frontend
   npm install
   npm run dev

Usage:
1. Start the Flask backend:
   cd backend
   source venv/bin/activate
   python app.py

2. Start the React frontend:
   cd frontend
   npm run dev

API Endpoints:
Method  | Endpoint          | Description  
--------|------------------|-----------------------------  
GET     | /auth/login      | Redirect to LinkedIn login  
GET     | /auth/callback   | Handle LinkedIn OAuth callback  
POST    | /webhook/github  | Receive GitHub push events  

Need Help?
If you have issues setting up, contact support at support@yourapp.com.
