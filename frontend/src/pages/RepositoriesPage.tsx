import { useState, useEffect } from 'react';
import { getRepositories, getCICD } from '../lib/api';
import { GitBranch, Shield, CheckCircle, XCircle } from 'lucide-react';
import Card from '../components/shared/Card';
import DataState from '../components/shared/DataState';
import SourceStateBadge from '../components/shared/SourceStateBadge';
import InfoTip from '../components/shared/InfoTip';

/** Colour class for a Security Posture value (0-100, higher is better). */
function postureClasses(score: number) {
  if (score >= 80) return 'text-success';
  if (score >= 60) return 'text-warning';
  return 'text-critical';
}

function postureLabel(score: number) {
  if (score >= 90) return 'Strong';
  if (score >= 80) return 'Good';
  if (score >= 60) return 'Needs attention';
  return 'At risk';
}

export default function RepositoriesPage() {
  const [repos, setRepos] = useState<any>(null);
  const [cicd, setCicd] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    Promise.all([getRepositories(), getCICD()])
      .then(([r, c]) => {
        setRepos(r);
        setCicd(c);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const items: any[] = repos?.items ?? [];

  return (
    <DataState loading={loading} error={error} onRetry={load}>
      <div className="space-y-4">
        {/* CI/CD Pipeline Security */}
        {cicd && cicd.items?.length > 0 && (
          <Card>
            <div className="flex items-center justify-between mb-3">
              <div className="eyebrow tracking-wider">
                CI/CD Security Gates
              </div>
              <SourceStateBadge state={cicd.source_state} />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {cicd.items.map((pipeline: any) => (
                <div key={pipeline.name} className="p-3 rounded-lg border-border bg-surface">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-text">{pipeline.name}</span>
                    {pipeline.status === 'passing' ? (
                      <CheckCircle className="w-4 h-4 text-success" aria-label="Gate passing" />
                    ) : (
                      <XCircle className="w-4 h-4 text-critical" aria-label="Gate failing" />
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-[10px] text-text-secondary">
                    <span className={pipeline.security_gates ? 'text-success' : 'text-critical'}>
                      {pipeline.security_gates ? 'Gates active' : 'No gates'}
                    </span>
                    <span aria-hidden="true">·</span>
                    <span>Last build: {pipeline.last_build ?? pipeline.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Repository list */}
        <Card padding="none">
          <div className="px-4 py-3 border-b border-border flex items-center justify-between">
            <div className="eyebrow tracking-wider">Repositories</div>
            <SourceStateBadge state={repos?.source_state} />
          </div>
          <div className="overflow-x-auto">
            <table className="vigil-table">
              <thead>
                <tr>
                  <th>Repository</th>
                  <th>Dependencies</th>
                  <th>Findings</th>
                  <th>Secrets</th>
                  <th>Last Scan</th>
                  <th>CI/CD Gate</th>
                  <th>
                    <span className="inline-flex items-center gap-1">
                      Security Posture
                      <InfoTip
                        label="About Security Posture"
                        text="Demo score (0-100, higher is better) derived from the finding mix. Not a validated risk model, and not fetched from a live SCM scanner."
                      />
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {items.map((repo: any) => (
                  <tr key={repo.id}>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded bg-elevated border-border flex items-center justify-center flex-shrink-0">
                          <GitBranch className="w-3.5 h-3.5 text-primary" aria-hidden="true" />
                        </div>
                        <div>
                          <div className="text-xs font-medium text-text">{repo.name}</div>
                          <div className="text-[10px] text-muted">{repo.language}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="text-xs text-text-secondary">{repo.dependencies}</span>
                    </td>
                    <td>
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs text-text-secondary">{repo.total_findings}</span>
                        {repo.critical_findings > 0 && (
                          <span className="text-[10px] px-1 py-0.5 rounded bg-critical/10 text-critical">
                            {repo.critical_findings} crit
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className={`text-xs ${repo.secrets_detected > 0 ? 'text-warning' : 'text-text-secondary'}`}>
                        {repo.secrets_detected}
                      </span>
                    </td>
                    <td>
                      <span className="text-[10px] text-text-secondary">
                        {repo.last_scan ? new Date(repo.last_scan).toLocaleDateString() : '-'}
                      </span>
                    </td>
                    <td>
                      {repo.ci_cd_gate === 'passing' ? (
                        <span className="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-success/10 text-success">
                          <CheckCircle className="w-2.5 h-2.5" aria-hidden="true" /> Passing
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-critical/10 text-critical">
                          <XCircle className="w-2.5 h-2.5" aria-hidden="true" /> Failing
                        </span>
                      )}
                    </td>
                    <td>
                      <div className="flex items-center gap-1.5">
                        <Shield className={`w-3 h-3 ${postureClasses(repo.security_score)}`} aria-hidden="true" />
                        <span className={`text-xs font-semibold ${postureClasses(repo.security_score)}`}>
                          {repo.security_score}
                        </span>
                        <span className="text-[10px] text-muted">{postureLabel(repo.security_score)}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </DataState>
  );
}
