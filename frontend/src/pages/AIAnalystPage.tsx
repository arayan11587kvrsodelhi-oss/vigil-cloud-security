import { useState, useEffect } from 'react';
import { aiAnalyze, aiExplainVulnerability, aiExplainAttackPath } from '../lib/api';
import { Shield, AlertTriangle, CheckCircle, Lightbulb, Search, Target } from 'lucide-react';
import { motion } from 'framer-motion';
import Card from '../components/shared/Card';
import DataState from '../components/shared/DataState';
import SourceStateBadge from '../components/shared/SourceStateBadge';

const ANALYSIS_CONTEXTS = [
  { id: 'general', label: 'Security Posture', icon: Shield },
  { id: 'vuln-CVE-2021-44228', label: 'Critical CVEs', icon: AlertTriangle },
  { id: 'path-path-001', label: 'Attack Paths', icon: Lightbulb },
];

/** Render analyst output as a repeated Finding -> Evidence -> Risk -> Impact -> Action block. */
function AnalysisBlock({ analysis }: { analysis: any }) {
  const finding = analysis.finding ?? analysis.summary ?? analysis.analysis;
  const evidence: string[] = analysis.evidence ?? [];
  const risk = analysis.risk ?? analysis.risk_assessment;
  const impact = analysis.impact;
  const actions: string[] = analysis.recommended_actions ?? analysis.remediation ?? [];
  const threatContext = analysis.threat_context ?? analysis.context;

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
      {/* Finding */}
      <Card>
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary/10 border-primary/30 flex items-center justify-center">
              <Search className="w-4 h-4 text-primary" aria-hidden="true" />
            </div>
            <div>
              <div className="text-sm font-semibold text-text">Finding</div>
              <div className="text-[10px] text-muted">{analysis.model ?? 'Demo Analyst (static)'}</div>
            </div>
          </div>
          <SourceStateBadge state={analysis.source_state} />
        </div>
        <div className="text-xs text-text leading-relaxed whitespace-pre-wrap">{finding}</div>
      </Card>

      {/* Evidence */}
      {evidence.length > 0 && (
        <Card>
          <div className="flex items-center gap-2 mb-3">
            <Target className="w-4 h-4 text-primary" aria-hidden="true" />
            <span className="eyebrow tracking-wider">Evidence</span>
          </div>
          <ul className="space-y-1.5">
            {evidence.map((e, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs text-text-secondary">
                <span className="text-primary mt-0.5" aria-hidden="true">
                  {'>'}
                </span>
                <span>{e}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Risk + Impact */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-4 h-4 text-warning" aria-hidden="true" />
            <span className="eyebrow tracking-wider">Risk</span>
          </div>
          <div className="text-xs text-text leading-relaxed whitespace-pre-wrap">{risk}</div>
        </Card>

        {impact && (
          <Card>
            <div className="flex items-center gap-2 mb-3">
              <Shield className="w-4 h-4 text-critical" aria-hidden="true" />
              <span className="eyebrow tracking-wider">Impact</span>
            </div>
            <div className="text-xs text-text leading-relaxed whitespace-pre-wrap">{impact}</div>
          </Card>
        )}
      </div>

      {/* Recommended actions */}
      {actions.length > 0 && (
        <Card>
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb className="w-4 h-4 text-primary" aria-hidden="true" />
            <span className="eyebrow tracking-wider">Recommended Actions</span>
          </div>
          <div className="space-y-2">
            {actions.map((action, idx) => (
              <div key={idx} className="flex items-start gap-2 p-2 rounded bg-elevated border-border">
                <CheckCircle className="w-3 h-3 text-success mt-0.5 flex-shrink-0" aria-hidden="true" />
                <span className="text-xs text-text">{action}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Threat context (clearly labelled simulated) */}
      {threatContext && (
        <Card>
          <div className="flex items-center gap-2 mb-3">
            <Shield className="w-4 h-4 text-warning" aria-hidden="true" />
            <span className="eyebrow tracking-wider">
              Demo Threat Context
            </span>
            <SourceStateBadge state="simulated" />
          </div>
          <div className="text-xs text-text-secondary leading-relaxed whitespace-pre-wrap">{threatContext}</div>
        </Card>
      )}
    </motion.div>
  );
}

export default function AIAnalystPage() {
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [context, setContext] = useState<string>('general');

  const handleAnalyze = async (ctx: string) => {
    setLoading(true);
    setError(null);
    setContext(ctx);
    try {
      let result;
      if (ctx === 'general') {
        result = await aiAnalyze('general');
      } else if (ctx.startsWith('vuln-')) {
        result = await aiExplainVulnerability(ctx.replace('vuln-', ''));
      } else if (ctx.startsWith('path-')) {
        result = await aiExplainAttackPath(ctx);
      } else {
        result = await aiAnalyze(ctx);
      }
      setAnalysis(result);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleAnalyze('general');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          {ANALYSIS_CONTEXTS.map((ctx) => (
            <button
              key={ctx.id}
              onClick={() => handleAnalyze(ctx.id)}
              aria-pressed={context === ctx.id}
              className={`flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-lg border transition-colors ${context === ctx.id
                  ? 'bg-primary/10 border-primary/30 text-primary'
                  : 'bg-surface border-border text-muted hover:text-text hover:border-muted'
                }`}
            >
              <ctx.icon className="w-3 h-3" aria-hidden="true" />
              {ctx.label}
            </button>
          ))}
        </div>
        <span className="text-[10px] text-muted max-w-sm text-right">
          Static, simulated analyst output. No LLM or external intelligence feed is consulted.
        </span>
      </div>

      <DataState loading={loading} error={error}>
        {analysis && <AnalysisBlock analysis={analysis} />}
      </DataState>
    </div>
  );
}
