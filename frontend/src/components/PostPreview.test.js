import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import PostPreview from './PostPreview';

describe('PostPreview Component', () => {
  test('renders default message when no content is provided', () => {
    render(<PostPreview postContent="" onEdit={jest.fn()} />);
    expect(screen.getByText('Your post content will appear here...')).toBeInTheDocument();
  });

  test('renders provided post content', () => {
    const content = 'This is a LinkedIn post preview.';
    render(<PostPreview postContent={content} onEdit={jest.fn()} />);
    expect(screen.getByText(content)).toBeInTheDocument();
  });

  test('calls onEdit when Edit Post button is clicked', () => {
    const onEditMock = jest.fn();
    render(<PostPreview postContent="Sample content" onEdit={onEditMock} />);
    fireEvent.click(screen.getByText('Edit Post'));
    expect(onEditMock).toHaveBeenCalledTimes(1);
  });
});