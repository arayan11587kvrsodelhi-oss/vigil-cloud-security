import { Shield, AlertTriangle, Info, Globe } from 'lucide-react';
import clsx from 'clsx';

interface Props {
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info' | 'external' | string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

const SEVERITY_CONFIG = {
  critical: {
    icon: Shield,
    color: 'text-critical',
    bg: 'bg-critical/10',
    border: 'border-critical/30',
    label: 'Critical',
  },
  high: {
    icon: AlertTriangle,
    color: 'text-warning',
    bg: 'bg-warning/10',
    border: 'border-warning/30',
    label: 'High',
  },
  medium: {
    // Medium maps to the pink brand accent (was blue).
    icon: AlertTriangle,
    color: 'text-primary',
    bg: 'bg-primary/10',
    border: 'border-primary/30',
    label: 'Medium',
  },
  low: {
    icon: Info,
    color: 'text-text-secondary',
    bg: 'bg-text-secondary/10',
    border: 'border-text-secondary/30',
    label: 'Low',
  },
  info: {
    icon: Info,
    color: 'text-muted',
    bg: 'bg-muted/10',
    border: 'border-muted/30',
    label: 'Info',
  },
  external: {
    // External / informational maps to the purple accent.
    icon: Globe,
    color: 'text-purple-accent',
    bg: 'bg-purple-accent/10',
    border: 'border-purple-accent/30',
    label: 'External',
  },
} as const;

export default function SeverityBadge({
  severity,
  size = 'md',
  showLabel = true,
}: Props) {
  // Defensive: never assume the API enum only contains known values. Unknown or
  // missing severities fall back to a generic "info" badge rather than blanking
  // the page or throwing on undefined config.
  const normalizedSeverity = String(severity ?? 'info').trim().toLowerCase();
  const known = SEVERITY_CONFIG[normalizedSeverity as keyof typeof SEVERITY_CONFIG];

  const config = known ?? SEVERITY_CONFIG.info;

  // For an unrecognised (but present) value, surface the raw label instead of
  // silently pretending it is "Info", so the data problem stays visible.
  const label = known === undefined && normalizedSeverity ? normalizedSeverity : config.label;

  const Icon = config.icon;

  const sizeClasses =
    size === 'sm'
      ? 'text-[10px] px-1.5 py-0.5 gap-1'
      : size === 'lg'
        ? 'text-sm px-3 py-1.5 gap-2'
        : 'text-xs px-2 py-1 gap-1.5';

  return (
    <span
      className={clsx(
        'inline-flex items-center rounded border font-medium',
        config.bg,
        config.border,
        config.color,
        sizeClasses
      )}
    >
      <Icon
        className={
          size === 'sm'
            ? 'w-2.5 h-2.5'
            : size === 'lg'
              ? 'w-4 h-4'
              : 'w-3 h-3'
        }
      />

      {showLabel && <span>{label}</span>}
    </span>
  );
}