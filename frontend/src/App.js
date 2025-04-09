import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [repo, setRepo] = useState("");
  const [message, setMessage] = useState("");
  const [githubUserId, setGithubUserId] = useState(localStorage.getItem("github_user_id") || "");
  const [userInfo, setUserInfo] = useState(null);
  const [isPosting, setIsPosting] = useState(false);
  const [commits, setCommits] = useState([]);
  const [selectedCommit, setSelectedCommit] = useState(null);

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

      fetch(`/api/github/${storedId}/commits`)
        .then(res => res.json())
        .then(data => {
          if (data.commits) {
            console.log("Fetched commits:", data.commits); // Debug log
            setCommits(data.commits);
          } else {
            console.error("No commits found:", data); // Debug log
          }
        })
        .catch(err => console.error("Error fetching commits:", err)); // Debug log
    }
  }, []);

  // Fetch unposted commits after GitHub login
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
        .then((res) => res.json())
        .then((data) => {
          if (data.github_id) {
            setUserInfo(data);
          }
        });

      fetch(`/api/github/${storedId}/commits`)
        .then((res) => res.json())
        .then((data) => {
          if (data.commits) {
            console.log("Fetched unposted commits:", data.commits); // Debug log
            setCommits(data.commits);
          } else {
            console.error("No unposted commits found:", data); // Debug log
          }
        })
        .catch((err) => console.error("Error fetching commits:", err)); // Debug log
    }
  }, []);
  

  const handleCommitSelect = (commit) => {
    setSelectedCommit(commit);
    setMessage(`Commit: ${commit.message}`);
  };

  const postToLinkedIn = async () => {
    if (!selectedCommit) {
      alert("Please select a commit first.");
      return;
    }
    setIsPosting(true);
    try {
      await axios.post("http://localhost:5000/webhook", {
        repository: { full_name: repo, owner: { id: githubUserId } },
        head_commit: { message },
        pusher: { name: githubUserId }, // fallback if needed
      });
      alert("Posted!");
    } catch (error) {
      alert("Failed to post. Please try again.");
    } finally {
      setIsPosting(false);
    }
  };

  const postSelectedCommitToLinkedIn = async () => {
    if (!selectedCommit) {
      alert("Please select a commit first.");
      return;
    }
  
    setIsPosting(true);
    try {
      const response = await axios.post(`/api/github/${githubUserId}/post_commit`, {
        commit_id: selectedCommit.id,
      });
      if (response.data.status === "success") {
        alert("Commit posted to LinkedIn successfully!");
        setCommits((prevCommits) =>
          prevCommits.map((commit) =>
            commit.id === selectedCommit.id ? { ...commit, status: "posted" } : commit
          )
        );
      } else {
        alert("Failed to post commit to LinkedIn.");
      }
    } catch (error) {
      console.error("Error posting commit to LinkedIn:", error);
      alert("An error occurred while posting the commit.");
    } finally {
      setIsPosting(false);
    }
  };

  const handleGitHubLogin = () => {
    localStorage.removeItem("github_user_id");  // clear cache
    const githubClientId = process.env.REACT_APP_GITHUB_CLIENT_ID;
    const redirectUri = encodeURIComponent("https://github-linkedin-auto-post-e0d1a2bbce9b.herokuapp.com/auth/github/callback");
    const scope = "repo"; // Ensure the scope includes access to repositories
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
    <div style={{ padding: "20px", maxWidth: "600px", margin: "0 auto" }}>
      <h2>GitHub to LinkedIn Post</h2>
      <div>
        <h3>Available Commits</h3>
        <ul>
          {commits.map((commit) => (
            <li key={commit.id}>
              <button
                onClick={() => handleCommitSelect(commit)}
                disabled={commit.status === "posted"}
              >
                {commit.message} {commit.status === "posted" ? "✅" : ""}
              </button>
            </li>
          ))}
        </ul>
      </div>
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
        <button onClick={postSelectedCommitToLinkedIn} disabled={isPosting || !selectedCommit}>
          {isPosting ? "Posting..." : "Post Selected Commit"}
        </button>
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
