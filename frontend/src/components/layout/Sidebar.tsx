import { Shield, Crosshair, LayoutDashboard, Bug, GitBranch, Container, Activity, FileSearch, Settings, ChevronLeft, ChevronRight } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { useState } from 'react';
import clsx from 'clsx';

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: 'Command Center', path: '/dashboard' },
  { icon: Bug, label: 'Vulnerabilities', path: '/vulnerabilities' },
  { icon: Crosshair, label: 'Attack Paths', path: '/attack-paths' },
  { icon: GitBranch, label: 'Repositories', path: '/repositories' },
  { icon: Container, label: 'Containers', path: '/containers' },
  { icon: FileSearch, label: 'Secrets', path: '/secrets' },
  { icon: Activity, label: 'Scans', path: '/scans' },
  { icon: Shield, label: 'AI Analyst', path: '/ai-analyst' },
];

// Active nav item: subtle pink -> purple wash with a pink left rule.
const ACTIVE_CLASS =
  'bg-gradient-to-r from-[rgba(255,45,170,0.16)] to-[rgba(155,92,255,0.08)] text-pink-electric border-l-pink';
const INACTIVE_CLASS =
  'text-muted hover:text-text hover:bg-[rgba(255,45,170,0.05)] border-l-transparent';

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={clsx(
        'relative flex-shrink-0 border-r border-border bg-surface transition-all duration-300 flex-col h-full',
        collapsed ? 'w-16' : 'w-56'
      )}
    >
      {/* Logo */}
      <div className={clsx('flex items-center gap-3 px-3 h-14 border-b border-border', collapsed && 'justify-center px-0')}>
        <div className="w-8 h-8 rounded-lg bg-brand-gradient flex items-center justify-center flex-shrink-0">
          <Shield className="w-4 h-4 text-white" aria-hidden="true" />
        </div>
        {!collapsed && (
          <div>
            <div className="text-sm font-semibold tracking-wide text-gradient-brand">VIGIL</div>
            <div className="text-[10px] font-medium text-muted leading-tight">Cloud Security Intelligence</div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3 px-2.5 space-y-0.5 overflow-y-auto">
        {!collapsed && <div className="eyebrow px-2.5 pb-2">Discover</div>}
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            title={collapsed ? item.label : undefined}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-2.5 py-2 rounded-md text-[13px] font-medium transition-colors duration-150 border-l-2',
                collapsed && 'justify-center px-0',
                isActive ? ACTIVE_CLASS : INACTIVE_CLASS
              )
            }
          >
            <item.icon className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
            {!collapsed && <span className="truncate">{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Settings */}
      <div className="px-2.5 pb-3 pt-3 border-t border-border">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            clsx(
              'flex items-center gap-3 px-2.5 py-2 rounded-md text-[13px] font-medium transition-colors duration-150 border-l-2',
              collapsed && 'justify-center px-0',
              isActive ? ACTIVE_CLASS : INACTIVE_CLASS
            )
          }
        >
          <Settings className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
          {!collapsed && <span>Settings</span>}
        </NavLink>
      </div>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        className="absolute -right-3 top-14 w-6 h-6 rounded-full bg-elevated border-border flex items-center justify-center text-muted hover:text-text hover:border-border-strong transition-colors z-10"
      >
        {collapsed ? <ChevronRight className="w-3 h-3" /> : <ChevronLeft className="w-3 h-3" />}
      </button>
    </aside>
  );
}
