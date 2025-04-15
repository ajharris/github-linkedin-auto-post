import React from "react";

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
    </div>
  );
}

export default UserInfo;
