import { useState, useRef } from "react";

export default function UploadModal({ onUpload, onClose, uploading }) {
  const [dragging, setDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const inputRef = useRef();

  const handleFile = (file) => {
    if (file && file.name.endsWith(".csv")) {
      setSelectedFile(file);
    } else {
      alert("Please upload a CSV file.");
    }
  };

  return (
    <div style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)",
      display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100
    }}>
      <div style={{
        background: "#fff", borderRadius: 14, padding: 28, width: 420,
        boxShadow: "0 20px 60px rgba(0,0,0,0.15)"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, color: "#101828" }}>Upload CSV for Quality Check</h2>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", fontSize: 20, color: "#98a2b3" }}>×</button>
        </div>

        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]); }}
          onClick={() => inputRef.current.click()}
          style={{
            border: `2px dashed ${dragging ? "#3b82f6" : "#e5e7eb"}`,
            borderRadius: 10, padding: "32px 20px", textAlign: "center",
            cursor: "pointer", background: dragging ? "#eff6ff" : "#f9fafb",
            transition: "all 0.15s", marginBottom: 16
          }}
        >
          <input ref={inputRef} type="file" accept=".csv" style={{ display: "none" }} onChange={(e) => handleFile(e.target.files[0])} />
          <div style={{ fontSize: 32, marginBottom: 8 }}>📂</div>
          {selectedFile ? (
            <p style={{ fontSize: 13, color: "#3b82f6", fontWeight: 500 }}>{selectedFile.name}</p>
          ) : (
            <>
              <p style={{ fontSize: 13, color: "#344054", fontWeight: 500 }}>Drop your CSV here or click to browse</p>
              <p style={{ fontSize: 12, color: "#98a2b3", marginTop: 4 }}>Supports any CSV file with headers</p>
            </>
          )}
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={onClose} style={{
            flex: 1, padding: "9px 0", border: "1px solid #e5e7eb", borderRadius: 8,
            background: "#fff", color: "#344054", fontSize: 13, fontWeight: 500, cursor: "pointer"
          }}>Cancel</button>
          <button
            onClick={() => selectedFile && onUpload(selectedFile)}
            disabled={!selectedFile || uploading}
            style={{
              flex: 1, padding: "9px 0", border: "none", borderRadius: 8,
              background: selectedFile && !uploading ? "#18181b" : "#e5e7eb",
              color: selectedFile && !uploading ? "#fff" : "#98a2b3",
              fontSize: 13, fontWeight: 600, cursor: selectedFile ? "pointer" : "not-allowed"
            }}
          >
            {uploading ? "Analysing..." : "Run Quality Check"}
          </button>
        </div>
      </div>
    </div>
  );
}
