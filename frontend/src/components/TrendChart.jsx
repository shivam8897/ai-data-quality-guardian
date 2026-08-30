import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts";

export default function TrendChart({ runs, currentRunId }) {
  const data = [...runs].reverse().map((r) => ({
    id: r.id,
    name: new Date(r.run_at).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
    score: Number(r.health_score) || 0,
  }));

  return (
    <div style={{ background: "#fff", borderRadius: 12, border: "1px solid #eaecf0", padding: 18 }}>
      <div style={{ fontSize: 12.5, fontWeight: 600, color: "#344054", marginBottom: 12 }}>
        Health Score History
      </div>

      {data.length === 0 ? (
        <div style={{ height: 180, display: "flex", alignItems: "center", justifyContent: "center", color: "#98a2b3", fontSize: 12.5 }}>
          Not enough runs yet
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f2f5" vertical={false} />
            <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#98a2b3" }} axisLine={false} tickLine={false} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: "#98a2b3" }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: "1px solid #eaecf0", fontSize: 12 }}
              formatter={(value) => [`${value}`, "Health Score"]}
            />
            <Bar dataKey="score" radius={[4, 4, 0, 0]}>
              {data.map((d) => (
                <Cell key={d.id} fill={d.id === currentRunId ? "#3b82f6" : "#c7d2fe"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
