import React from "react";
import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders GitHub to LinkedIn Post header", () => {
  render(<App />);
  expect(screen.getByText(/GitHub to LinkedIn Post/i)).toBeInTheDocument();
});
