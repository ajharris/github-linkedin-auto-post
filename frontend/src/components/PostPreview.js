import React from "react";

function PostPreview({ selectedCommit, repo }) {
  if (!selectedCommit) {
    return <p>Please select a commit to preview the LinkedIn post.</p>;
  }

  const generatedText = `Check out this update from my repository "${repo || "N/A"}":\n\n"${selectedCommit.message}"`;

  return (
    <div style={{ border: "1px solid #ccc", padding: "10px", marginTop: "20px" }}>
      <h4>LinkedIn Post Preview</h4>
      <textarea
        style={{ width: "100%", height: "100px" }}
        value={generatedText}
        readOnly
      />
    </div>
  );
}

export default PostPreview;