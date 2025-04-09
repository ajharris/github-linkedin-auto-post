import React, { useState, useEffect } from "react";
import axios from "axios";
import CommitList from "./components/CommitList";
import UserInfo from "./components/UserInfo";
import Header from "./components/Header";
import LinkedInActions from "./components/LinkedInActions";
import GitHubActions from "./components/GitHubActions";
import {
  handleCommitSelect,
  postToLinkedIn,
  postSelectedCommitToLinkedIn,
  handleGitHubLogin,
  handleLinkedInLogin,
  handleGitHubLogout,
  handleLinkedInDisconnect,
} from "./utils/githubLinkedInActions";

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
  

  return (
    <div style={{ padding: "20px", maxWidth: "600px", margin: "0 auto" }}>
      <Header />
      <CommitList commits={commits} onSelectCommit={(commit) => handleCommitSelect(commit, setSelectedCommit, setMessage)} />
      <UserInfo
        userInfo={userInfo}
        onGitHubLogout={() => handleGitHubLogout(setGithubUserId, setUserInfo, setCommits)}
        onLinkedInLogin={() => handleLinkedInLogin(githubUserId)}
        onLinkedInDisconnect={() => handleLinkedInDisconnect(githubUserId, setUserInfo)}
        onGitHubLogin={handleGitHubLogin}
      />
      <LinkedInActions
        githubUserId={githubUserId}
        onLinkedInLogin={() => handleLinkedInLogin(githubUserId)}
        onLinkedInDisconnect={() => handleLinkedInDisconnect(githubUserId, setUserInfo)}
      />
      <GitHubActions
        onGitHubLogin={handleGitHubLogin}
        onGitHubLogout={() => handleGitHubLogout(setGithubUserId, setUserInfo, setCommits)}
        githubUserId={githubUserId}
      />
    </div>
  );
}

export default App;
