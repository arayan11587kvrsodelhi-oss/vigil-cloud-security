import { useState, useEffect, useCallback } from 'react';
import { getAttackPaths, getAttackPathStats } from '../lib/api';
import ReactFlow, {
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  Handle,
  Position,
  BackgroundVariant,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion } from 'framer-motion';
import { Globe, Server, Shield, Database, Key, Terminal } from 'lucide-react';
import Card from '../components/shared/Card';
import SeverityBadge from '../components/shared/SeverityBadge';
import DataState from '../components/shared/DataState';
import SourceStateBadge from '../components/shared/SourceStateBadge';
import InfoTip from '../components/shared/InfoTip';

const NODE_ICONS: Record<string, React.ReactNode> = {
  source: <Globe className="w-4 h-4" />,
  entry: <Terminal className="w-4 h-4" />,
  vulnerability: <Shield className="w-4 h-4" />,
  container: <Server className="w-4 h-4" />,
  iam: <Key className="w-4 h-4" />,
  database: <Database className="w-4 h-4" />,
  secret: <Key className="w-4 h-4" />,
  storage: <Server className="w-4 h-4" />,
  host: <Server className="w-4 h-4" />,
  cluster: <Server className="w-4 h-4" />,
  data: <Database className="w-4 h-4" />,
};

// Node accent colours. Security semantics are preserved: vulnerability/secret/
// cluster use the critical red, entry/iam/host use warning amber, database/data
// use healthy green. The pink brand and purple accent colour the neutral stages.
const NODE_COLORS: Record<string, string> = {
  source: '#9B5CFF', // purple accent
  entry: '#FFB84D', // warning (high)
  vulnerability: '#FF3B6B', // critical
  container: '#FF4FD8', // electric pink (brand)
  iam: '#FFB84D', // warning (high)
  database: '#35E0A1', // healthy
  secret: '#FF3B6B', // critical
  storage: '#8E8298', // muted
  host: '#FFB84D', // warning (high)
  cluster: '#FF3B6B', // critical
  data: '#35E0A1', // healthy
};

function AttackPathNode({ data }: any) {
  return (
    <div
      className="px-4 py-3 rounded-lg shadow-card min-w-[180px] cursor-pointer group transition-colors duration-200 hover:border-border-strong"
      style={{
        // Restrained: neutral 1px border on all sides, semantic colour only on
        // the left accent rule so nodes read as an investigation graph, not neon.
        background: '#120A1C',
        border: '1px solid rgba(255, 255, 255, 0.06)',
        borderLeft: `3px solid ${NODE_COLORS[data.nodeType] || '#FF4FD8'}`,
      }}
      onClick={() => data.onSelect?.(data)}
    >
      <Handle type="target" position={Position.Top} style={{ background: '#2A1542', width: 8, height: 8 }} />
      <div className="flex items-center gap-2 mb-1">
        <span style={{ color: NODE_COLORS[data.nodeType] }}>{NODE_ICONS[data.nodeType]}</span>
        <span className="text-xs font-medium text-text">{data.label}</span>
      </div>
      <div className="text-[10px] text-text-secondary leading-tight">{data.detail}</div>
      <div className="mt-1">
        <SeverityBadge severity={data.risk} size="sm" />
      </div>
      <Handle type="source" position={Position.Bottom} style={{ background: '#2A1542', width: 8, height: 8 }} />
    </div>
  );
}

const nodeTypes = { attackPathNode: AttackPathNode };

