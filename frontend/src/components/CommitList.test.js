import React from 'react';
import { render, screen } from '@testing-library/react';
import CommitList from './CommitList';

describe('CommitList Component', () => {
  it('renders without crashing', () => {
    render(<CommitList commits={[]} />);
    expect(screen.getByTestId('commit-list')).toBeInTheDocument();
  });

  // Add more specific tests based on the component's functionality
});