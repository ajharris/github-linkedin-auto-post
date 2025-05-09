import React, { useState, useEffect } from "react";
import axios from "axios";
import CommitList from "./components/CommitList";
import UserInfo from "./components/UserInfo";
import PostPreview from "./components/PostPreview";
import LoginButtons from "./components/LoginButtons";
import Cookies from "js-cookie"; // Install with `npm install js-cookie`
import CryptoJS from "crypto-js"; // Install with `npm install crypto-js`
import AuthSection from "./components/AuthSection";
import CommitActions from "./components/CommitActions";
import { previewLinkedInDigest } from "./apiService"; // Import the digest preview function
const SECRET_KEY = "your-secure-key"; // Replace with a securely managed key

function App() {
  console.log("App component is mounting"); // Add this at the top of the App component
  console.log("App component is rendering"); // Debug log

  const [repo, setRepo] = useState("");
  const [message, setMessage] = useState("");
  const [githubUserId, setGithubUserId] = useState(Cookies.get("SECRET_GITHUB_user_id") || "");
  const [userInfo, setUserInfo] = useState(null);
  const [isPosting, setIsPosting] = useState(false);
  const [commits, setCommits] = useState([]);
  const [selectedCommit, setSelectedCommit] = useState(null);
  const [useDigestFormat, setUseDigestFormat] = useState(false);

  const toggleDigestFormat = () => {
    setUseDigestFormat((prev) => !prev);
  };

  const handlePreviewDigest = async () => {
    try {
      const preview = await previewLinkedInDigest(commits);
      alert(preview);
    } catch (error) {
      alert("Failed to generate digest preview.");
    }
  };

  // Check for GitHub OAuth callback with ?SECRET_GITHUB_user_id=
  useEffect(() => {
    console.log("useEffect for GitHub OAuth callback is running"); // Debug log

    // Read the GitHub user ID from the secure cookie
    const githubUserIdFromCookie = Cookies.get("SECRET_GITHUB_user_id");
    if (githubUserIdFromCookie) {
      console.log("GitHub user ID found in cookie:", githubUserIdFromCookie); // Debug log
      setGithubUserId(githubUserIdFromCookie);

      fetch(`/api/github/${githubUserIdFromCookie}/status`)
        .then((res) => res.json())
        .then((data) => {
          console.log("GitHub user status fetched:", data); // Debug log
          if (data.SECRET_GITHUB_id) {
            setUserInfo(data);
          } else {
            console.error("Invalid user status data:", data); // Debug log
          }
        })
        .catch((err) => console.error("Error fetching user status:", err)); // Debug log

      fetch(`/api/github/${githubUserIdFromCookie}/commits`)
        .then((res) => res.json())
        .then((data) => {
          console.log("Fetched commits:", data.commits); // Debug log
          if (data.commits) {
            setCommits(data.commits);
          } else {
            console.error("No commits found:", data); // Debug log
          }
        })
        .catch((err) => console.error("Error fetching commits:", err)); // Debug log
    } else {
      console.log("No GitHub user ID found in cookie"); // Debug log
    }
  }, []);

  // Fetch unposted commits after GitHub login
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = params.get("SECRET_GITHUB_user_id");

    if (id) {
      const encryptedId = CryptoJS.AES.encrypt(id, "SECRET_KEY").toString();
      sessionStorage.setItem("SECRET_GITHUB_user_id", encryptedId);
      setGithubUserId(id);
      window.history.replaceState({}, document.title, "/");
    }

    const encryptedStoredId = id || sessionStorage.getItem("SECRET_GITHUB_user_id");
    let storedId = null;
    if (encryptedStoredId) {
      try {
        const bytes = CryptoJS.AES.decrypt(encryptedStoredId, "SECRET_KEY");
        storedId = bytes.toString(CryptoJS.enc.Utf8);
      } catch (err) {
        console.error("Error decrypting stored ID:", err); // Debug log
      }
    }
    if (storedId) {
      fetch(`/api/github/${storedId}/status`)
        .then((res) => res.json())
        .then((data) => {
          console.log("GitHub user status:", data); // Debug log
          if (data.SECRET_GITHUB_id) {
            setUserInfo(data);
          }
        })
        .catch((err) => console.error("Error fetching user status:", err)); // Debug log;

      fetch(`/api/github/${storedId}/commits`)
        .then((res) => res.json())
        .then((data) => {
          console.log("Fetched commits:", data.commits); // Debug log
          if (data.commits) {
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
      await axios.post(`${process.env.REACT_APP_BACKEND_URL}/webhook`, {
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
    console.log("GitHub login initiated");
    sessionStorage.removeItem("SECRET_GITHUB_user_id"); // Clear cache
    const githubClientId = process.env.REACT_APPGITHUB_CLIENT_ID;
    const redirectUri = encodeURIComponent(`${process.env.REACT_APP_BACKEND_URL}/auth/github/callback`);
    const scope = "repo"; // Ensure the scope includes access to repositories
    const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${githubClientId}&redirect_uri=${redirectUri}&scope=${scope}`;
    
    console.log("[GitHub] Redirecting to:", githubAuthUrl); // Debug log
    window.location.href = githubAuthUrl; // Redirect to GitHub OAuth
  };
  

  const handleLinkedInLogin = () => {
    if (!githubUserId) {
      alert("Please log in with GitHub first.");
      return;
    }
  
    const linkedinUrl = `${process.env.REACT_APP_BACKEND_URL}/auth/linkedin?SECRET_GITHUB_user_id=${githubUserId}`;
    console.log("[LinkedIn] Redirecting to:", linkedinUrl); // Debug log
    window.location.href = linkedinUrl;
  };

  const handleGitHubLogout = () => {
    console.log("GitHub logout initiated");
    Cookies.remove("SECRET_GITHUB_user_id"); // Remove the secure cookie
    setGithubUserId("");
    setUserInfo(null); // Clear user info
    setCommits([]); // Clear commits
    alert("Logged out of GitHub.");
  };

  const handleLinkedInDisconnect = async () => {
    try {
      const response = await axios.post(`/api/github/${githubUserId}/disconnect_linkedin`);
      if (response.data.status === "success") {
        setUserInfo((prev) => ({ ...prev, linked: false }));
        alert("Disconnected LinkedIn successfully.");
      } else {
        alert("Failed to disconnect LinkedIn.");
      }
    } catch (error) {
      console.error("Error disconnecting LinkedIn:", error);
      alert("An error occurred while disconnecting LinkedIn.");
    }
  };

  // Debug log to verify state updates
  useEffect(() => {
    console.log("GitHub User ID:", githubUserId);
    console.log("User Info:", userInfo);
  }, [githubUserId, userInfo]);

  useEffect(() => {
    console.log("GitHub User ID:", githubUserId);
    console.log("User Info:", userInfo);
    console.log("Commits:", commits);
  }, [githubUserId, userInfo, commits]);

  const renderAuthSection = () => {
    return (
      <AuthSection
        userInfo={userInfo}
        handleGitHubLogin={handleGitHubLogin}
        handleGitHubLogout={handleGitHubLogout}
        isGitHubLoggedIn={!!githubUserId}
        handleLinkedInLogin={handleLinkedInLogin}
        handleLinkedInDisconnect={handleLinkedInDisconnect}
        isLinkedInLinked={userInfo?.linked}
      />
    );
  };

  return (
    <div style={{ padding: "20px", maxWidth: "600px", margin: "0 auto" }}>
      <h2>GitHub to LinkedIn Post</h2>
      <PostPreview selectedCommit={selectedCommit} repo={repo} />
      <CommitList commits={commits} handleCommitSelect={handleCommitSelect} />
      <CommitActions
        selectedCommit={selectedCommit}
        setSelectedCommit={setSelectedCommit}
        setMessage={setMessage}
        postToLinkedIn={postToLinkedIn}
        postSelectedCommitToLinkedIn={postSelectedCommitToLinkedIn}
      />
      <div>{renderAuthSection()}</div>
      <div>
        <label>
          <input
            type="checkbox"
            checked={useDigestFormat}
            onChange={toggleDigestFormat}
          />
          Use Digest Format
        </label>
        {useDigestFormat && (
          <button onClick={handlePreviewDigest}>Preview Digest</button>
        )}
      </div>
    </div>
  );
}

export default App;

