import { RefreshCw } from 'lucide-react';
import clsx from 'clsx';

interface Props {
  status: 'synced' | 'live' | 'stale';
  lastSync?: string;
  className?: string;
}

export default function SyncIndicator({ status, lastSync, className }: Props) {
  const config = {
    synced: { label: 'Synced', dot: 'bg-security-green' },
    live: { label: 'Live', dot: 'bg-primary' },
    stale: { label: 'Stale', dot: 'bg-critical' },
  } as const;

  // Safe fallback: an unexpected status value must never crash the dashboard.
  const { label, dot } = config[status as keyof typeof config] ?? {
    label: String(status ?? 'Unknown'),
    dot: 'bg-muted',
  };

  return (
    <div className={clsx('flex items-center gap-2 text-xs text-text-secondary', className)}>
      <span className={`w-2 h-2 rounded-full ${dot}`} />
      <span>{label}</span>
      {lastSync && (
        <>
          <RefreshCw className="w-3 h-3" />
          <span>{lastSync}</span>
        </>
      )}
    </div>
  );
}