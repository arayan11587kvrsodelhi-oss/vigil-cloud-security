interface Props {
  label: string;
  value: string | number;
  unit?: string;
  /**
   * Directional marker only. No numeric delta is rendered because the demo
   * fixtures do not provide week-over-week trend data (avoids fabricated stats).
   */
  trend?: 'up' | 'down' | 'neutral';
  icon?: React.ReactNode;
  color?: string;
  /** Optional short caption shown under the value. */
  hint?: string;
}

export default function StatCard({ label, value, unit, trend, icon, color = 'text-text', hint }: Props) {
  const trendConfig = {
    up: { className: 'text-security-green', glyph: '↑' },
    down: { className: 'text-critical', glyph: '↓' },
    neutral: { className: 'text-muted', glyph: '→' },
  } as const;

  return (
    <div className="bg-surface border-border rounded-card p-4 shadow-card transition-colors duration-200 hover:border-border-strong">
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="eyebrow">{label}</span>
        {icon && <span className="text-muted flex-shrink-0" aria-hidden="true">{icon}</span>}
      </div>
      <div className="flex items-baseline gap-1.5">
        <span className={`text-2xl font-semibold tabular-nums ${color}`}>{value}</span>
        {unit && <span className="text-xs text-muted">{unit}</span>}
        {trend && (
          <span className={`text-xs ${trendConfig[trend].className}`} aria-hidden="true">
            {trendConfig[trend].glyph}
          </span>
        )}
      </div>
      {hint && <div className="mt-1 text-[11px] text-muted">{hint}</div>}
    </div>
  );
}
