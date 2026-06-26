import React from 'react';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  count?: number;
}

const Skeleton: React.FC<SkeletonProps> = ({ className = '', variant = 'text', width, height, count = 1 }) => {
  const baseClass = 'animate-pulse bg-gray-200 rounded';
  const variantClass = variant === 'circular' ? 'rounded-full' : variant === 'text' ? 'rounded h-4' : 'rounded';
  const style: React.CSSProperties = {};
  if (width) style.width = typeof width === 'number' ? `${width}px` : width;
  if (height) style.height = typeof height === 'number' ? `${height}px` : height;

  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={`${baseClass} ${variantClass} ${className}`} style={count > 1 && i < count - 1 ? { ...style, marginBottom: '8px' } : style} />
      ))}
    </>
  );
};

export const CardSkeleton: React.FC = () => (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-pulse">
    <Skeleton className="w-1/3 h-5 mb-4" />
    <Skeleton className="w-full h-4 mb-2" count={3} />
  </div>
);

export const TableSkeleton: React.FC<{ rows?: number }> = ({ rows = 5 }) => (
  <div className="animate-pulse">
    <div className="flex gap-4 mb-4">
      <Skeleton className="w-1/4 h-4" />
      <Skeleton className="w-1/4 h-4" />
      <Skeleton className="w-1/4 h-4" />
      <Skeleton className="w-1/4 h-4" />
    </div>
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="flex gap-4 mb-3">
        <Skeleton className="w-1/4 h-3" />
        <Skeleton className="w-1/4 h-3" />
        <Skeleton className="w-1/4 h-3" />
        <Skeleton className="w-1/4 h-3" />
      </div>
    ))}
  </div>
);

export default Skeleton;
