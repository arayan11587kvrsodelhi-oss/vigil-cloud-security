import { X } from 'lucide-react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

interface Props {
  title: string;
  children: React.ReactNode;
  onClose?: () => void;
  className?: string;
}

export default function DetailPanel({ title, children, onClose, className }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className={clsx('bg-elevated border border-border rounded-lg overflow-hidden', className)}
    >
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <h3 className="text-sm font-semibold text-text">{title}</h3>
        {onClose && (
          <button onClick={onClose} className="text-muted hover:text-text transition-colors">
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
      <div className="p-4 overflow-y-auto max-h-[60vh]">
        {children}
      </div>
    </motion.div>
  );
}