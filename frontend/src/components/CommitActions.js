import React from "react";

const CommitActions = ({
  selectedCommit,
  setSelectedCommit,
  setMessage,
  postToLinkedIn,
  postSelectedCommitToLinkedIn,
}) => {
  const handleCommitSelect = (commit) => {
    setSelectedCommit(commit);
    setMessage(`Commit: ${commit.message}`);
  };

  return (
    <div>
      {selectedCommit && (
        <button onClick={() => alert("Previewing LinkedIn post!")}>Preview LinkedIn Post</button>
      )}
      <button onClick={postToLinkedIn}>Post to LinkedIn</button>
      <button onClick={postSelectedCommitToLinkedIn}>Post Selected Commit</button>
    </div>
  );
};

export default CommitActions;