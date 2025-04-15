import React from "react";

function Button({ name, onClick, disabled }) {
  console.log(`Rendering Button: ${name}`); // Log the button name
  return (
    <button onClick={onClick} disabled={disabled}>
      {name}
    </button>
  );
}

export default Button;
