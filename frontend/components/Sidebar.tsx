"use client";

import { useState, useEffect } from "react";
import { syncData } from "../lib/api";

interface SidebarProps {
  isDark: boolean;
  onToggleTheme: () => void;
}

export default function Sidebar({ isDark, onToggleTheme }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncMsg, setSyncMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const handleSync = async () => {
    setSyncing(true);
    setSyncMsg(null);
    try {
      const res = await syncData();
      setSyncMsg({ type: "success", text: res.message || "Đồng bộ thành công!" });
    } catch {
      setSyncMsg({ type: "error", text: "Lỗi kết nối. Vui lòng thử lại." });
    } finally {
      setSyncing(false);
    }
  };

  // Keyboard shortcut D → toggle theme
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName?.toLowerCase();
      if (tag === "input" || tag === "textarea" || (e.target as HTMLElement).isContentEditable) return;
      if (e.key === "d" || e.key === "D") onToggleTheme();
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [onToggleTheme]);

  return (
    <>
      {/* Sidebar panel */}
      <aside className={`sidebar${collapsed ? " collapsed" : ""}`}>
        <div className="sidebar-title">🛠️ Quản trị Data</div>
        <hr className="sidebar-divider" />

        <p className="sidebar-desc">
          Nhấn nút bên dưới để crawler thu thập toàn bộ dữ liệu chương trình đào tạo từ{" "}
          <strong style={{ color: "var(--text-accent)" }}>NEU</strong> và lưu vào cơ sở dữ liệu.
        </p>

        <button
          id="sync-btn"
          className="btn-primary"
          onClick={handleSync}
          disabled={syncing}
        >
          {syncing ? "⏳  Đang đồng bộ..." : "🚀  Cập nhật dữ liệu mới nhất"}
        </button>

        {syncMsg && (
          <div className={`alert alert-${syncMsg.type}`}>
            {syncMsg.type === "success" ? "✅" : "❌"} {syncMsg.text}
          </div>
        )}

        <div className="sidebar-info-box">
          📡 <strong>API Backend:</strong>
          <br />
          <code>/api</code>
          <br />
          <br />
          🗄️ <strong>Database:</strong> MongoDB Atlas
          <br />
          🔄 <strong>Cache:</strong> 60 giây
        </div>

        <div className="sidebar-shortcut">
          {isDark ? "☀️" : "🌙"} <strong>Phím tắt:</strong> Nhấn{" "}
          <kbd>D</kbd> để đổi giao diện
        </div>

        <button
          id="theme-toggle-sidebar"
          className="theme-toggle"
          onClick={onToggleTheme}
          style={{ marginTop: "auto" }}
        >
          {isDark ? "☀️ Light Mode" : "🌙 Dark Mode"}
        </button>
      </aside>

      {/* Floating toggle arrow */}
      <button
        id="sidebar-toggle-arrow"
        className={`sidebar-toggle-btn${collapsed ? " collapsed" : ""}`}
        onClick={() => setCollapsed((c) => !c)}
        title={collapsed ? "Mở sidebar" : "Đóng sidebar"}
        style={{ left: collapsed ? "0" : "280px" }}
      >
        {collapsed ? "›" : "‹"}
      </button>
    </>
  );
}
