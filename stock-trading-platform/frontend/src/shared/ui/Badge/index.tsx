import React from 'react';

type BadgeVariant = 'blue' | 'green' | 'red' | 'yellow' | 'gray' | 'purple';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: 'sm' | 'md';
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  blue: 'bg-blue-100 text-blue-800',
  green: 'bg-green-100 text-green-800',
  red: 'bg-red-100 text-red-800',
  yellow: 'bg-yellow-100 text-yellow-800',
  gray: 'bg-gray-100 text-gray-800',
  purple: 'bg-purple-100 text-purple-800',
};

const Badge: React.FC<BadgeProps> = ({ children, variant = 'gray', size = 'sm', className = '' }) => (
  <span className={`inline-flex items-center font-medium rounded-full ${size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm'} ${variantClasses[variant]} ${className}`}>
    {children}
  </span>
);

export default Badge;
