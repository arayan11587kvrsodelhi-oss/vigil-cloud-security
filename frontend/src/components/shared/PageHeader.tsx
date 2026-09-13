import type { ReactNode } from 'react';
import SourceStateBadge from './SourceStateBadge';

interface Props {
  /** Page title, e.g. "Command Center". */
  title: string;
  /** One-line description of what the page answers. */
  subtitle?: string;
  /** Optional right-aligned slot for actions or a data-source badge. */
  actions?: ReactNode;
  /** Optional small metadata (e.g. "Last updated 09:00"). */
  meta?: string;
}

/**
 * Consistent page header used across every route: eyebrow + title + subtitle on
 * the left, actions/source state on the right.
 */
export default function PageHeader({ title, subtitle, actions, meta }: Props) {
  return (
    <header className="flex flex-wrap items-start justify-between gap-4 mb-6 pb-5 border-b border-border">
      <div className="min-w-0">
        <div className="eyebrow mb-1.5">VIGIL</div>
        <h1 className="text-xl lg:text-2xl font-semibold text-text tracking-tight leading-tight">{title}</h1>
        {subtitle && <p className="mt-1 text-xs text-text-secondary max-w-2xl">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-3">
        {meta && <span className="text-[10px] text-muted hidden sm:inline">{meta}</span>}
        {actions ?? <SourceStateBadge state="simulated" />}
      </div>
    </header>
  );
}
