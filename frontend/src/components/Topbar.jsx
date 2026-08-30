export default function Topbar({ sourceName, onUpload, onConnect, onRefresh }) {
  return (
    <div style={{
      height: 58, background: "#fff", borderBottom: "1px solid #eaecf0",
      display: "flex", alignItems: "center", justifyContent: "space-between",
      padding: "0 20px", flexShrink: 0,
    }}>
      <div>
        <div style={{ fontSize: 14, fontWeight: 600, color: "#101828" }}>{sourceName}</div>
        <div style={{ fontSize: 11, color: "#98a2b3" }}>Data Quality Overview</div>
      </div>

      <div style={{ display: "flex", gap: 8 }}>
        <button
          onClick={onRefresh}
          style={{
            padding: "7px 14px", borderRadius: 8, border: "1px solid #e5e7eb",
            background: "#fff", color: "#344054", fontSize: 12.5, fontWeight: 500, cursor: "pointer",
          }}
        >
          Refresh
        </button>
        <button
          onClick={onConnect}
          style={{
            padding: "7px 14px", borderRadius: 8, border: "1px solid #e5e7eb",
            background: "#fff", color: "#344054", fontSize: 12.5, fontWeight: 500, cursor: "pointer",
          }}
        >
          + Connect DB
        </button>
        <button
          onClick={onUpload}
          style={{
            padding: "7px 16px", borderRadius: 8, border: "none",
            background: "linear-gradient(135deg, #3b82f6, #6366f1)",
            color: "#fff", fontSize: 12.5, fontWeight: 600, cursor: "pointer",
          }}
        >
          + Upload CSV
        </button>
      </div>
    </div>
  );
}
