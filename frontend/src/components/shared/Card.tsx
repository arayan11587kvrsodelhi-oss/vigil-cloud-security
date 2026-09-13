import clsx from 'clsx';

interface Props {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'elevated' | 'glass' | 'bordered';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export default function Card({ children, className, variant = 'default', padding = 'md' }: Props) {
  const variantClasses = {
    default: 'bg-surface border-border shadow-card',
    elevated: 'bg-elevated border-border shadow-card',
    glass: 'bg-surface/80 backdrop-blur-sm border-border shadow-card',
    bordered: 'bg-transparent border-border',
  };
  const paddingClasses = {
    none: 'p-0',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  };

  return (
    <div
      className={clsx(
        'rounded-card transition-colors duration-200',
        variantClasses[variant],
        paddingClasses[padding],
        className
      )}
    >
      {children}
    </div>
  );
}
