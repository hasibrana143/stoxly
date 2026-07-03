import React from 'react';

interface LoadingSpinnerProps {
  fullScreen?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const sizes = { sm: 'h-6 w-6', md: 'h-10 w-10', lg: 'h-16 w-16' };

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ fullScreen = false, size = 'md' }) => {
  const spinner = (
    <div className="flex items-center justify-center">
      <div className={`${sizes[size]} animate-spin rounded-full border-4 border-blue-200 border-t-blue-600`} role="status" />
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-50">
        {spinner}
      </div>
    );
  }

  return (
    <div className="flex min-h-[200px] items-center justify-center">
      {spinner}
    </div>
  );
};

export default LoadingSpinner;
