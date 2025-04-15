import React from "react";
import Button from "./Button";

function LoginButtons({
  handleGitHubLogin,
  handleGitHubLogout,
  isGitHubLoggedIn,
  handleLinkedInLogin,
  handleLinkedInDisconnect,
  isLinkedInLinked,
}) {
  console.log("Rendering LoginButtons component");
  console.log("isGitHubLoggedIn:", isGitHubLoggedIn);
  console.log("isLinkedInLinked:", isLinkedInLinked);

  return (
    <div>
      {isGitHubLoggedIn ? (
        <Button name="Logout from GitHub" onClick={handleGitHubLogout} />
      ) : (
        <Button name="Login with GitHub" onClick={handleGitHubLogin} />
      )}
      {isLinkedInLinked ? (
        <Button name="Disconnect LinkedIn" onClick={handleLinkedInDisconnect} />
      ) : (
        <Button
          name="Link LinkedIn"
          onClick={handleLinkedInLogin}
          disabled={!isGitHubLoggedIn} // Disable LinkedIn button if not logged in to GitHub
        />
      )}
    </div>
  );
}

export default LoginButtons;
