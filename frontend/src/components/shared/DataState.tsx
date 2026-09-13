import { AlertTriangle, RefreshCw, FolderSearch } from 'lucide-react';

interface Props {
  loading?: boolean;
  error?: string | null;
  empty?: boolean;
  emptyMessage?: string;
  onRetry?: () => void;
  children: React.ReactNode;
}

export default function DataState({
  loading,
  error,
  empty = false,
  emptyMessage = 'No telemetry data available.',
  onRetry,
  children,
}: Props) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-16" role="status" aria-live="polite">
        <div className="flex flex-col items-center gap-3 text-text-secondary">
          <div className="w-7 h-7 border-2 border-primary/20 border-t-primary rounded-full animate-spin" />
          <span className="text-xs font-mono tracking-wide text-muted">SYNCHRONIZING TELEMETRY...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12" role="alert">
        <div className="flex flex-col items-center gap-3 max-w-md text-center p-6 rounded-card bg-critical/5 border border-critical/20">
          <AlertTriangle className="w-6 h-6 text-critical" />
          <div className="text-xs font-semibold text-critical uppercase tracking-wider">Telemetry Ingestion Error</div>
          <span className="text-xs text-text-secondary">{error}</span>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-2 inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-primary bg-primary/10 border border-primary/30 rounded-lg hover:bg-primary/20 transition-colors"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Retry Telemetry Sync</span>
            </button>
          )}
        </div>
      </div>
    );
  }

  if (empty) {
    return (
      <div className="flex items-center justify-center py-14">
        <div className="flex flex-col items-center gap-2 text-center p-6 text-muted">
          <FolderSearch className="w-8 h-8 text-muted/60 mb-1" />
          <span className="text-xs font-medium text-text-secondary">{emptyMessage}</span>
          <span className="text-[11px] text-muted">No security events match the current filter parameters.</span>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}