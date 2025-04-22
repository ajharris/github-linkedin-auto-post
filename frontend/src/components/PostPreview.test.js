import React from "react";
import { render, screen } from "@testing-library/react";
import PostPreview from "./PostPreview";

describe("PostPreview Component", () => {
  it("renders a message when no commit is selected", () => {
    render(<PostPreview selectedCommit={null} repo="test-repo" />);
    expect(screen.getByText(/please select a commit to preview the linkedin post/i)).toBeInTheDocument();
  });

  it("renders the LinkedIn post preview when a commit is selected", () => {
    const selectedCommit = { message: "Initial commit" };
    render(<PostPreview selectedCommit={selectedCommit} repo="test-repo" />);
    expect(screen.getByText(/repository:/i)).toHaveTextContent("Repository: test-repo");
    expect(screen.getByText(/commit message:/i)).toHaveTextContent("Commit Message: Initial commit");
  });
});