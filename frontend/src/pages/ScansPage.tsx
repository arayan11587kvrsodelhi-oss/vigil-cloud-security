import { useState, useEffect } from 'react';
import { getScans, triggerScan } from '../lib/api';
import { Play, Loader, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';
import Card from '../components/shared/Card';
import DataState from '../components/shared/DataState';
import SourceStateBadge from '../components/shared/SourceStateBadge';

/** Status presentation for a scan record. */
const STATUS_CONFIG: Record<string, { label: string; className: string; dot: string }> = {
  completed: { label: 'COMPLETED', className: 'bg-success/10 text-success', dot: 'bg-success' },
  running: { label: 'RUNNING', className: 'bg-primary/10 text-primary', dot: 'bg-primary' },
  queued: { label: 'QUEUED', className: 'bg-warning/10 text-warning', dot: 'bg-warning' },
  failed: { label: 'FAILED', className: 'bg-critical/10 text-critical', dot: 'bg-critical' },
};

function StatusIcon({ status }: { status: string }) {
  if (status === 'completed') return <CheckCircle className="w-4 h-4 text-success" aria-hidden="true" />;
  if (status === 'failed') return <XCircle className="w-4 h-4 text-critical" aria-hidden="true" />;
  return <Loader className="w-3.5 h-3.5 text-primary animate-spin" aria-hidden="true" />;
}

function StatusPill({ status }: { status: string }) {
  const config = STATUS_CONFIG[status] ?? { label: String(status ?? 'UNKNOWN').toUpperCase(), className: 'bg-muted/10 text-muted', dot: 'bg-muted' };
  return (
    <span className={`inline-flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded ${config.className}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} aria-hidden="true" />
      {config.label}
    </span>
  );
}

export default function ScansPage() {
  const [scans, setScans] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [triggering, setTriggering] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [notice, setNotice] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    getScans()
      .then(setScans)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleTriggerScan = async () => {
    setTriggering(true);
    setNotice(null);
    try {
      const result = await triggerScan('dependency', 'all-repositories');
      setNotice(`Scan ${result?.id ?? ''} queued. ${result?.message ?? 'No scanner executed in demo mode.'}`);
      const updated = await getScans();
      setScans(updated);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setTriggering(false);
    }
  };

  const items: any[] = scans?.items ?? [];
  const filtered = statusFilter ? items.filter((s) => s.status === statusFilter) : items;

  const stats = [
    { key: '', label: 'Total', value: scans?.total ?? items.length, color: 'text-text' },
    { key: 'completed', label: 'Completed', value: scans?.completed ?? 0, color: 'text-success' },
    { key: 'running', label: 'Running', value: scans?.running ?? 0, color: 'text-primary' },
    { key: 'queued', label: 'Queued', value: scans?.queued ?? 0, color: 'text-warning' },
    { key: 'failed', label: 'Failed', value: scans?.failed ?? 0, color: 'text-critical' },
  ];

  return (
    <DataState loading={loading} error={error} onRetry={load}>
      <div className="space-y-4">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="eyebrow tracking-wider">Scan Operations</span>
            <SourceStateBadge state={scans?.source_state} size="md" />
          </div>
          <button
            onClick={handleTriggerScan}
            disabled={triggering}
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-brand-gradient text-white rounded-md shadow-card hover:shadow-glow-sm hover:brightness-110 active:brightness-95 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
          >
            {triggering ? <Loader className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3" />}
            {triggering ? 'Queuing...' : 'New Scan'}
          </button>
        </div>

        {notice && (
          <div className="text-[11px] text-warning bg-warning/5 border-warning/20 rounded-lg px-3 py-2 flex items-center gap-2">
            <AlertTriangle className="w-3.5 h-3.5" aria-hidden="true" />
            {notice}
          </div>
        )}

        {/* Status summary doubles as a filter */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {stats.map((s) => (
            <button
              key={s.label}
              type="button"
              onClick={() => setStatusFilter(s.key)}
              aria-pressed={statusFilter === s.key}
              className={`text-left bg-surface border rounded-lg p-3 transition-colors focus:outline-none focus-visible:ring-1 focus-visible:ring-primary/60 ${statusFilter === s.key ? 'border-primary/40' : 'border-border hover:border-primary/20'
                }`}
            >
              <div className="text-xs text-text-secondary">{s.label}</div>
              <div className={`text-xl font-bold ${s.color}`}>{s.value}</div>
            </button>
          ))}
        </div>

        <Card padding="none">
          <div className="divide-y divide-border/50">
            {filtered.map((scan: any) => (
              <div key={scan.id} className="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 hover:bg-elevated/50 transition-colors">
                <div className="w-8 h-8 rounded bg-elevated border-border flex items-center justify-center flex-shrink-0">
                  <StatusIcon status={scan.status} />
                </div>
                <div className="flex-1 min-w-[240px]">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-medium text-text capitalize">{scan.scan_type} Scan</span>
                    <StatusPill status={scan.status} />
                    {scan.status === 'failed' && (
                      <span className="text-[10px] text-critical">Reason: {scan.failure_reason ?? 'unspecified'}</span>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-0.5 mt-0.5 text-[10px] text-text-secondary">
                    <span>Target: {scan.target}</span>
                    {scan.status === 'completed' && (
                      <>
                        <span aria-hidden="true">·</span>
                        <span>{scan.total_findings} findings</span>
                        {scan.critical_findings > 0 && (
                          <>
                            <span aria-hidden="true">·</span>
                            <span className="text-critical">{scan.critical_findings} critical</span>
                          </>
                        )}
                        <span aria-hidden="true">·</span>
                        <span>Duration: {scan.duration_minutes != null ? `${scan.duration_minutes}m` : '-'}</span>
                      </>
                    )}
                    <span aria-hidden="true">·</span>
                    <span className="inline-flex items-center gap-1">
                      <Clock className="w-2.5 h-2.5" aria-hidden="true" />
                      {scan.started_at ? new Date(scan.started_at).toLocaleString() : '-'}
                    </span>
                  </div>
                </div>
                {scan.status === 'completed' && scan.critical_findings > 0 && (
                  <span className="inline-flex items-center gap-1 text-[10px] text-critical">
                    <AlertTriangle className="w-3 h-3" aria-hidden="true" />
                    {scan.critical_findings} critical
                  </span>
                )}
              </div>
            ))}
            {filtered.length === 0 && (
              <div className="px-4 py-10 text-center text-xs text-muted">No scans match the current filter.</div>
            )}
          </div>
        </Card>

        <div className="text-[10px] text-muted leading-relaxed">
          Scan history is simulated demo data. Triggering a scan queues a record only - no scanner executes against
          infrastructure in this build.
        </div>
      </div>
    </DataState>
  );
}
