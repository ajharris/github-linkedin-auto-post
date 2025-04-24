import React from "react";
import UserInfo from "./UserInfo";
import LoginButtons from "./LoginButtons";

const AuthSection = ({
  userInfo,
  handleGitHubLogin,
  handleGitHubLogout,
  isGitHubLoggedIn,
  handleLinkedInLogin,
  handleLinkedInDisconnect,
  isLinkedInLinked,
}) => {
  return (
    <div>
      <UserInfo userInfo={userInfo} />
      <LoginButtons
        handleGitHubLogin={handleGitHubLogin}
        handleGitHubLogout={handleGitHubLogout}
        isGitHubLoggedIn={isGitHubLoggedIn}
        handleLinkedInLogin={handleLinkedInLogin}
        handleLinkedInDisconnect={handleLinkedInDisconnect}
        isLinkedInLinked={isLinkedInLinked}
      />
    </div>
  );
};

export default AuthSection;