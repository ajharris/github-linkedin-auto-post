import React from "react";

function CommitList({ commits, handleCommitSelect }) {
  console.log("Rendering CommitList with commits:", commits);

  return (
    <div data-testid="commit-list">
      <h3>Available Commits</h3>
      <ul>
        {commits.map((commit) => (
          <li key={commit.id}>
            <button
              onClick={() => handleCommitSelect(commit)}
              disabled={commit.status === "posted"}
            >
              {commit.message} {commit.status === "posted" ? "✅" : ""}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CommitList;
