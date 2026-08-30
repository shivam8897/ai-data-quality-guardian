const severityColor = (sev) => ({
  critical: "#ef4444",
  warning: "#f59e0b",
  info: "#3b82f6",
}[sev] || "#98a2b3");

export default function AiInsightCard({ anomaly }) {
  return (
    <div style={{
      borderRadius: 12, padding: 18,
      background: "linear-gradient(135deg, #eff6ff, #eef2ff)",
      border: "1px solid #dbeafe",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
        <span style={{ fontSize: 16 }}>✨</span>
        <span style={{ fontSize: 12.5, fontWeight: 700, color: "#3730a3" }}>AI Insight</span>
        <span style={{
          fontSize: 10.5, fontWeight: 700, textTransform: "uppercase", color: "#fff",
          background: severityColor(anomaly.severity), borderRadius: 5, padding: "2px 7px", marginLeft: "auto",
        }}>
          {anomaly.severity}
        </span>
      </div>

      <div style={{ fontSize: 13, color: "#101828", fontWeight: 500, marginBottom: 8 }}>
        {anomaly.column_name} — {anomaly.anomaly_type?.replace(/_/g, " ")}
      </div>

      <p style={{ fontSize: 13, color: "#344054", lineHeight: 1.5, marginBottom: 8 }}>
        {anomaly.ai_explanation || "No explanation available."}
      </p>

      {anomaly.ai_recommendation && (
        <div style={{ fontSize: 12.5, color: "#1e293b", background: "rgba(255,255,255,0.6)", borderRadius: 8, padding: "8px 10px", marginBottom: anomaly.ai_fix_code ? 8 : 0 }}>
          <strong>Recommendation:</strong> {anomaly.ai_recommendation}
        </div>
      )}

      {anomaly.ai_fix_code && (
        <pre style={{
          fontSize: 12, fontFamily: "'JetBrains Mono', monospace", background: "#0f172a",
          color: "#e2e8f0", borderRadius: 8, padding: "10px 12px", overflowX: "auto", margin: 0,
        }}>
          {anomaly.ai_fix_code}
        </pre>
      )}
    </div>
  );
}
