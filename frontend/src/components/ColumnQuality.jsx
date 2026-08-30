const qualityColor = (score) => (score >= 80 ? "#22c55e" : score >= 60 ? "#f59e0b" : "#ef4444");

export default function ColumnQuality({ profiles }) {
  return (
    <div style={{ background: "#fff", borderRadius: 12, border: "1px solid #eaecf0", padding: 18 }}>
      <div style={{ fontSize: 12.5, fontWeight: 600, color: "#344054", marginBottom: 14 }}>
        Column Quality
      </div>

      {profiles.length === 0 ? (
        <div style={{ color: "#98a2b3", fontSize: 13 }}>No column data available.</div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {profiles.map((p) => (
            <div key={p.column_name}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ fontSize: 12.5, fontWeight: 500, color: "#101828" }}>{p.column_name}</span>
                <span style={{ fontSize: 11.5, color: "#98a2b3" }}>
                  {p.data_type} · {p.null_pct}% null
                  {p.duplicate_count > 0 ? ` · ${p.duplicate_count} dup` : ""}
                </span>
              </div>
              <div style={{ height: 6, background: "#f0f2f5", borderRadius: 4, overflow: "hidden" }}>
                <div
                  style={{
                    width: `${Math.max(0, Math.min(100, p.quality_score))}%`,
                    height: "100%",
                    background: qualityColor(p.quality_score),
                    borderRadius: 4,
                    transition: "width 0.3s ease",
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
