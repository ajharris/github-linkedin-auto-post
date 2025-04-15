import React from "react";

<<<<<<< HEAD
function UserInfo({ userInfo }) {
  if (!userInfo) {
    return <p>👤 Not logged in to GitHub</p>;
  }

  return (
    <div>
      <p>
        👤 GitHub: <strong>{userInfo.github_username}</strong> (ID: {userInfo.github_id})
      </p>
      <p>
        🔗 LinkedIn: {userInfo.linked ? "Linked ✅" : "Not linked ❌"}
      </p>
=======
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
>>>>>>> heroku/main
    </div>
  );
}

export default UserInfo;
