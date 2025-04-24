import React from "react";

function UserInfo({ userInfo }) {
  if (!userInfo) {
    return <p>👤 Not logged in to GitHub</p>;
  }

  return (
    <div>
      <p>
        👤 GitHub: <strong>{userInfo.SECRET_GITHUB_username}</strong> (ID: {userInfo.SECRET_GITHUB_id})
      </p>
      <p>
        🔗 LinkedIn: {userInfo.linked ? "Linked ✅" : "Not linked ❌"}
      </p>
    </div>
  );
}

export default UserInfo;
