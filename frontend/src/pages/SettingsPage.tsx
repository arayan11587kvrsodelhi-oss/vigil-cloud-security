import { Shield, Bell, Database, Globe, Lock, Key, Webhook, Check } from 'lucide-react';
import Card from '../components/shared/Card';
import SourceStateBadge from '../components/shared/SourceStateBadge';
import InfoTip from '../components/shared/InfoTip';

/**
 * Data/feature status. Each entry states truthfully whether the capability is
 * demo data, an unconnected (but API-ready) integration, or not configured.
 * Nothing here claims a live connection that does not exist.
 */
const SECTIONS = [
  {
    icon: Database,
    title: 'Threat Intelligence Feeds',
    description: 'NVD, CISA KEV and OSV enrichment for vulnerability records',
    state: 'api-ready' as const,
    detail:
      'Vulnerability fixtures ship with fixed KEV and exploit flags. A feed connector can be configured via environment variables; no feed is queried in this build.',
  },
  {
    icon: Key,
    title: 'Cloud Providers',
    description: 'AWS, GCP and Azure asset discovery',
    state: 'simulated' as const,
    detail:
      'Asset inventory is a simulated fixture. No cloud API credentials are configured and no provider is scanned.',
  },
  {
    icon: Globe,
    title: 'Attack Surface Discovery',
    description: 'Domain and IP range monitoring',
    state: 'simulated' as const,
    detail: 'Exposure data is part of the simulator fixtures; no external surface scanning is performed.',
  },
  {
    icon: Bell,
    title: 'Notifications',
    description: 'Slack, PagerDuty and email alert channels',
    state: 'api-ready' as const,
    detail: 'No notification channels are connected in this build.',
  },
  {
    icon: Lock,
    title: 'Authentication',
    description: 'SSO, MFA, API keys and team management',
    state: 'demo' as const,
    detail: 'This is a single-user demonstration build with no authentication layer enabled.',
  },
  {
    icon: Webhook,
    title: 'Webhooks',
    description: 'Event-driven with your toolchain',
    state: 'api-ready' as const,
    detail: 'WebSocket event streaming is wired for the live UI; outbound webhooks are not configured.',
  },
];

export default function SettingsPage() {
  return (
    <div className="space-y-4">
      <Card>
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-3">
            <Shield className="w-5 h-5 text-primary" aria-hidden="true" />
            <div>
              <div className="text-sm font-semibold text-text">VIGIL Configuration</div>
              <div className="text-[10px] text-muted">Version 1.0.0 - Cloud Security Intelligence Platform</div>
            </div>
          </div>
          <SourceStateBadge state="demo" size="md" />
        </div>
        <div className="text-xs text-text-secondary leading-relaxed">
          This is a demonstration build. All security telemetry shown across the product is <strong>simulated</strong>.
          No live AWS/GCP/Azure scanning, GitHub scanning, secret scanning, threat-intelligence ingestion or SIEM
          ingestion is performed. Integrations marked <em>API-Ready</em> are connection points that can be supplied
          via environment variables but are not active here.
        </div>
      </Card>

      {/* Data provenance legend */}
      <Card>
        <div className="flex items-center gap-2 mb-3">
          <span className="eyebrow tracking-wider">Data Source States</span>
          <InfoTip
            label="About source states"
            text="VIGIL labels every dataset with the state that is actually true for it, so simulated telemetry is never mistaken for live production data."
          />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {[
            ['live', 'Retrieved live from a configured source'],
            ['cached', 'Served from a local cache'],
            ['simulated', 'Generated demo telemetry (current default)'],
            ['demo', 'Demonstration build data'],
            ['fallback', 'A fallback path was used'],
            ['api-ready', 'Integration point exists but is not connected'],
          ].map(([state, meaning]) => (
            <div key={state} className="flex items-center gap-2 p-2 rounded border-border bg-surface">
              <SourceStateBadge state={state} />
              <span className="text-[10px] text-text-secondary">{meaning}</span>
            </div>
          ))}
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {SECTIONS.map((section) => (
          <Card key={section.title}>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded bg-elevated border-border flex items-center justify-center flex-shrink-0">
                <section.icon className="w-4 h-4 text-primary" aria-hidden="true" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <div className="text-xs font-semibold text-text">{section.title}</div>
                  <SourceStateBadge state={section.state} />
                </div>
                <div className="text-[10px] text-text-secondary mt-1">{section.description}</div>
                <div className="text-[10px] text-muted mt-2 leading-relaxed">{section.detail}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="flex items-center gap-2 text-[10px] text-muted">
        <Check className="w-3 h-3 text-security-green" aria-hidden="true" />
        No external API keys are stored or transmitted in this demonstration build.
      </div>
    </div>
  );
}
