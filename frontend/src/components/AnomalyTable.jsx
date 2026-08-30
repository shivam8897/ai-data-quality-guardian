import { useState } from "react";

const severityColor = (sev) => ({
  critical: "#ef4444",
  warning: "#f59e0b",
  info: "#3b82f6",
}[sev] || "#98a2b3");

export default function AnomalyTable({ anomalies }) {
  const [expandedId, setExpandedId] = useState(null);

  return (
    <div style={{ background: "#fff", borderRadius: 12, border: "1px solid #eaecf0", overflow: "hidden" }}>
      <div style={{ padding: "14px 18px", fontSize: 12.5, fontWeight: 600, color: "#344054", borderBottom: "1px solid #eaecf0" }}>
        Anomalies ({anomalies.length})
      </div>

      {anomalies.length === 0 ? (
        <div style={{ padding: "24px 18px", textAlign: "center", color: "#98a2b3", fontSize: 13 }}>
          No anomalies detected. Data looks healthy.
        </div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12.5 }}>
          <thead>
            <tr style={{ background: "#f9fafb" }}>
              {["Severity", "Column", "Type", "Detected", "Expected", "AI Explanation"].map((h) => (
                <th key={h} style={{ textAlign: "left", padding: "8px 12px", color: "#98a2b3", fontWeight: 600, fontSize: 11 }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {anomalies.map((a, i) => {
              const id = a.id ?? i;
              const expanded = expandedId === id;
              return (
                <tr
                  key={id}
                  onClick={() => setExpandedId(expanded ? null : id)}
                  style={{ borderTop: "1px solid #f0f2f5", cursor: "pointer" }}
                >
                  <td style={{ padding: "10px 12px" }}>
                    <span style={{
                      fontSize: 10.5, fontWeight: 700, textTransform: "uppercase", color: "#fff",
                      background: severityColor(a.severity), borderRadius: 5, padding: "2px 7px",
                    }}>
                      {a.severity}
                    </span>
                  </td>
                  <td style={{ padding: "10px 12px", fontWeight: 500, color: "#101828" }}>{a.column_name}</td>
                  <td style={{ padding: "10px 12px", color: "#475467" }}>{a.anomaly_type?.replace(/_/g, " ")}</td>
                  <td style={{ padding: "10px 12px", color: "#475467", fontFamily: "'JetBrains Mono', monospace" }}>{a.detected_value}</td>
                  <td style={{ padding: "10px 12px", color: "#98a2b3", fontFamily: "'JetBrains Mono', monospace" }}>{a.expected_range}</td>
                  <td style={{ padding: "10px 12px", color: "#475467", maxWidth: expanded ? "none" : 260, whiteSpace: expanded ? "normal" : "nowrap", overflow: expanded ? "visible" : "hidden", textOverflow: "ellipsis" }}>
                    {a.ai_explanation}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
