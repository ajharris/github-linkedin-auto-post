import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [repo, setRepo] = useState("");
  const [message, setMessage] = useState("");
  const [githubUserId, setGithubUserId] = useState(localStorage.getItem("github_user_id") || "");
  const [userInfo, setUserInfo] = useState(null);


  // Check for GitHub OAuth callback with ?github_user_id=
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("github_user_id");
  
    if (id) {
      localStorage.setItem("github_user_id", id);
      setGithubUserId(id);
      window.history.replaceState({}, document.title, "/");
    }
  
    const storedId = id || localStorage.getItem("github_user_id");
    if (storedId) {
      fetch(`/api/github/${storedId}/status`)
        .then(res => res.json())
        .then(data => {
          if (data.github_id) {
            setUserInfo(data);
          }
        });
    }
  }, []);
  

  const postToLinkedIn = async () => {
    await axios.post("http://localhost:5000/webhook", {
      repository: { full_name: repo, owner: { id: githubUserId } },
      head_commit: { message },
      pusher: { name: githubUserId }, // fallback if needed
    });
    alert("Posted!");
  };

  const handleGitHubLogin = () => {
    localStorage.removeItem("github_user_id");  // clear cache
    const githubClientId = process.env.REACT_APP_GITHUB_CLIENT_ID;
    const redirectUri = encodeURIComponent("https://github-linkedin-auto-post-e0d1a2bbce9b.herokuapp.com/auth/github/callback");
    const scope = "read:user";
    const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${githubClientId}&redirect_uri=${redirectUri}&scope=${scope}`;
    window.location.href = githubAuthUrl;
  };
  

  const handleLinkedInLogin = () => {
    if (!githubUserId) {
      alert("Please log in with GitHub first.");
      return;
    }
    const linkedinUrl = `https://github-linkedin-auto-post-e0d1a2bbce9b.herokuapp.com/auth/linkedin?github_user_id=${githubUserId}`;
    window.location.href = linkedinUrl;
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>GitHub to LinkedIn Post</h2>
      <input
        type="text"
        placeholder="Repo Name"
        value={repo}
        onChange={(e) => setRepo(e.target.value)}
      />
      <br />
      <input
        type="text"
        placeholder="Commit Message"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <br />
      <div>
      <button onClick={postToLinkedIn}>Post</button>
      <br />
      <button onClick={handleGitHubLogin}>Login with GitHub</button>
      <button onClick={handleLinkedInLogin}>Link LinkedIn</button>
      {userInfo ? (
      <div>
        <p>👤 GitHub: <strong>{userInfo.github_username}</strong> (ID: {userInfo.github_id})</p>
        {userInfo.linked ? (
          <p>🔗 Linked to LinkedIn ✅</p>
        ) : (
          <p>❌ Not linked to LinkedIn yet</p>
        )}
      </div>
    ) : (
      <p>GitHub User ID: {githubUserId || "Not logged in"}</p>
    )}

      </div> 
    </div>
  );
}

export default App;
