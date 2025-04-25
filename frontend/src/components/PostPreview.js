import React from "react";

function PostPreview({ postContent, onEdit }) {
  if (!postContent) {
    return <p>Your post content will appear here...</p>;
  }

  return (
    <div style={{ border: "1px solid #ccc", padding: "10px", marginTop: "20px" }}>
      <h4>LinkedIn Post Preview</h4>
      <textarea
        style={{ width: "100%", height: "100px" }}
        value={postContent}
        readOnly
      />
      <button onClick={onEdit} style={{ marginTop: "10px" }}>
        Edit Post
      </button>
    </div>
  );
}

export default PostPreview;