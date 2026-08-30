export default function Sidebar({ runs, selectedRunId, onSelectRun }) {
  return (
    <div style={{
      width: 240, background: "#18181b", color: "#e4e4e7",
      display: "flex", flexDirection: "column", padding: "18px 14px",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 24, padding: "0 6px" }}>
        <span style={{ fontSize: 20 }}>🛡️</span>
        <span style={{ fontWeight: 700, fontSize: 14, color: "#fff" }}>DQ Guardian</span>
      </div>

      <div style={{ fontSize: 11, fontWeight: 600, color: "#71717a", textTransform: "uppercase", letterSpacing: 0.5, padding: "0 6px", marginBottom: 8 }}>
        Recent Runs
      </div>

      <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 4 }}>
        {runs.length === 0 && (
          <div style={{ fontSize: 12, color: "#71717a", padding: "8px 6px" }}>No runs yet</div>
        )}
        {runs.map((r) => {
          const active = r.id === selectedRunId;
          const scoreColor = r.health_score >= 80 ? "#22c55e" : r.health_score >= 60 ? "#f59e0b" : "#ef4444";
          return (
            <button
              key={r.id}
              onClick={() => onSelectRun(r.id)}
              style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                textAlign: "left", padding: "9px 10px", borderRadius: 8, border: "none",
                background: active ? "#27272a" : "transparent", cursor: "pointer",
              }}
            >
              <div style={{ overflow: "hidden" }}>
                <div style={{ fontSize: 12.5, fontWeight: 500, color: "#fff", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {r.source_name}
                </div>
                <div style={{ fontSize: 11, color: "#71717a" }}>
                  {new Date(r.run_at).toLocaleDateString()} · {r.anomaly_count} issues
                </div>
              </div>
              <span style={{ fontSize: 11, fontWeight: 700, color: scoreColor, flexShrink: 0, marginLeft: 8 }}>
                {Math.round(r.health_score)}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
