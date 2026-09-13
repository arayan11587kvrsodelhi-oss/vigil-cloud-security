import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import DashboardPage from './pages/DashboardPage';
import VulnerabilitiesPage from './pages/VulnerabilitiesPage';
import AttackPathsPage from './pages/AttackPathsPage';
import RepositoriesPage from './pages/RepositoriesPage';
import ContainersPage from './pages/ContainersPage';
import SecretsPage from './pages/SecretsPage';
import ScansPage from './pages/ScansPage';
import AIAnalystPage from './pages/AIAnalystPage';
import SettingsPage from './pages/SettingsPage';

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/vulnerabilities" element={<VulnerabilitiesPage />} />
        <Route path="/attack-paths" element={<AttackPathsPage />} />
        <Route path="/repositories" element={<RepositoriesPage />} />
        <Route path="/containers" element={<ContainersPage />} />
        <Route path="/secrets" element={<SecretsPage />} />
        <Route path="/scans" element={<ScansPage />} />
        <Route path="/ai-analyst" element={<AIAnalystPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}