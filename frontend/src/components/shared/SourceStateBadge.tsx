import clsx from 'clsx';

/**
 * Small, non-decorative data-provenance indicator.
 *
 * Only states that are actually true should be used:
 *  - demo       : demonstration build data
 *  - simulated  : generated/simulated telemetry (not from a live source)
 *  - live       : retrieved live from a configured source
 *  - cached     : served from a local cache
 *  - fallback   : a fallback path was used (e.g. DB unavailable)
 *  - api-ready  : the integration exists but is not connected
 */
export type SourceState = 'demo' | 'simulated' | 'live' | 'cached' | 'fallback' | 'api-ready';

interface Props {
  state?: string | null;
  size?: 'sm' | 'md';
  className?: string;
}

const CONFIG: Record<SourceState, { label: string; dot: string; text: string; border: string }> = {
  demo: { label: 'Demo', dot: 'bg-warning', text: 'text-warning', border: 'border-warning/30' },
  simulated: { label: 'Simulated', dot: 'bg-warning', text: 'text-warning', border: 'border-warning/30' },
  live: { label: 'Live', dot: 'bg-security-green', text: 'text-security-green', border: 'border-security-green/30' },
  cached: { label: 'Cached', dot: 'bg-primary', text: 'text-primary', border: 'border-primary/30' },
  fallback: { label: 'Fallback', dot: 'bg-critical', text: 'text-critical', border: 'border-critical/30' },
  'api-ready': { label: 'API-Ready', dot: 'bg-muted', text: 'text-muted', border: 'border-muted/30' },
};

export default function SourceStateBadge({ state, size = 'sm', className }: Props) {
  const key = String(state ?? 'simulated').toLowerCase().replace('_', '-') as SourceState;
  const config = CONFIG[key] ?? CONFIG.simulated;

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 rounded border font-medium uppercase tracking-wider',
        size === 'sm' ? 'text-[9px] px-1.5 py-0.5' : 'text-[10px] px-2 py-1',
        config.border,
        config.text,
        className
      )}
      title={`Data source state: ${config.label}`}
      aria-label={`Data source state: ${config.label}`}
    >
      <span className={clsx('w-1.5 h-1.5 rounded-full', config.dot)} aria-hidden="true" />
      {config.label}
    </span>
  );
}
