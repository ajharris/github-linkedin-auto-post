import React from "react";

<<<<<<< HEAD
function CommitList({ commits, handleCommitSelect }) {
  console.log("Rendering CommitList with commits:", commits);

=======
function CommitList({ commits, onSelectCommit }) {
>>>>>>> heroku/main
  return (
    <div>
      <h3>Available Commits</h3>
      <ul>
        {commits.map((commit) => (
          <li key={commit.id}>
            <button
<<<<<<< HEAD
              onClick={() => handleCommitSelect(commit)}
=======
              onClick={() => onSelectCommit(commit)}
>>>>>>> heroku/main
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
