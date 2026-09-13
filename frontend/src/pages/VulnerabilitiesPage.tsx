import { useState, useEffect } from 'react';
import { getVulnerabilities, getVulnerabilityStats } from '../lib/api';
import { Search, ShieldAlert } from 'lucide-react';
import SeverityBadge from '../components/shared/SeverityBadge';
import Card from '../components/shared/Card';
import DataState from '../components/shared/DataState';
import SourceStateBadge from '../components/shared/SourceStateBadge';
import InfoTip from '../components/shared/InfoTip';

/** Remediation lifecycle label for a finding status. */
const STATUS_CONFIG: Record<string, { label: string; className: string }> = {
  active: { label: 'Remediation Required', className: 'bg-critical/10 text-critical' },
  in_triage: { label: 'In Triage', className: 'bg-warning/10 text-warning' },
  fixed: { label: 'Resolved', className: 'bg-success/10 text-success' },
};

function StatusPill({ status }: { status?: string }) {
  const key = String(status ?? '').toLowerCase();
  const config = STATUS_CONFIG[key] ?? { label: key || 'Unknown', className: 'bg-muted/10 text-muted' };
  return (
    <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${config.className}`}>{config.label}</span>
  );
}

export default function VulnerabilitiesPage() {
  const [vulns, setVulns] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('');

  const load = () => {
    setLoading(true);
    setError(null);
    Promise.all([getVulnerabilities(), getVulnerabilityStats()])
      .then(([v, s]) => {
        setVulns(v);
        setStats(s);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const filteredVulns = (vulns?.items ?? []).filter((v: any) => {
    if (severityFilter && v.severity !== severityFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      const matchCve = v.cve_id?.toLowerCase().includes(q);
      const matchTitle = v.title?.toLowerCase().includes(q);
      const matchComp = v.affected_component?.toLowerCase().includes(q);
      const matchAsset = v.asset_name?.toLowerCase().includes(q);
      if (!matchCve && !matchTitle && !matchComp && !matchAsset) return false;
    }
    return true;
  });

  return (
    <DataState loading={loading} error={error} onRetry={load}>
      <div className="space-y-4">
        {/* Summary stats (open/unresolved findings only) */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
            {[
              { label: 'Total Tracked', value: stats.total, color: 'text-text' },
              { label: 'Critical (open)', value: stats.critical, color: 'text-critical' },
              { label: 'High (open)', value: stats.high, color: 'text-warning' },
              { label: 'Remediation Req.', value: stats.remediation_required, color: 'text-warning' },
              { label: 'CISA KEV', value: stats.cisa_kev, color: 'text-critical' },
              { label: 'Resolved', value: stats.fixed, color: 'text-success' },
            ].map((s) => (
              <Card key={s.label} padding="sm">
                <div className="text-xs text-text-secondary">{s.label}</div>
                <div className={`text-xl font-bold ${s.color}`}>{s.value ?? 0}</div>
              </Card>
            ))}
          </div>
        )}

        {/* Search + filters + provenance */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex-1 min-w-[200px] max-w-sm relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" aria-hidden="true" />
            <input
              type="text"
              placeholder="Search by CVE, title, component, asset..."
              aria-label="Search vulnerabilities"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-surface border-border rounded-lg pl-9 pr-4 py-2 text-sm text-text placeholder-muted focus:outline-none focus:border-primary/50 transition-colors"
            />
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-2">
              {['', 'critical', 'high', 'medium', 'low'].map((s) => (
                <button
                  key={s || 'all'}
                  onClick={() => setSeverityFilter(s)}
                  aria-pressed={severityFilter === s}
                  className={`px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors capitalize ${severityFilter === s
                      ? 'bg-primary/10 border-primary/30 text-primary'
                      : 'bg-surface border-border text-muted hover:text-text hover:border-muted'
                    }`}
                >
                  {s || 'All'}
                </button>
              ))}
            </div>
            <SourceStateBadge state={vulns?.source_state} size="md" />
          </div>
        </div>

        {/* Vulnerability table */}
        <Card padding="none">
          <div className="overflow-x-auto">
            <table className="vigil-table">
              <thead>
                <tr>
                  <th>
                    CVE / Finding
                  </th>
                  <th>Severity</th>
                  <th>CVSS</th>
                  <th>Component</th>
                  <th>Installed &rarr; Fixed</th>
                  <th>Asset</th>
                  <th>Remediation</th>
                  <th>
                    <span className="inline-flex items-center gap-1">
                      KEV
                      <InfoTip
                        label="About CISA KEV"
                        text="CISA Known Exploited Vulnerabilities flag. In this demo build the flag is fixed per-CVE fixture, not fetched from the CISA catalogue."
                      />
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredVulns.map((v: any) => (
                  <tr key={v.id}>
                    <td className="max-w-xs">
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs font-medium text-text font-mono">{v.cve_id}</span>
                        {v.publicly_exposed && (
                          <span
                            className="text-[9px] px-1 py-0.5 rounded bg-warning/10 text-warning border-warning/30"
                            title="Affected asset is publicly exposed in the demo inventory"
                          >
                            EXPOSED
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-text-secondary truncate" title={v.title}>
                        {v.title}
                      </div>
                    </td>
                    <td>
                      <SeverityBadge severity={v.severity} size="sm" />
                    </td>
                    <td>
                      <span
                        className={`text-xs font-semibold tabular-nums ${v.cvss_score >= 9 ? 'text-critical' : v.cvss_score >= 7 ? 'text-warning' : 'text-text-secondary'
                          }`}
                      >
                        {v.cvss_score?.toFixed(1) ?? '-'}
                      </span>
                    </td>
                    <td>
                      <div className="text-xs text-text font-mono">{v.affected_component}</div>
                      <div className="text-[10px] text-muted">{v.ecosystem}</div>
                    </td>
                    <td>
                      <span className="text-xs text-text-secondary font-mono">
                        {v.installed_version ?? '-'} &rarr; {v.fixed_version ?? '-'}
                      </span>
                    </td>
                    <td>
                      <span className="text-xs text-text-secondary">{v.asset_name}</span>
                    </td>
                    <td>
                      <StatusPill status={v.status} />
                    </td>
                    <td>
                      {v.cisa_kev ? (
                        <span className="inline-flex items-center gap-1 text-[10px] font-medium px-1.5 py-0.5 rounded bg-critical/10 text-critical">
                          <ShieldAlert className="w-2.5 h-2.5" aria-hidden="true" /> KEV
                        </span>
                      ) : (
                        <span className="text-[10px] text-muted">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-4 py-3 text-xs text-muted border-t border-border flex items-center justify-between flex-wrap gap-2">
            <span>
              Showing {filteredVulns.length} of {vulns?.total ?? 0} tracked vulnerabilities
            </span>
            <span className="text-[10px]">
              Simulated dataset - severity derived from CVSS, KEV/exploit flags fixed per CVE.
            </span>
          </div>
        </Card>
      </div>
    </DataState>
  );
}
