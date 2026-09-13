export interface DashboardSummary {
  total_assets: number;
  publicly_exposed: number;
  total_vulnerabilities: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  active_attack_paths: number;
  containers: number;
  secrets_detected: number;
  iam_roles: number;
  databases: number;
  repositories: number;
  recent_findings: Finding[];
  risk_categories: RiskCategory[];
  system_health: SystemHealth;
  attack_surface: AttackSurface;
}

export interface Finding {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  source: string;
  asset: string;
  discovered_at: string;
  status: string;
}

export interface RiskCategory {
  category: string;
  score: number;
  status: 'good' | 'needs_attention' | 'at_risk';
}

export interface SystemHealth {
  status: 'synced' | 'live' | 'stale';
  last_sync: string;
  scanners_active: number;
  queued_scans: number;
  uptime: string;
}

export interface AttackSurface {
  total_exposed: number;
  api_endpoints: number;
  web_applications: number;
  open_ports: number;
  dns_records: number;
  cloud_instances: number;
}

export interface SecurityScore {
  overall_score: number;
  asset_coverage: number;
  vulnerability_score: number;
  exposure_score: number;
  iam_score: number;
  secret_score: number;
  trend: { date: string; score: number }[];
}

export interface Vulnerability {
  id: string;
  cve_id: string;
  title: string;
  description: string;
  cvss_score: number;
  cvss_vector: string;
  severity: string;
  cisa_kev: boolean;
  exploit_available: boolean;
  affected_component: string;
  fixed_version: string;
  status: string;
  asset_id: string;
  asset_name: string;
  discovered_at: string;
  updated_at: string;
}

export interface Asset {
  id: string;
  name: string;
  asset_type: string;
  provider: string;
  region: string;
  ip_address: string;
  domain: string;
  publicly_exposed: boolean;
  criticality: number;
  tags: string[];
  discovered_at: string;
  last_seen_at: string;
  is_active: boolean;
  vulnerability_count: number;
  open_findings: number;
}

export interface AttackPath {
  id: string;
  name: string;
  description: string;
  risk_score: number;
  risk_level: string;
  steps: AttackPathStep[];
  blast_radius: string[];
  remediation: string[];
  is_active: boolean;
  discovered_at: string;
  asset_id: string;
  vulnerability_id: string | null;
}

export interface AttackPathStep {
  node: string;
  type: string;
  risk: string;
  detail: string;
}

export interface Repository {
  id: string;
  name: string;
  url: string;
  language: string;
  default_branch: string;
  security_score: number;
  total_findings: number;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
  dependencies: number;
  secrets_detected: number;
  last_scan: string;
  last_commit: string;
  ci_cd_pipeline: string;
}

export interface Container {
  id: string;
  name: string;
  image: string;
  status: string;
  privileges: string;
  exposed_ports: number[];
  vulnerabilities: number;
  asset_id: string;
}

export interface Secret {
  id: string;
  name: string;
  type: string;
  severity: string;
  location: string;
  exposed: boolean;
  rotated: boolean;
  discovered_at: string;
}

export interface ScanResult {
  id: string;
  scan_type: string;
  status: string;
  total_findings: number;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
  target: string;
  started_at: string;
  completed_at: string | null;
}

export interface AIResponse {
  summary: string;
  risk_assessment: string;
  recommended_actions: string[];
  threat_context: string;
}