export default function AttackPathsPage() {
  const [paths, setPaths] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPath, setSelectedPath] = useState<any>(null);
  const [activeGraph, setActiveGraph] = useState<any>(null);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const buildGraph = useCallback((path: any) => {
    const steps: any[] = Array.isArray(path?.steps) ? path.steps : [];
    const stepNodes = steps.map((step: any, idx: number) => ({
      id: `node-${idx}`,
      type: 'attackPathNode',
      position: { x: 250, y: idx * 140 + 40 },
      data: {
        label: step.node,
        nodeType: step.type,
        risk: step.risk,
        detail: step.detail,
        onSelect: () => setActiveGraph(path),
      },
    }));

    const stepEdges = [];
    for (let i = 0; i < steps.length - 1; i++) {
      stepEdges.push({
        id: `edge-${i}`,
        source: `node-${i}`,
        target: `node-${i + 1}`,
        animated: true,
        style: {
          // critical -> red, high -> amber, otherwise the pink brand colour.
          stroke: path.risk_level === 'critical' ? '#FF3B6B' : path.risk_level === 'high' ? '#FFB84D' : '#FF4FD8',
          strokeWidth: 2,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: path.risk_level === 'critical' ? '#FF3B6B' : path.risk_level === 'high' ? '#FFB84D' : '#FF4FD8',
        },
      });
    }

    setNodes(stepNodes);
    setEdges(stepEdges);
    setActiveGraph(path);
  }, [setNodes, setEdges]);

  useEffect(() => {
    Promise.all([getAttackPaths(), getAttackPathStats()])
      .then(([p, s]) => {
        setPaths(p);
        setStats(s);
        if (p?.items?.length > 0) {
          setSelectedPath(p.items[0]);
          buildGraph(p.items[0]);
        }
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [buildGraph]);

  return (
    <DataState loading={loading} error={error}>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 min-h-[600px] lg:h-[calc(100vh-12rem)]">
        {/* Attack path list */}
        <div className="space-y-3 overflow-y-auto max-h-[320px] lg:max-h-none pr-1">
          <div className="flex items-center justify-between gap-2">
            <span className="text-[10px] text-text-secondary uppercase tracking-wider">Attack Paths</span>
            <SourceStateBadge state={paths?.source_state} />
          </div>
          {stats && (
            <div className="grid grid-cols-3 gap-2">
              <Card padding="sm">
                <div className="text-[10px] text-text-secondary">Total Paths</div>
                <div className="text-lg font-bold text-text">{stats.total_paths}</div>
              </Card>
              <Card padding="sm">
                <div className="text-[10px] text-text-secondary">Critical</div>
                <div className="text-lg font-bold text-critical">{stats.critical}</div>
              </Card>
              <Card padding="sm">
                <div className="text-[10px] text-text-secondary flex items-center gap-1">
                  Avg Risk
                  <InfoTip
                    label="About the risk score"
                    text="Demo Risk Score. Influenced by vulnerability severity, internet exposure, privilege level, path depth and potential blast radius. Not a mathematically validated model."
                  />
                </div>
                <div className="text-lg font-bold text-warning">{stats.avg_risk_score}</div>
              </Card>
            </div>
          )}

          <div className="space-y-2">
            {paths?.items.map((path: any) => (
              <motion.div
                key={path.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${selectedPath?.id === path.id
                    ? 'bg-primary/10 border-primary/30'
                    : 'bg-surface border-border hover:border-primary/20'
                  }`}
                onClick={() => { setSelectedPath(path); buildGraph(path); }}
              >
                <div className="flex items-start justify-between gap-2 mb-1">
                  <div className="flex items-center gap-1">
                    <SeverityBadge severity={path.risk_level} size="sm" showLabel={false} />
                    <span className="text-xs font-medium text-text">
                      {String(path.risk_level ?? 'unknown').toUpperCase()}
                    </span>
                  </div>
                  <span
                    className="text-xs font-bold text-text"
                    title="Demo Risk Score"
                  >
                    {Number(path.risk_score ?? 0).toFixed(1)}
                  </span>
                </div>
                <div className="text-[10px] text-text-secondary mt-1 line-clamp-2">{path.name}</div>
                <div className="flex items-center gap-1 mt-1 text-[10px] text-muted">
                  <span>{Array.isArray(path.steps) ? path.steps.length : 0} steps</span>
                  <span>·</span>
                  <span>{Array.isArray(path.blast_radius) ? path.blast_radius.length : 0} blast radius items</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Graph area */}
        <div className="lg:col-span-2 h-[480px] lg:h-full">
          {activeGraph ? (
            <div className="h-full rounded-lg overflow-hidden border border-border" style={{ background: '#0D0814' }}>
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={nodeTypes}
                fitView
                attributionPosition="bottom-left"
                minZoom={0.5}
                maxZoom={2}
              >
                <Controls showInteractive={false} />
                <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#2A1542" />
              </ReactFlow>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center border border-border rounded-lg bg-surface">
              <div className="text-center max-w-md">
                <Terminal className="w-12 h-12 text-muted mx-auto mb-3" />
                <div className="text-sm text-text-secondary font-medium mb-1">Attack Path Visualization</div>
                <div className="text-xs text-muted">Select an attack path from the list to visualize the kill chain</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Detail panel */}
      {selectedPath && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 grid grid-cols-1 lg:grid-cols-3 gap-4"
        >
          <Card className="lg:col-span-2">
            <div className="flex items-center justify-between gap-2 mb-1">
              <div className="eyebrow tracking-wider">Description</div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-muted">Risk Score</span>
                <span className="text-sm font-bold text-text">{Number(selectedPath.risk_score ?? 0).toFixed(1)}</span>
                <SeverityBadge severity={selectedPath.risk_level} size="sm" />
              </div>
            </div>
            <div className="text-[10px] text-muted mb-3">
              Demo Risk Score - a demonstration value, not a mathematically validated risk algorithm.
            </div>
            <div className="text-xs text-text leading-relaxed">{selectedPath.description}</div>

            {Array.isArray(selectedPath.risk_factors) && selectedPath.risk_factors.length > 0 && (
              <>
                <div className="eyebrow tracking-wider mt-4 mb-2">
                  Risk Factors
                </div>
                <ul className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                  {selectedPath.risk_factors.map((factor: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2 text-[11px] text-text-secondary">
                      <span className="text-primary mt-0.5" aria-hidden="true">
                        •
                      </span>
                      <span>{factor}</span>
                    </li>
                  ))}
                </ul>
              </>
            )}

            <div className="eyebrow tracking-wider mt-4 mb-2">Blast Radius</div>
            <div className="flex flex-wrap gap-2">
              {(selectedPath.blast_radius ?? []).map((item: string, idx: number) => (
                <span key={idx} className="text-[10px] px-2 py-1 rounded bg-critical/10 text-critical border border-critical/30">
                  {item}
                </span>
              ))}
            </div>
          </Card>

          <Card>
            <div className="eyebrow tracking-wider mb-3">Remediation</div>
            <ol className="space-y-2">
              {(selectedPath.remediation ?? []).map((item: string, idx: number) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-text">
                  <span className="text-primary font-mono mt-0.5">{idx + 1}.</span>
                  <span>{item}</span>
                </li>
              ))}
            </ol>
          </Card>
        </motion.div>
      )}
    </DataState>
  );
}