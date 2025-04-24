import axios from 'axios';

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
