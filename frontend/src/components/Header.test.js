import React from 'react';
import { render, screen } from '@testing-library/react';
import Header from './Header';

describe('Header Component', () => {
  it('renders without crashing', () => {
    render(<Header title="Test Header" />);
    expect(screen.getByText('Test Header')).toBeInTheDocument();
  });

  // Add more specific tests based on the component's functionality
});