import React from "react";
import ReactDOM from "react-dom/client"; // Use the new 'react-dom/client' API
import "./index.css";
import App from "./App";
import reportWebVitals from "./reportWebVitals";

const root = ReactDOM.createRoot(document.getElementById("root")); // Ensure this matches <div id="root"></div> in index.html
root.render(
  <App /> // Remove React.StrictMode temporarily
);

reportWebVitals();
