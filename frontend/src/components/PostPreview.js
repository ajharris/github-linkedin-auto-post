import React from "react";

function PostPreview({ selectedCommit, repo }) {
  if (!selectedCommit) {
    return <p>Please select a commit to preview the LinkedIn post.</p>;
  }

  return (
    <div style={{ border: "1px solid #ccc", padding: "10px", marginTop: "20px" }}>
      <h4>LinkedIn Post Preview</h4>
      <p>
        <strong>Repository:</strong> <span>{repo || "N/A"}</span> {/* Wrap repo in a span */}
      </p>
      <p>
        <strong>Commit Message:</strong> <span>{selectedCommit.message}</span> {/* Wrap message in a span */}
      </p>
    </div>
  );
}

export default PostPreview;