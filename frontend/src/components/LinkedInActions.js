import React from "react";

function LinkedInActions({ githubUserId, onLinkedInLogin, onLinkedInDisconnect }) {
  if (!githubUserId) {
    return (
      <button onClick={onLinkedInLogin} disabled>
        Link LinkedIn
      </button>
    );
  }

  return (
    <>
      <button onClick={onLinkedInLogin}>Link LinkedIn</button>
      <button onClick={onLinkedInDisconnect}>Disconnect LinkedIn</button>
    </>
  );
}

export default LinkedInActions;
