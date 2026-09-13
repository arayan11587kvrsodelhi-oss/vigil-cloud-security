import { motion } from 'framer-motion';

interface Props {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  showLabel?: boolean;
}

export default function SecurityScoreGauge({ score, size = 'md', label = 'Security Score', showLabel = true }: Props) {
  const radius = size === 'sm' ? 36 : size === 'md' ? 54 : 72;
  const strokeWidth = size === 'sm' ? 5 : size === 'md' ? 7 : 9;
  const circumference = 2 * Math.PI * radius;
  const progress = Math.min(Math.max(score, 0), 100);
  const offset = circumference - (progress / 100) * circumference;

  // Numeric label colour stays semantically meaningful (healthy/warning/critical).
  const getScoreColor = (s: number) => {
    if (s >= 80) return '#35E0A1';
    if (s >= 60) return '#FFB84D';
    if (s >= 40) return '#FFB84D';
    return '#FF3B6B';
  };

  // The arc itself uses the pink -> purple brand gradient.
  const gradientId = `score-grad-${size}`;

  const getScoreLabel = (s: number) => {
    if (s >= 90) return 'Excellent';
    if (s >= 80) return 'Good';
    if (s >= 60) return 'Needs Work';
    if (s >= 40) return 'At Risk';
    return 'Critical';
  };

  const fontSize = size === 'sm' ? 'text-sm' : size === 'md' ? 'text-xl' : 'text-3xl';
  const labelSize = size === 'sm' ? 'text-[10px]' : size === 'md' ? 'text-xs' : 'text-sm';

  return (
    <div className="relative flex flex-col items-center justify-center">
      <svg width={(radius + strokeWidth) * 2} height={(radius + strokeWidth) * 2} className="transform -rotate-90">
        {/* Background circle */}
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FF2DAA" />
            <stop offset="100%" stopColor="#9B5CFF" />
          </linearGradient>
        </defs>
        <circle
          cx={radius + strokeWidth}
          cy={radius + strokeWidth}
          r={radius}
          fill="none"
          stroke="#2A1542"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <motion.circle
          cx={radius + strokeWidth}
          cy={radius + strokeWidth}
          r={radius}
          fill="none"
          stroke={`url(#${gradientId})`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: 'easeOut' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`${fontSize} font-bold`} style={{ color: getScoreColor(score) }}>{Math.round(score)}</span>
        {showLabel && (
          <span className={`${labelSize} text-text-secondary font-medium`}>{getScoreLabel(score)}</span>
        )}
      </div>
      {showLabel && label && (
        <div className={`mt-1 ${labelSize} text-muted font-medium`}>{label}</div>
      )}
    </div>
  );
}