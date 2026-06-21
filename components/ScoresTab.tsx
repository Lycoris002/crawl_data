"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

interface ScoresTabProps {
  scores: Record<string, number>;
  isDark: boolean;
}

interface TooltipPayload {
  value: number;
}

// Custom tooltip component
function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: TooltipPayload[];
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div
      style={{
        background: "var(--chart-tooltip-bg)",
        border: "1px solid var(--chart-tooltip-border)",
        borderRadius: "10px",
        padding: "10px 16px",
        boxShadow: "0 8px 24px rgba(0,0,0,0.15)",
        color: "var(--text-primary)",
        fontSize: "0.88rem",
      }}
    >
      <p style={{ fontWeight: 700, marginBottom: 4 }}>Năm {label}</p>
      <p style={{ color: "var(--text-accent)", fontWeight: 600 }}>
        Điểm chuẩn: <strong>{payload[0].value}</strong>
      </p>
    </div>
  );
}

export default function ScoresTab({ scores, isDark }: ScoresTabProps) {
  if (!scores || Object.keys(scores).length === 0) {
    return (
      <div className="alert alert-info">
        ℹ️ Nhà trường chưa công bố hoặc chưa cập nhật dữ liệu điểm chuẩn cho ngành này.
      </div>
    );
  }

  const data = Object.entries(scores)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([year, score]) => ({ year, score }));

  const latestEntry = data[data.length - 1];
  const prevEntry = data[data.length - 2];
  const delta = prevEntry
    ? (latestEntry.score - prevEntry.score).toFixed(2)
    : null;

  const gridColor = isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)";
  const axisColor = isDark ? "#64748b" : "#94a3b8";

  return (
    <div>
      <h3 className="section-title">📊 Lịch sử Điểm chuẩn</h3>

      <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: "1.5rem", alignItems: "start" }}>
        {/* Chart */}
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
              <XAxis
                dataKey="year"
                tick={{ fill: axisColor, fontSize: 12 }}
                axisLine={{ stroke: gridColor }}
                tickLine={false}
              />
              <YAxis
                domain={["auto", "auto"]}
                tick={{ fill: axisColor, fontSize: 12 }}
                axisLine={false}
                tickLine={false}
                width={40}
              />
              <Tooltip content={<CustomTooltip />} />
              <ReferenceLine
                y={latestEntry.score}
                stroke={isDark ? "rgba(99,179,237,0.25)" : "rgba(59,130,246,0.2)"}
                strokeDasharray="4 4"
              />
              <Line
                type="monotone"
                dataKey="score"
                stroke={isDark ? "#60a5fa" : "#3b82f6"}
                strokeWidth={2.5}
                dot={{
                  r: 5,
                  fill: isDark ? "#93c5fd" : "#1d4ed8",
                  strokeWidth: 2,
                  stroke: isDark ? "#0d1526" : "#ffffff",
                }}
                activeDot={{
                  r: 7,
                  fill: isDark ? "#60a5fa" : "#2563eb",
                  strokeWidth: 3,
                  stroke: isDark ? "#0d1526" : "#ffffff",
                }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Metric */}
        <div className="metric-card" style={{ minWidth: "160px" }}>
          <p className="metric-label">🏆 Điểm chuẩn {latestEntry.year}</p>
          <p className="metric-value">{latestEntry.score}</p>
          {delta && (
            <p className="metric-delta">
              {parseFloat(delta) >= 0 ? "▲" : "▼"}{" "}
              {Math.abs(parseFloat(delta))} so với {prevEntry?.year}
            </p>
          )}
        </div>
      </div>

      {/* Score history table */}
      <div style={{ marginTop: "1.5rem" }}>
        <table className="subject-table">
          <thead>
            <tr>
              <th>Năm</th>
              <th style={{ textAlign: "right" }}>Điểm chuẩn</th>
            </tr>
          </thead>
          <tbody>
            {[...data].reverse().map(({ year, score }) => (
              <tr key={year}>
                <td style={{ fontWeight: 600 }}>{year}</td>
                <td style={{ textAlign: "right", fontWeight: 700, color: "var(--text-accent)" }}>
                  {score}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
