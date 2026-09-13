import { useState, useEffect } from 'react';
import { getContainers } from '../lib/api';
import { Container, Wifi, AlertTriangle, ShieldAlert, Server } from 'lucide-react';
import Card from '../components/shared/Card';
import DataState from '../components/shared/DataState';
import SourceStateBadge from '../components/shared/SourceStateBadge';
import InfoTip from '../components/shared/InfoTip';

/** Risk band for a container based on the signals present in the data model. */
function containerRisk(c: any) {
  const privileged = c.privileges === 'privileged';
  const exposed = (c.exposed_ports?.length ?? 0) > 0;
  const vulns = c.vulnerabilities ?? 0;

  if (privileged && (exposed || vulns > 5)) return { level: 'critical', score: 90 };
  if (privileged) return { level: 'high', score: 75 };
  if (vulns > 5 || (exposed && vulns > 0)) return { level: 'high', score: 68 };
  if (exposed || vulns > 0) return { level: 'medium', score: 45 };
  return { level: 'low', score: 15 };
}

const RISK_CLASSES: Record<string, string> = {
  critical: 'bg-critical/10 text-critical border-critical/30',
  high: 'bg-warning/10 text-warning border-warning/30',
  medium: 'bg-primary/10 text-primary border-primary/30',
  low: 'bg-success/10 text-success border-success/30',
};

export default function ContainersPage() {
  const [containers, setContainers] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    getContainers()
      .then(setContainers)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const items: any[] = containers?.items ?? [];
  const privileged = items.filter((c) => c.privileges === 'privileged').length;
  const running = items.filter((c) => c.status === 'running').length;
  const totalVulns = items.reduce((a, c) => a + (c.vulnerabilities ?? 0), 0);

  const stats = [
    { label: 'Total Containers', value: containers?.total ?? items.length, color: 'text-text' },
    { label: 'Running', value: running, color: 'text-security-green' },
    { label: 'Privileged', value: privileged, color: 'text-critical' },
    { label: 'Vulnerabilities', value: totalVulns, color: 'text-warning' },
  ];

  return (
    <DataState loading={loading} error={error} onRetry={load}>
      <div className="space-y-4">
        <div className="flex items-center justify-between gap-2">
          <span className="text-xs text-text-secondary uppercase tracking-wider">Container Inventory</span>
          <SourceStateBadge state={containers?.source_state} size="md" />
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {stats.map((s) => (
            <Card key={s.label} padding="sm">
              <div className="text-xs text-text-secondary">{s.label}</div>
              <div className={`text-xl font-bold ${s.color}`}>{s.value}</div>
            </Card>
          ))}
        </div>

        <Card padding="none">
          <div className="overflow-x-auto">
            <table className="vigil-table">
              <thead>
                <tr>
                  <th>Container</th>
                  <th>Image</th>
                  <th>Status</th>
                  <th>Privileges</th>
                  <th>Exposed Ports</th>
                  <th>Vulns</th>
                  <th>
                    <span className="inline-flex items-center gap-1">
                      Risk
                      <InfoTip
                        label="About container risk"
                        text="Demo risk band derived from privileged mode, exposed ports and vulnerability count. Not a runtime container-security verdict."
                      />
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {items.map((c: any) => {
                  const risk = containerRisk(c);
                  return (
                    <tr key={c.id}>
                      <td>
                        <div className="flex items-center gap-2">
                          <div className="w-7 h-7 rounded bg-elevated border-border flex items-center justify-center flex-shrink-0">
                            <Container className="w-3.5 h-3.5 text-primary" aria-hidden="true" />
                          </div>
                          <div>
                            <div className="text-xs font-medium text-text">{c.name}</div>
                            {c.host && (
                              <div className="text-[10px] text-muted flex items-center gap-1">
                                <Server className="w-2.5 h-2.5" aria-hidden="true" />
                                {c.host}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className="text-[10px] text-text-secondary font-mono">{c.image}</span>
                      </td>
                      <td>
                        <span
                          className={`text-[10px] px-1.5 py-0.5 rounded ${c.status === 'running' ? 'bg-success/10 text-success' : 'bg-muted/10 text-muted'
                            }`}
                        >
                          {String(c.status ?? 'unknown').toUpperCase()}
                        </span>
                      </td>
                      <td>
                        {c.privileges === 'privileged' ? (
                          <span className="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-critical/10 text-critical font-medium">
                            <ShieldAlert className="w-2.5 h-2.5" aria-hidden="true" /> PRIVILEGED
                          </span>
                        ) : (
                          <span className="text-[10px] text-text-secondary">Standard</span>
                        )}
                      </td>
                      <td>
                        {c.exposed_ports?.length > 0 ? (
                          <span className="inline-flex items-center gap-1 text-[10px] text-warning font-mono">
                            <Wifi className="w-2.5 h-2.5" aria-hidden="true" />
                            {c.exposed_ports.join(', ')}
                          </span>
                        ) : (
                          <span className="text-[10px] text-muted">None</span>
                        )}
                      </td>
                      <td>
                        <span
                          className={`text-xs font-semibold ${(c.vulnerabilities ?? 0) > 5 ? 'text-warning' : 'text-text-secondary'
                            }`}
                        >
                          {c.vulnerabilities ?? 0}
                        </span>
                      </td>
                      <td>
                        <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded border ${RISK_CLASSES[risk.level]}`}>
                          {risk.level.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <div className="px-4 py-3 border-t border-border flex-wrap items-center justify-between gap-2">
            <span className="text-[10px] text-muted">
              Simulated inventory. Image digests, capabilities and mounted secrets are not part of this dataset and
              are not shown.
            </span>
            {privileged > 0 && (
              <span className="text-[10px] text-critical inline-flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" aria-hidden="true" />
                {privileged} privileged container{privileged === 1 ? '' : 's'} require review
              </span>
            )}
          </div>
        </Card>
      </div>
    </DataState>
  );
}
