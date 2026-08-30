import { useState, useEffect } from "react";
import axios from "axios";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import KpiCards from "./components/KpiCards";
import HealthScore from "./components/HealthScore";
import TrendChart from "./components/TrendChart";
import AnomalyTable from "./components/AnomalyTable";
import AiInsightCard from "./components/AiInsightCard";
import ColumnQuality from "./components/ColumnQuality";
import UploadModal from "./components/UploadModal";
import ConnectDbModal from "./components/ConnectDbModal";

const API = "http://localhost:8000";

export default function App() {
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showConnect, setShowConnect] = useState(false);
  const [connecting, setConnecting] = useState(false);

  useEffect(() => {
    fetchRuns();
  }, []);

  const fetchRuns = async () => {
    try {
      const res = await axios.get(`${API}/api/runs`);
      setRuns(res.data);
      if (res.data.length > 0 && !selectedRun) {
        fetchRunDetail(res.data[0].id);
      }
    } catch (err) {
      console.error("Failed to fetch runs:", err);
    }
  };

  const fetchRunDetail = async (runId) => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/api/runs/${runId}`);
      setSelectedRun(res.data);
    } catch (err) {
      console.error("Failed to fetch run detail:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file) => {
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await axios.post(`${API}/api/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setSelectedRun(res.data);
      await fetchRuns();
      setShowUpload(false);
    } catch (err) {
      alert("Upload failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setUploading(false);
    }
  };

  const handleConnect = async (payload) => {
    setConnecting(true);
    try {
      const res = await axios.post(`${API}/api/connect`, payload);
      setSelectedRun(res.data);
      await fetchRuns();
      setShowConnect(false);
    } catch (err) {
      alert("Connection failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setConnecting(false);
    }
  };

  const run = selectedRun;
  const criticalCount = run?.anomalies?.filter(a => a.severity === "critical").length || 0;
  const warningCount = run?.anomalies?.filter(a => a.severity === "warning").length || 0;
  const topAnomaly = run?.anomalies?.find(a => a.severity === "critical") || run?.anomalies?.[0];

  return (
    <div style={{ display: "flex", height: "100vh", background: "#f0f2f5", fontFamily: "Inter, sans-serif" }}>
      <Sidebar runs={runs} selectedRunId={run?.id} onSelectRun={fetchRunDetail} />

      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        <Topbar
          sourceName={run?.source_name || "No data"}
          onUpload={() => setShowUpload(true)}
          onConnect={() => setShowConnect(true)}
          onRefresh={fetchRuns}
        />

        {loading ? (
          <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "#98a2b3" }}>
            Running quality check...
          </div>
        ) : run ? (
          <div style={{ flex: 1, overflowY: "auto", padding: "18px 20px", display: "flex", flexDirection: "column", gap: 14 }}>
            <KpiCards
              healthScore={run.health_score}
              totalRows={run.total_rows}
              criticalCount={criticalCount}
              warningCount={warningCount}
              duration={run.duration_secs}
            />

            <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 12 }}>
              <TrendChart runs={runs} currentRunId={run.id} />
              <HealthScore score={run.health_score} anomalyCount={run.anomalies?.length || 0} />
            </div>

            {topAnomaly && <AiInsightCard anomaly={topAnomaly} />}

            <AnomalyTable anomalies={run.anomalies || []} />

            <ColumnQuality profiles={run.column_profiles || []} />
          </div>
        ) : (
          <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 12 }}>
            <p style={{ color: "#98a2b3", fontSize: 14 }}>No data yet. Upload a CSV or connect a database table to get started.</p>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                onClick={() => setShowUpload(true)}
                style={{ background: "#18181b", color: "#fff", border: "none", padding: "8px 20px", borderRadius: 8, cursor: "pointer", fontSize: 13, fontWeight: 500 }}
              >
                Upload CSV
              </button>
              <button
                onClick={() => setShowConnect(true)}
                style={{ background: "#fff", color: "#344054", border: "1px solid #e5e7eb", padding: "8px 20px", borderRadius: 8, cursor: "pointer", fontSize: 13, fontWeight: 500 }}
              >
                Connect DB
              </button>
            </div>
          </div>
        )}
      </div>

      {showUpload && (
        <UploadModal
          onUpload={handleUpload}
          onClose={() => setShowUpload(false)}
          uploading={uploading}
        />
      )}

      {showConnect && (
        <ConnectDbModal
          onConnect={handleConnect}
          onClose={() => setShowConnect(false)}
          connecting={connecting}
        />
      )}
    </div>
  );
}
