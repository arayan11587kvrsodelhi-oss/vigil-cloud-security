import { useState, useEffect } from 'react';
import { Menu, X } from 'lucide-react';
import Sidebar from './Sidebar';
import PageHeader from '../shared/PageHeader';
import { Outlet, useLocation } from 'react-router-dom';

// Page title + one-line question each screen answers.
const PAGE_META: Record<string, { title: string; subtitle: string }> = {
  '/dashboard': { title: 'Command Center', subtitle: 'Security posture overview across assets, vulnerabilities, exposure and active attack paths.' },
  '/vulnerabilities': { title: 'Vulnerabilities', subtitle: 'Tracked CVEs with CVSS, KEV status, affected components and remediation state.' },
  '/attack-paths': { title: 'Attack Paths', subtitle: 'Chained weaknesses that connect internet exposure to high-value data.' },
  '/repositories': { title: 'Repositories', subtitle: 'Supply-chain posture, dependency findings, secrets and CI/CD security gates.' },
  '/containers': { title: 'Containers', subtitle: 'Runtime inventory with privilege, exposed ports and vulnerability signals.' },
  '/secrets': { title: 'Secrets Detection', subtitle: 'Detected credentials with exposure and rotation lifecycle state.' },
  '/scans': { title: 'Scans', subtitle: 'Scan operations with status, timing, findings and failure detail.' },
  '/ai-analyst': { title: 'AI Security Analyst', subtitle: 'Structured analysis of VIGIL telemetry: finding, evidence, risk, impact, action.' },
  '/settings': { title: 'Settings', subtitle: 'Data sources, integrations and demonstration-build transparency.' },
};

export default function AppLayout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const meta = PAGE_META[location.pathname] ?? PAGE_META['/dashboard'];

  return (
    <div className="flex h-screen bg-obsidian bg-aurora overflow-hidden">
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex">
        <Sidebar />
      </div>

      {/* Mobile sidebar overlay */}
      {mobileMenuOpen && (
        <>
          <div className="fixed inset-0 bg-black/60 backdrop-blur-xs z-40 lg:hidden" onClick={() => setMobileMenuOpen(false)} />
          <div className="fixed inset-y-0 left-0 z-50 lg:hidden animate-fade-in-up flex">
            <Sidebar />
            <button
              onClick={() => setMobileMenuOpen(false)}
              className="p-2 text-muted hover:text-text self-start mt-3 ml-2 bg-surface/90 rounded-md border border-border"
              aria-label="Close menu"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </>
      )}

      {/* Main content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Top bar (mobile) */}
        <header className="lg:hidden flex items-center gap-3 px-4 h-12 border-b border-border bg-surface">
          <button onClick={() => setMobileMenuOpen(true)} className="text-muted hover:text-text" aria-label="Open navigation menu">
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-primary/10 border border-primary/30 flex items-center justify-center">
              <span className="text-[10px] font-bold text-white">V</span>
            </div>
            <span className="text-sm font-semibold text-gradient-brand">VIGIL</span>
          </div>
          <span className="text-xs text-muted ml-auto">Cloud Security Intelligence</span>
        </header>

        {/* Page content */}
        <div className="flex-1 overflow-y-auto">
          <div className="px-4 py-5 lg:px-8 lg:py-8 max-w-[1600px] mx-auto w-full">
            <PageHeader title={meta.title} subtitle={meta.subtitle} />
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
}