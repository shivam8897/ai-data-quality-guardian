import { useState } from "react";

export default function ConnectDbModal({ onConnect, onClose, connecting }) {
  const [connectionString, setConnectionString] = useState("");
  const [tableName, setTableName] = useState("");
  const [sampleRows, setSampleRows] = useState("");

  const canSubmit = connectionString.trim() && tableName.trim();

  const handleSubmit = () => {
    if (!canSubmit) return;
    onConnect({
      connection_string: connectionString.trim(),
      table_name: tableName.trim(),
      sample_rows: sampleRows ? parseInt(sampleRows, 10) : null,
    });
  };

  const inputStyle = {
    width: "100%", padding: "9px 10px", borderRadius: 8,
    border: "1px solid #e5e7eb", fontSize: 13, color: "#101828",
    boxSizing: "border-box",
  };
  const labelStyle = { fontSize: 12, fontWeight: 500, color: "#344054", marginBottom: 6, display: "block" };

  return (
    <div style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)",
      display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100
    }}>
      <div style={{
        background: "#fff", borderRadius: 14, padding: 28, width: 440,
        boxShadow: "0 20px 60px rgba(0,0,0,0.15)"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, color: "#101828" }}>Connect a Database Table</h2>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", fontSize: 20, color: "#98a2b3" }}>×</button>
        </div>

        <div style={{ marginBottom: 14 }}>
          <label style={labelStyle}>Connection string</label>
          <input
            style={inputStyle}
            type="text"
            placeholder="postgresql://user:pass@host:5432/dbname"
            value={connectionString}
            onChange={(e) => setConnectionString(e.target.value)}
          />
          <p style={{ fontSize: 11, color: "#98a2b3", marginTop: 4 }}>
            Used only to run this check — never stored.
          </p>
        </div>

        <div style={{ marginBottom: 14 }}>
          <label style={labelStyle}>Table name</label>
          <input
            style={inputStyle}
            type="text"
            placeholder="orders"
            value={tableName}
            onChange={(e) => setTableName(e.target.value)}
          />
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={labelStyle}>Row sample limit (optional)</label>
          <input
            style={inputStyle}
            type="number"
            min="1"
            placeholder="e.g. 100000 — leave blank for the full table"
            value={sampleRows}
            onChange={(e) => setSampleRows(e.target.value)}
          />
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={onClose} style={{
            flex: 1, padding: "9px 0", border: "1px solid #e5e7eb", borderRadius: 8,
            background: "#fff", color: "#344054", fontSize: 13, fontWeight: 500, cursor: "pointer"
          }}>Cancel</button>
          <button
            onClick={handleSubmit}
            disabled={!canSubmit || connecting}
            style={{
              flex: 1, padding: "9px 0", border: "none", borderRadius: 8,
              background: canSubmit && !connecting ? "#18181b" : "#e5e7eb",
              color: canSubmit && !connecting ? "#fff" : "#98a2b3",
              fontSize: 13, fontWeight: 600, cursor: canSubmit ? "pointer" : "not-allowed"
            }}
          >
            {connecting ? "Analysing..." : "Run Quality Check"}
          </button>
        </div>
      </div>
    </div>
  );
}
