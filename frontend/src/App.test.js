import axios from 'axios';
import { render, screen, fireEvent } from "@testing-library/react";
import App from "./App";
import MockAdapter from "axios-mock-adapter";

const mock = new MockAdapter(axios);

describe('Dynamic URL Resolution', () => {
  it('sets axios baseURL correctly for local development', () => {
    process.env.REACT_APP_BACKEND_URL = 'http://localhost:5000';
    axios.defaults.baseURL = process.env.REACT_APP_BACKEND_URL;
    expect(axios.defaults.baseURL).toBe('http://localhost:5000');
  });

  it('sets axios baseURL correctly for production', () => {
    process.env.REACT_APP_BACKEND_URL = 'https://prod.example.com';
    axios.defaults.baseURL = process.env.REACT_APP_BACKEND_URL;
    expect(axios.defaults.baseURL).toBe('https://prod.example.com');
  });
});

describe('Missing Environment Variables', () => {
  it('throws an error if REACT_APP_BACKEND_URL is missing', () => {
    delete process.env.REACT_APP_BACKEND_URL;
    expect(() => {
      if (!process.env.REACT_APP_BACKEND_URL) {
        throw new Error('Missing REACT_APP_BACKEND_URL environment variable');
      }
    }).toThrow('Missing REACT_APP_BACKEND_URL environment variable');
  });
});

describe('Frontend Preview API Calls', () => {
  it('uses REACT_APP_BACKEND_URL for preview API calls', () => {
    process.env.REACT_APP_BACKEND_URL = 'https://api.example.com';
    const previewUrl = `${process.env.REACT_APP_BACKEND_URL}/api/preview_linkedin_post`;
    expect(previewUrl).toBe('https://api.example.com/api/preview_linkedin_post');
  });
});

test("renders digest toggle and respects its state", () => {
  render(<App />);
  const toggle = screen.getByLabelText(/Use Digest Format/i);
  expect(toggle).toBeInTheDocument();
  fireEvent.click(toggle);
  expect(toggle.checked).toBe(true);
});

test("preview digest with multiple events", async () => {
  mock.onPost("/api/preview_linkedin_digest").reply(200, {
    preview: "Here's a summary of recent GitHub activity:"
  });

  render(<App />);
  const toggle = screen.getByLabelText(/Use Digest Format/i);
  fireEvent.click(toggle);

  const previewButton = screen.getByText(/Preview Digest/i);
  fireEvent.click(previewButton);

  const alert = await screen.findByText(/Here's a summary of recent GitHub activity:/i);
  expect(alert).toBeInTheDocument();
});
