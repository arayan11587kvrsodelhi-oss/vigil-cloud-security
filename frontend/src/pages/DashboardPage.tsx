import { useState, useEffect } from 'react';
import { getDashboardSummary, getSecurityScore } from '../lib/api';
import { Shield, Globe, Activity, Lock, Server, ChevronRight, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import SecurityScoreGauge from '../components/shared/SecurityScoreGauge';
import StatCard from '../components/shared/StatCard';
import SeverityBadge from '../components/shared/SeverityBadge';
import Card from '../components/shared/Card';
import DataState from '../components/shared/DataState';
import SyncIndicator from '../components/shared/SyncIndicator';
import SourceStateBadge from '../components/shared/SourceStateBadge';
import InfoTip from '../components/shared/InfoTip';
import { AreaChart, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, CartesianGrid } from 'recharts';

export default function DashboardPage() {
  const [summary, setSummary] = useState<any>(null);
  const [score, setScore] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getDashboardSummary(), getSecurityScore()])
      .then(([s, sc]) => {
        setSummary(s);
        setScore(sc);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <DataState loading={loading} error={error}>
      {summary && score && (
        <div className="space-y-6">
          {/* Top row: Security Score + Live Status */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
            <Card className="lg:col-span-1 flex flex-col items-center justify-center">
              <div className="w-full flex items-center justify-between mb-2">
                <span className="flex items-center gap-1.5 eyebrow">
                  Security Score
                  <InfoTip
                    label="How this score is calculated"
                    text="Demo composite of five sub-scores: asset coverage, vulnerability management, exposure, IAM and secret posture. A demonstration value, not a validated risk model."
                  />
                </span>
                <SourceStateBadge state={score.source_state} />
              </div>
              <SecurityScoreGauge score={score.overall_score} size="md" />
              <div className="mt-3">
                <SyncIndicator
                  status={summary.system_health.status}
                  lastSync={new Date(summary.system_health.last_sync).toLocaleTimeString()}
                />
              </div>
              <div className="mt-4 w-full flex overflow-hidden rounded-md border-border divide-x divide-border">
                {[
                  { label: 'Assets', value: score.asset_coverage },
                  { label: 'Vulns', value: score.vulnerability_score },
                  { label: 'Exposure', value: score.exposure_score },
                  { label: 'IAM', value: score.iam_score },
                  { label: 'Secrets', value: score.secret_score },
                ].map((s) => (
                  <div key={s.label} className="flex-1 text-center py-2">
                    <div className="text-sm font-semibold tabular-nums text-text">{Math.round(s.value)}</div>
                    <div className="text-[9px] text-muted">{s.label}</div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Score Trend */}
            <Card className="lg:col-span-3">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-1.5">
                  <span className="eyebrow tracking-wider">Security Score Trend</span>
                  <InfoTip
                    label="About the score trend"
                    text="Demo score series computed from the simulated fixtures. Not a live measurement and not a validated risk model."
                  />
                </div>
                <div className="flex items-center gap-4 text-xs text-text-secondary">
                  <span className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-primary" aria-hidden="true" />
                    Security score (last 15 days)
                  </span>
                </div>
              </div>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={score.trend} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
                    <defs>
                      <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#FF2DAA" stopOpacity={0.22} />
                        <stop offset="95%" stopColor="#9B5CFF" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis
                      dataKey="date"
                      tick={{ fill: '#8E8298', fontSize: 10 }}
                      tickFormatter={(d: string) => (d ? d.slice(5) : '')}
                      axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
                      tickLine={false}
                      minTickGap={24}
                    />
                    <YAxis
                      domain={[0, 100]}
                      tick={{ fill: '#8E8298', fontSize: 10 }}
                      axisLine={false}
                      tickLine={false}
                      width={40}
                    />
                    <Tooltip
                      cursor={{ stroke: 'rgba(255,79,216,0.3)', strokeWidth: 1 }}
                      contentStyle={{ background: '#160D24', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '10px', color: '#F8F3FA', fontSize: 12, boxShadow: '0 8px 28px rgba(8,5,13,0.6)' }}
                      labelFormatter={(d: string) => (d ? new Date(d).toLocaleDateString() : '')}
                      formatter={(value: number) => [`${value.toFixed(1)}`, 'Score']}
                    />
                    <Area type="monotone" dataKey="score" stroke="#FF4FD8" strokeWidth={2} fill="url(#scoreGrad)" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>

          {/* Attack Surface + Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            <StatCard label="Total Assets" value={summary.total_assets} icon={<Server className="w-4 h-4" />} />
            <StatCard label="Publicly Exposed" value={summary.publicly_exposed} icon={<Globe className="w-4 h-4" />} trend="up" color="text-warning" />
            <StatCard label="Vulnerabilities" value={summary.total_vulnerabilities} icon={<Shield className="w-4 h-4" />} />
            <StatCard label="Critical" value={summary.critical} icon={<AlertTriangle className="w-4 h-4" />} trend="up" color="text-critical" />
            <StatCard label="Attack Paths" value={summary.active_attack_paths} icon={<Activity className="w-4 h-4" />} trend="down" color="text-critical" />
            <StatCard label="Secrets" value={summary.secrets_detected} icon={<Lock className="w-4 h-4" />} trend="up" color="text-warning" />
          </div>

          {/* Security Posture + Recent Findings */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Risk Categories */}
            <Card className="lg:col-span-1">
              <div className="eyebrow tracking-wider mb-3">Security Posture</div>
              <div className="space-y-2">
                {summary.risk_categories.map((cat: any) => (
                  <div key={cat.category} className="flex items-center gap-3 py-1.5">
                    <div className="flex-1 text-xs text-text-secondary">{cat.category}</div>
                    <div className="w-20 h-1.5 bg-obsidian rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${cat.score >= 80 ? 'bg-security-green' : cat.score >= 60 ? 'bg-warning' : 'bg-critical'
                          }`}
                        style={{ width: `${cat.score}%` }}
                      />
                    </div>
                    <div className={`text-xs font-medium w-8 text-right ${cat.score >= 80 ? 'text-security-green' : cat.score >= 60 ? 'text-warning' : 'text-critical'
                      }`}>{cat.score}</div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Attack Surface Details */}
            <Card className="lg:col-span-1">
              <div className="eyebrow tracking-wider mb-3">Attack Surface</div>
              <div className="space-y-3">
                {[
                  { label: 'API Endpoints', value: summary.attack_surface.api_endpoints, color: 'text-primary' },
                  { label: 'Web Applications', value: summary.attack_surface.web_applications, color: 'text-warning' },
                  { label: 'Open Ports', value: summary.attack_surface.open_ports, color: 'text-critical' },
                  { label: 'DNS Records', value: summary.attack_surface.dns_records, color: 'text-text-secondary' },
                  { label: 'Cloud Instances', value: summary.attack_surface.cloud_instances, color: 'text-security-green' },
                ].map((item) => (
                  <div key={item.label} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`w-1.5 h-1.5 rounded-full ${item.color.replace('text-', 'bg-')}`} />
                      <span className="text-xs text-text-secondary">{item.label}</span>
                    </div>
                    <span className={`text-sm font-semibold ${item.color}`}>{item.value}</span>
                  </div>
                ))}
                <div className="pt-2 border-t border-border">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-text">Total Exposed</span>
                    <span className="text-lg font-bold text-critical">{summary.attack_surface.total_exposed}</span>
                  </div>
                </div>
              </div>
            </Card>

            {/* System Health */}
            <Card className="lg:col-span-1">
              <div className="eyebrow tracking-wider mb-3">System Health</div>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-text-secondary">Status</span>
                  <span className={`text-xs font-medium ${summary.system_health.status === 'synced' ? 'text-security-green' :
                      summary.system_health.status === 'live' ? 'text-primary' : 'text-critical'
                    }`}>{summary.system_health.status.toUpperCase()}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-text-secondary">Scanners Active</span>
                  <span className="text-xs font-medium text-text">{summary.system_health.scanners_active}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-text-secondary">Queued Scans</span>
                  <span className="text-xs font-medium text-warning">{summary.system_health.queued_scans}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-text-secondary">Uptime</span>
                  <span className="text-xs font-medium text-text">{summary.system_health.uptime}</span>
                </div>
                <div className="pt-2 border-t border-border">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-text-secondary">Last Sync</span>
                    <span className="text-xs font-medium text-text">{
                      new Date(summary.system_health.last_sync).toLocaleString()
                    }</span>
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Recent Findings */}
          <Card>
            <div className="flex items-center justify-between mb-3">
              <div className="eyebrow tracking-wider">Recent Findings</div>
              <button className="text-xs text-primary hover:text-primary-soft flex items-center gap-1">
                View All <ChevronRight className="w-3 h-3" />
              </button>
            </div>
            <div className="space-y-1">
              {summary.recent_findings.map((finding: any, idx: number) => (
                <motion.div
                  key={finding.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="flex items-start gap-3 px-3 py-2.5 rounded-lg hover:bg-elevated transition-colors group cursor-pointer"
                >
                  <SeverityBadge severity={finding.severity} size="sm" showLabel={false} />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs text-text truncate">{finding.title}</div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[10px] text-muted">{finding.source}</span>
                      <span className="text-[10px] text-muted">•</span>
                      <span className="text-[10px] text-muted">{finding.asset}</span>
                      <span className="text-[10px] text-muted">•</span>
                      <span className="text-[10px] text-muted">{new Date(finding.discovered_at).toLocaleString()}</span>
                    </div>
                  </div>
                  <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${finding.status === 'active' ? 'bg-critical/10 text-critical' :
                      finding.status === 'in_triage' ? 'bg-warning/10 text-warning' :
                        'bg-success/10 text-success'
                    }`}>{finding.status.replace('_', ' ')}</span>
                </motion.div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </DataState>
  );
}