import React, { useState } from "react";
import axios from "axios";

function App() { 
  const [repo, setRepo] = useState("");
  const [message, setMessage] = useState("");

  const postToLinkedIn = async () => {
    await axios.post("http://localhost:5000/webhook", { 
      repository: { full_name: repo },
      head_commit: { message },
    });
    alert("Posted!");
  };

  const handleGitHubLogin = () => {
    const githubClientId = process.env.REACT_APP_GITHUB_CLIENT_ID;
    const redirectUri = encodeURIComponent("https://github-linkedin-auto-post-e0d1a2bbce9b.herokuapp.com/auth/github/callback");
    const scope = "read:user";
    const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${githubClientId}&redirect_uri=${redirectUri}&scope=${scope}`;
    window.location.href = githubAuthUrl;
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
      <button onClick={postToLinkedIn}>Post</button>
      <button onClick={handleGitHubLogin}>Login with GitHub</button>

    </div>
  );
}

export default App;
