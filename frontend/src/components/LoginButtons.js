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
    <div data-testid="login-buttons">
      {isGitHubLoggedIn ? (
        <Button label="Logout from GitHub" onClick={handleGitHubLogout} />
      ) : (
        <Button label="Login with GitHub" onClick={handleGitHubLogin} />
      )}
      {isLinkedInLinked ? (
        <Button label="Disconnect LinkedIn" onClick={handleLinkedInDisconnect} />
      ) : (
        <Button
          label="Link LinkedIn"
          onClick={handleLinkedInLogin}
          disabled={!isGitHubLoggedIn} // Disable LinkedIn button if not logged in to GitHub
        />
      )}
    </div>
  );
}

export default LoginButtons;
