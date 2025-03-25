import React, { useState } from "react";
import axios from "axios";

function App() { 
  const [repo, setRepo] = useState("");
  const [message, setMessage] = useState("");

  const postToLinkedIn = async () => {
    await axios.post("http://localhost:5000/webhook", {
      repository: { full_name: repo },
      head_commit: { message },
    });
    alert("Posted!");
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>GitHub to LinkedIn Post</h2>
      <input
        type="text"
        placeholder="Repo Name"
        value={repo}
        onChange={(e) => setRepo(e.target.value)}
      />
      <br />
      <input
        type="text"
        placeholder="Commit Message"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <br />
      <button onClick={postToLinkedIn}>Post</button>
    </div>
  );
}

export default App;
