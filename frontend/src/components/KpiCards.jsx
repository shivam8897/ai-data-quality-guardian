const cardStyle = {
  background: "#fff", borderRadius: 12, padding: "14px 16px",
  border: "1px solid #eaecf0", flex: 1,
};
const labelStyle = { fontSize: 11.5, color: "#98a2b3", fontWeight: 500, marginBottom: 6 };
const valueStyle = { fontSize: 22, fontWeight: 700, color: "#101828", fontFamily: "'JetBrains Mono', monospace" };

export default function KpiCards({ healthScore, totalRows, criticalCount, warningCount, duration }) {
  const scoreColor = healthScore >= 80 ? "#22c55e" : healthScore >= 60 ? "#f59e0b" : "#ef4444";

  const items = [
    { label: "Health Score", value: `${Math.round(healthScore)}/100`, color: scoreColor },
    { label: "Rows Scanned", value: (totalRows ?? 0).toLocaleString(), color: "#101828" },
    { label: "Critical Issues", value: criticalCount, color: criticalCount > 0 ? "#ef4444" : "#101828" },
    { label: "Warnings", value: warningCount, color: warningCount > 0 ? "#f59e0b" : "#101828" },
    { label: "Scan Duration", value: `${duration ?? 0}s`, color: "#101828" },
  ];

  return (
    <div style={{ display: "flex", gap: 12 }}>
      {items.map((item) => (
        <div key={item.label} style={cardStyle}>
          <div style={labelStyle}>{item.label}</div>
          <div style={{ ...valueStyle, color: item.color }}>{item.value}</div>
        </div>
      ))}
    </div>
  );
}
