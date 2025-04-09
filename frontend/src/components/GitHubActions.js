import React from "react";

function GitHubActions({ onGitHubLogin, onGitHubLogout, githubUserId }) {
  return githubUserId ? (
    <button onClick={onGitHubLogout}>Logout from GitHub</button>
  ) : (
    <button onClick={onGitHubLogin}>Login with GitHub</button>
  );
}

export default GitHubActions;
