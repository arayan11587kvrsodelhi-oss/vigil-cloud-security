import { Info } from 'lucide-react';
import { useState } from 'react';

interface Props {
  /** Text shown inside the tooltip. Keep it factual — no invented claims. */
  text: string;
  /** Accessible label for the trigger button. */
  label?: string;
  className?: string;
}

/**
 * Small info icon that reveals an explanatory tooltip on hover and focus.
 * Keyboard-accessible and screen-reader labelled.
 */
export default function InfoTip({ text, label = 'More information', className }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <span className={`relative inline-flex ${className ?? ''}`}>
      <button
        type="button"
        aria-label={label}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onClick={(e) => {
          e.stopPropagation();
          setOpen((v) => !v);
        }}
        className="inline-flex items-center justify-center text-muted hover:text-text-secondary focus:text-text-secondary focus:outline-none focus-visible:ring-1 focus-visible:ring-primary/60 rounded transition-colors"
      >
        <Info className="w-3 h-3" aria-hidden="true" />
      </button>
      {open && (
        <span
          role="tooltip"
          className="absolute z-30 left-1/2 -translate-x-1/2 bottom-full mb-2 w-60 text-[10px] leading-relaxed font-normal text-text-secondary bg-elevated border-border rounded-lg px-3 py-2 shadow-panel"
        >
          {text}
        </span>
      )}
    </span>
  );
}
