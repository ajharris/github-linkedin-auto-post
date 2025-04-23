import axios from "axios";

export const handleCommitSelect = (commit, setSelectedCommit, setMessage) => {
  setSelectedCommit(commit);
  setMessage(`Commit: ${commit.message}`);
};

export const postToLinkedIn = async (selectedCommit, repo, githubUserId, message, setIsPosting) => {
  if (!selectedCommit) {
    alert("Please select a commit first.");
    return;
  }
  setIsPosting(true);
  try {
    await axios.post("http://localhost:5000/webhook", {
      repository: { full_name: repo, owner: { id: githubUserId } },
      head_commit: { message },
      pusher: { name: githubUserId },
    });
    alert("Posted!");
  } catch (error) {
    alert("Failed to post. Please try again.");
  } finally {
    setIsPosting(false);
  }
};

export const postSelectedCommitToLinkedIn = async (selectedCommit, githubUserId, setIsPosting, setCommits) => {
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

export const handleGitHubLogin = () => {
  localStorage.removeItem("SECRET_GITHUB_user_id");
  const githubClientId = process.env.REACT_APPGITHUB_CLIENT_ID;
  const redirectUri = encodeURIComponent("https://github-linkedin-auto-post-e0d1a2bbce9b.herokuapp.com/auth/github/callback");
  const scope = "repo";
  const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${githubClientId}&redirect_uri=${redirectUri}&scope=${scope}`;
  window.location.href = githubAuthUrl;
};

export const handleLinkedInLogin = (githubUserId) => {
  if (!githubUserId) {
    alert("Please log in with GitHub first.");
    return;
  }

  const linkedinUrl = `https://github-linkedin-auto-post-e0d1a2bbce9b.herokuapp.com/auth/linkedin?SECRET_GITHUB_user_id=${githubUserId}`;
  console.log("[LinkedIn] Redirecting to:", linkedinUrl);
  window.location.href = linkedinUrl;
};

export const handleGitHubLogout = (setGithubUserId, setUserInfo, setCommits) => {
  localStorage.removeItem("SECRET_GITHUB_user_id");
  setGithubUserId("");
  setUserInfo(null);
  setCommits([]);
  alert("Logged out of GitHub.");
};

export const handleLinkedInDisconnect = async (githubUserId, setUserInfo) => {
  if (!githubUserId) {
    alert("You need to log in with GitHub first.");
    return;
  }

  try {
    const response = await axios.post(`/api/github/${githubUserId}/disconnect_linkedin`);
    if (response.data.status === "success") {
      setUserInfo((prev) => ({ ...prev, linked: false, linkedin_id: null }));
      alert("Disconnected LinkedIn successfully.");
    } else {
      alert("Failed to disconnect LinkedIn.");
    }
  } catch (error) {
    console.error("Error disconnecting LinkedIn:", error);
    alert("An error occurred while disconnecting LinkedIn.");
  }
};
