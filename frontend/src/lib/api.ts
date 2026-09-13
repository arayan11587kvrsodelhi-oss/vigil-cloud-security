const API_BASE = 'https://YOUR-VIGIL-BACKEND.onrender.com/api/v1';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

// Dashboard
export const getDashboardSummary = () => fetchJSON<any>('/dashboard/summary');
export const getSecurityScore = () => fetchJSON<any>('/dashboard/security-score');

// Vulnerabilities
export const getVulnerabilities = (params?: { severity?: string; status?: string; search?: string; page?: number; page_size?: number }) => {
  const qs = new URLSearchParams();
  if (params?.severity) qs.set('severity', params.severity);
  if (params?.status) qs.set('status', params.status);
  if (params?.search) qs.set('search', params.search);
  if (params?.page) qs.set('page', String(params.page));
  if (params?.page_size) qs.set('page_size', String(params.page_size));
  return fetchJSON<any>(`/vulnerabilities/?${qs.toString()}`);
};
export const getVulnerabilityStats = () => fetchJSON<any>('/vulnerabilities/stats/overview');

// Assets
export const getAssets = (params?: { asset_type?: string; search?: string; page?: number; page_size?: number }) => {
  const qs = new URLSearchParams();
  if (params?.asset_type) qs.set('asset_type', params.asset_type);
  if (params?.search) qs.set('search', params.search);
  if (params?.page) qs.set('page', String(params.page));
  if (params?.page_size) qs.set('page_size', String(params.page_size));
  return fetchJSON<any>(`/assets/?${qs.toString()}`);
};
export const getAssetTypeSummary = () => fetchJSON<any>('/assets/types/summary');

// Attack Paths
export const getAttackPaths = () => fetchJSON<any>('/attack-paths/');
export const getAttackPathStats = () => fetchJSON<any>('/attack-paths/stats/overview');

// DevSecOps
export const getRepositories = () => fetchJSON<any>('/devsecops/repositories');
export const getRepositoryDependencies = (repoId: string) => fetchJSON<any>(`/devsecops/repositories/${repoId}/dependencies`);
export const getRepositorySecrets = (repoId: string) => fetchJSON<any>(`/devsecops/repositories/${repoId}/secrets`);
export const getRepositorySBOM = (repoId: string) => fetchJSON<any>(`/devsecops/repositories/${repoId}/sbom`);
export const getContainers = () => fetchJSON<any>('/devsecops/containers');
export const getCICD = () => fetchJSON<any>('/devsecops/ci-cd');

// Secrets
export const getSecrets = () => fetchJSON<any>('/secrets/');

// Scans
export const getScans = () => fetchJSON<any>('/scans/');
export const triggerScan = (scanType: string, target: string) => fetchJSON<any>('/scans/trigger', {
  method: 'POST',
  body: JSON.stringify({ scan_type: scanType, target }),
});

// AI Analyst
export const aiAnalyze = (context?: string) => fetchJSON<any>('/ai/analyze', {
  method: 'POST',
  body: JSON.stringify({ context: context || 'general' }),
});
export const aiExplainVulnerability = (cveId: string) => fetchJSON<any>('/ai/explain-vulnerability', {
  method: 'POST',
  body: JSON.stringify({ cve_id: cveId }),
});
export const aiExplainAttackPath = (pathId: string) => fetchJSON<any>('/ai/explain-attack-path', {
  method: 'POST',
  body: JSON.stringify({ path_id: pathId }),
});