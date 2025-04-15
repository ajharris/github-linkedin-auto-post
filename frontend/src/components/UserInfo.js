import React from "react";

function UserInfo({ userInfo, handleGitHubLogout, handleLinkedInLogin, handleLinkedInDisconnect }) {
  return (
    <div>
      <p>
        👤 GitHub: <strong>{userInfo.github_username}</strong> (ID: {userInfo.github_id})
      </p>
      {userInfo.linked ? (
        <>
          <p>🔗 Linked to LinkedIn ✅</p>
          <button onClick={handleLinkedInDisconnect}>Disconnect LinkedIn</button>
        </>
      ) : (
        <button onClick={handleLinkedInLogin}>Link LinkedIn</button>
      )}
      <button onClick={handleGitHubLogout}>Logout from GitHub</button>
    </div>
  );
}

export default UserInfo;
