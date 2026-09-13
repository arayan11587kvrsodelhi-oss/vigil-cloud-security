import { useState, useEffect } from 'react';
import { getSecrets } from '../lib/api';
import { Key, AlertTriangle, CheckCircle, RotateCcw, ShieldCheck } from 'lucide-react';
import Card from '../components/shared/Card';
import SeverityBadge from '../components/shared/SeverityBadge';
import DataState from '../components/shared/DataState';
import SourceStateBadge from '../components/shared/SourceStateBadge';
import InfoTip from '../components/shared/InfoTip';

/** Small visual separator for metadata rows. */
function Dot() {
  return <span aria-hidden="true">·</span>;
}

/** Format a secret type enum (snake_case) for display. */
function formatType(type?: string) {
  return String(type ?? '').split('_').join(' ');
}

/**
 * Security-state pill for a single secret. The three states mirror the backend
 * lifecycle and never overstate the remediation state:
 *   EXPOSED + ROTATION REQUIRED -> still a live risk
 *   EXPOSED + ROTATED           -> credential rotated, verification pending
 *   NOT EXPOSED                 -> found only in a safe location
 */
function SecretStatePills({ secret }: { secret: any }) {
  const lifecycle = secret.lifecycle ?? {};
  const exposureConfirmed = lifecycle.exposure_confirmed ?? secret.exposed;
  const rotationRequired = lifecycle.rotation_required ?? (secret.exposed && !secret.rotated);

  if (!secret.exposed) {
    return (
      <span className="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-elevated border-border text-text-secondary">
        <ShieldCheck className="w-2.5 h-2.5" aria-hidden="true" /> NOT EXPOSED
      </span>
    );
  }

  return (
    <>
      {exposureConfirmed && (
        <span className="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-critical/10 border-critical/30 text-critical">
          <AlertTriangle className="w-2.5 h-2.5" aria-hidden="true" /> EXPOSED
        </span>
      )}
      {rotationRequired ? (
        <span className="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-warning/10 border-warning/30 text-warning">
          <RotateCcw className="w-2.5 h-2.5" aria-hidden="true" /> ROTATION REQUIRED
        </span>
      ) : (
        <span
          className="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-success/10 border-success/30 text-success"
          title="Rotation completed in the demo dataset; verification has not been performed."
        >
          <CheckCircle className="w-2.5 h-2.5" aria-hidden="true" /> ROTATED
        </span>
      )}
    </>
  );
}

export default function SecretsPage() {
  const [secrets, setSecrets] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'rotation_required' | 'exposed' | 'not_exposed'>('all');

  const load = () => {
    setLoading(true);
    setError(null);
    getSecrets()
      .then(setSecrets)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const items: any[] = secrets?.items ?? [];
  const rotationRequired = items.filter(
    (s) => s.lifecycle?.rotation_required ?? (s.exposed && !s.rotated)
  ).length;

  const filtered = items.filter((s) => {
    if (filter === 'rotation_required') return s.lifecycle?.rotation_required ?? (s.exposed && !s.rotated);
    if (filter === 'exposed') return s.exposed;
    if (filter === 'not_exposed') return !s.exposed;
    return true;
  });

  const exposureRate = secrets?.total ? Math.round((secrets.exposed / secrets.total) * 100) : 0;

  const stats = [
    { key: 'all', label: 'Total Secrets', value: secrets?.total ?? 0, color: 'text-text' },
    { key: 'exposed', label: 'Exposed', value: secrets?.exposed ?? 0, color: 'text-critical' },
    { key: 'rotation_required', label: 'Rotation Required', value: rotationRequired, color: 'text-warning' },
    { key: 'not_exposed', label: 'Not Exposed', value: secrets?.not_exposed ?? 0, color: 'text-security-green' },
  ];

  return (
    <DataState loading={loading} error={error} onRetry={load}>
      <div className="space-y-4">
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-2 text-xs text-text-secondary">
            <span>Exposure rate</span>
            <span className="text-warning font-semibold">{exposureRate}%</span>
            <InfoTip
              label="About exposure rate"
              text="Percentage of detected secrets whose value was found outside a managed secret store. Simulated demo data - not from a live secret scanner."
            />
          </div>
          <SourceStateBadge state={secrets?.source_state} size="md" />
        </div>

        {/* Summary cards double as filters for the list below. */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {stats.map((s) => (
            <button
              key={s.key}
              type="button"
              onClick={() => setFilter(s.key as typeof filter)}
              aria-pressed={filter === s.key}
              className={`text-left bg-surface border rounded-lg p-3 transition-colors focus:outline-none focus-visible:ring-1 focus-visible:ring-primary/60 ${
                filter === s.key ? 'border-primary/40' : 'border-border hover:border-primary/20'
              }`}
            >
              <div className="text-xs text-text-secondary">{s.label}</div>
              <div className={`text-xl font-bold ${s.color}`}>{s.value}</div>
            </button>
          ))}
        </div>

        <Card padding="none">
          <div className="px-4 py-3 border-b border-border flex items-center justify-between">
            <div className="eyebrow tracking-wider">
              Detected Secrets
              <span className="text-muted font-normal normal-case tracking-normal"> - {filtered.length} shown</span>
            </div>
            <span className="text-[10px] text-muted">Values masked</span>
          </div>
          <div className="divide-y divide-border/50">
            {filtered.map((s: any) => (
              <div
                key={s.id}
                className="flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 hover:bg-elevated/50 transition-colors"
              >
                <div className="w-8 h-8 rounded bg-elevated border-border flex items-center justify-center flex-shrink-0">
                  <Key className={`w-4 h-4 ${s.exposed ? 'text-critical' : 'text-muted'}`} aria-hidden="true" />
                </div>
                <div className="flex-1 min-w-[220px]">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-medium text-text font-mono">{s.name}</span>
                    <SeverityBadge severity={s.severity} size="sm" />
                    {s.provider && <span className="text-[10px] text-muted">{s.provider}</span>}
                  </div>
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-0.5 mt-0.5 text-[10px] text-text-secondary">
                    <span>{formatType(s.type)}</span>
                    <Dot />
                    <span className="font-mono text-muted" title="Source file">
                      {s.source_file ?? s.location}
                    </span>
                    <Dot />
                    <span className="font-mono text-muted/80">[{s.value ?? 'Protected Secret'}]</span>
                    <Dot />
                    <span>
                      Discovered: {s.discovered_at ? new Date(s.discovered_at).toLocaleDateString() : '-'}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 flex-wrap">
                  <SecretStatePills secret={s} />
                </div>
              </div>
            ))}
            {filtered.length === 0 && (
              <div className="px-4 py-10 text-center text-xs text-muted">No secrets match the current filter.</div>
            )}
          </div>
        </Card>

        <div className="text-[10px] text-muted leading-relaxed">
          Secret values are never displayed - only a masked placeholder. Rotation states are simulated demo
          data; this build performs no live secret scanning and does not verify a rotation remotely.
        </div>
      </div>
    </DataState>
  );
}
