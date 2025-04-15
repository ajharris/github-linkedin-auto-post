import React from "react";

function LoginButtons({ handleGitHubLogin, handleLinkedInLogin }) {
  return (
    <div>
      <button onClick={handleGitHubLogin}>Login with GitHub</button>
      <button onClick={handleLinkedInLogin} disabled>
        Link LinkedIn
      </button>
    </div>
  );
}

export default LoginButtons;
