import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
}

const paddingClasses = { none: '', sm: 'p-3', md: 'p-4', lg: 'p-6' };

const Card: React.FC<CardProps> = ({ children, className = '', padding = 'md', hover = false }) => (
  <div className={`bg-white rounded-xl shadow-sm border border-gray-200 ${paddingClasses[padding]} ${hover ? 'hover:shadow-md transition-shadow' : ''} ${className}`}>
    {children}
  </div>
);

export const CardHeader: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`border-b border-gray-100 pb-3 mb-3 ${className}`}>{children}</div>
);

export const CardBody: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={className}>{children}</div>
);

export default Card;
