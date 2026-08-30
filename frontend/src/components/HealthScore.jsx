export default function HealthScore({ score, anomalyCount }) {
  const s = Math.max(0, Math.min(100, score ?? 0));
  const color = s >= 80 ? "#22c55e" : s >= 60 ? "#f59e0b" : "#ef4444";
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (s / 100) * circumference;

  return (
    <div style={{
      background: "#fff", borderRadius: 12, border: "1px solid #eaecf0",
      padding: 18, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
    }}>
      <div style={{ fontSize: 12.5, fontWeight: 600, color: "#344054", alignSelf: "flex-start", marginBottom: 8 }}>
        Data Health
      </div>

      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="#eaecf0" strokeWidth="12" />
        <circle
          cx="70" cy="70" r={radius} fill="none" stroke={color} strokeWidth="12"
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(-90 70 70)"
          style={{ transition: "stroke-dashoffset 0.4s ease" }}
        />
        <text x="70" y="66" textAnchor="middle" fontSize="26" fontWeight="700" fill="#101828" fontFamily="'JetBrains Mono', monospace">
          {Math.round(s)}
        </text>
        <text x="70" y="86" textAnchor="middle" fontSize="11" fill="#98a2b3">
          / 100
        </text>
      </svg>

      <div style={{ fontSize: 12, color: "#98a2b3", marginTop: 4 }}>
        {anomalyCount} anomal{anomalyCount === 1 ? "y" : "ies"} detected
      </div>
    </div>
  );
}
