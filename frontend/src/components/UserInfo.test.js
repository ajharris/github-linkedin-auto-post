import React from 'react';
import { render, screen } from '@testing-library/react';
import UserInfo from './UserInfo';

describe('UserInfo Component', () => {
  it('renders without crashing', () => {
    render(<UserInfo />);
    expect(screen.getByTestId('user-info')).toBeInTheDocument();
  });

  // Add more specific tests based on the component's functionality
});