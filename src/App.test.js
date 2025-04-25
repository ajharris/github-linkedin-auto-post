import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

// Component Render Test
test('renders auth status component without crashing', () => {
  render(<App />);
  const authStatusElement = screen.getByTestId('auth-status');
  expect(authStatusElement).toBeInTheDocument();
});

test('displays Linked or Not Linked based on props', () => {
  render(<App authStatus="Linked" />);
  expect(screen.getByText(/Linked/i)).toBeInTheDocument();

  render(<App authStatus="Not Linked" />);
  expect(screen.getByText(/Not Linked/i)).toBeInTheDocument();
});

// Auth Status Fetch Test
test('fetches LinkedIn auth status and handles loading state', async () => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      json: () => Promise.resolve({ linked: true }),
    })
  );

  render(<App />);
  expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  expect(await screen.findByText(/Linked/i)).toBeInTheDocument();
});

// State Update Test
test('updates auth status dynamically', () => {
  const { rerender } = render(<App authStatus="Not Linked" />);
  expect(screen.getByText(/Not Linked/i)).toBeInTheDocument();

  rerender(<App authStatus="Linked" />);
  expect(screen.getByText(/Linked/i)).toBeInTheDocument();
});

// Conditional UI Elements
test('shows Link LinkedIn Account button if not authenticated', () => {
  render(<App authStatus="Not Linked" />);
  expect(screen.getByText(/Link LinkedIn Account/i)).toBeInTheDocument();
});

test('shows Unlink button if authenticated', () => {
  render(<App authStatus="Linked" />);
  expect(screen.getByText(/Unlink/i)).toBeInTheDocument();
});