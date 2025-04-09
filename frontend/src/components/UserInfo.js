import React from "react";

function UserInfo({
  userInfo,
  onGitHubLogout,
  onLinkedInLogin,
  onLinkedInDisconnect,
  onGitHubLogin,
}) {
  return (
    <div>
      {userInfo ? (
        <>
          <p>
            👤 GitHub: <strong>{userInfo.github_username}</strong> (ID:{" "}
            {userInfo.github_id})
          </p>
          {userInfo.linked ? (
            <>
              <p>🔗 Linked to LinkedIn ✅</p>
              <button onClick={onLinkedInDisconnect}>Disconnect LinkedIn</button>
            </>
          ) : (
            <button onClick={onLinkedInLogin}>Link LinkedIn</button>
          )}
          <button onClick={onGitHubLogout}>Logout from GitHub</button>
        </>
      ) : (
        <>
          <button onClick={onGitHubLogin}>Login with GitHub</button>
          <button onClick={onLinkedInLogin} disabled>
            Link LinkedIn
          </button>
        </>
      )}
    </div>
  );
}

export default UserInfo;
