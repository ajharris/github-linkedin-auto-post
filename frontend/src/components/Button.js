import React from "react";

function Button({ label, onClick, disabled }) {
  console.log(`Rendering Button: ${label}`); // Log the button label
  return (
    <button onClick={onClick} disabled={disabled}>
      {label}
    </button>
  );
}

export default Button;
