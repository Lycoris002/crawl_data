"use client";

import { useState, useEffect, useCallback } from "react";
import Sidebar from "../components/Sidebar";
import SearchBar from "../components/SearchBar";
import MajorCard from "../components/MajorCard";
import ScoresTab from "../components/ScoresTab";
import CurriculumTab from "../components/CurriculumTab";
import OutcomesTab from "../components/OutcomesTab";
import { searchMajors, getCurriculum, Major, MajorDetail } from "../lib/api";

export default function Home() {
  const [isDark, setIsDark] = useState(true);
  const [activeTab, setActiveTab] = useState<"scores" | "curriculum" | "outcomes">("scores");

  // Data
  const [majors, setMajors] = useState<Major[]>([]);
  const [majorsLoading, setMajorsLoading] = useState(true);
  const [majorsError, setMajorsError] = useState<string | null>(null);

  const [selectedId, setSelectedId] = useState("");
  const [detail, setDetail] = useState<MajorDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  // Apply theme to <html>
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", isDark ? "dark" : "light");
  }, [isDark]);

  const toggleTheme = useCallback(() => setIsDark((d) => !d), []);

  // Fetch major list on mount
  useEffect(() => {
    setMajorsLoading(true);
    searchMajors()
      .then(setMajors)
      .catch(() => setMajorsError("Không thể tải danh sách ngành. Vui lòng kiểm tra kết nối backend."))
      .finally(() => setMajorsLoading(false));
  }, []);

  // Fetch detail when selection changes
  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      setDetailError(null);
      return;
    }
    setDetailLoading(true);
    setDetailError(null);
    setDetail(null);
    getCurriculum(selectedId)
      .then(setDetail)
      .catch(() => setDetailError("Không tìm thấy thông tin chi tiết cho ngành này."))
      .finally(() => setDetailLoading(false));
  }, [selectedId]);

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <Sidebar isDark={isDark} onToggleTheme={toggleTheme} />

      {/* Main content */}
      <main className="main-content">
        {/* Header */}
        <h1 className="main-header">🎓 NEU Course Explorer</h1>
        <p className="sub-header">
          Tra cứu điểm chuẩn &amp; lộ trình đào tạo · Đại học Kinh tế Quốc dân
        </p>
        <p className="theme-badge">
          {isDark ? "☀️" : "🌙"} Đang dùng {isDark ? "Dark" : "Light"} Mode · Nhấn{" "}
          <kbd style={{ fontFamily: "monospace", fontSize: "0.75rem" }}>D</kbd> để đổi
        </p>
        <div className="fancy-divider" />

        {/* Errors / warnings */}
        {majorsError && (
          <div className="alert alert-error" style={{ maxWidth: 600, margin: "0 auto 1.5rem" }}>
            ❌ {majorsError}
          </div>
        )}

        {!majorsLoading && !majorsError && majors.length === 0 && (
          <div className="alert alert-warning" style={{ maxWidth: 600, margin: "0 auto 1.5rem" }}>
            ⚠️ Chưa có dữ liệu. Vui lòng mở <strong>Sidebar → Cập nhật dữ liệu mới nhất</strong> để
            bắt đầu thu thập.
          </div>
        )}

        {/* Search */}
        <SearchBar
          options={majors}
          value={selectedId}
          onChange={setSelectedId}
          loading={majorsLoading}
        />

        {/* Detail view */}
        {detailLoading && (
          <div className="spinner-wrap">
            <div className="spinner" />
            ✨ Đang tải dữ liệu...
          </div>
        )}

        {detailError && (
          <div className="alert alert-error" style={{ maxWidth: 700, margin: "0 auto" }}>
            ❌ {detailError}
          </div>
        )}

        {detail && !detailLoading && (
          <>
            <MajorCard detail={detail} />

            {/* Tabs */}
            <div className="glass-card" style={{ padding: "24px 28px" }}>
              <div className="tabs-header">
                <button
                  id="tab-scores"
                  className={`tab-btn${activeTab === "scores" ? " active" : ""}`}
                  onClick={() => setActiveTab("scores")}
                >
                  📈 Điểm chuẩn (Dự kiến)
                </button>
                <button
                  id="tab-curriculum"
                  className={`tab-btn${activeTab === "curriculum" ? " active" : ""}`}
                  onClick={() => setActiveTab("curriculum")}
                >
                  📚 Lộ trình học (Dự kiến)
                </button>
                <button
                  id="tab-outcomes"
                  className={`tab-btn${activeTab === "outcomes" ? " active" : ""}`}
                  onClick={() => setActiveTab("outcomes")}
                >
                  🎯 Chuẩn đầu ra chương trình
                </button>
              </div>

              {activeTab === "scores" && (
                <ScoresTab scores={detail.scores} isDark={isDark} />
              )}
              {activeTab === "curriculum" && (
                <CurriculumTab curriculum={detail.curriculum} />
              )}
              {activeTab === "outcomes" && (
                <OutcomesTab summary={detail.outcomesSummary} />
              )}
            </div>
          </>
        )}

        {/* Empty selection state */}
        {!selectedId && !majorsLoading && majors.length > 0 && (
          <div className="empty-state">
            <span className="empty-state-icon">🎓</span>
            <p className="empty-state-title">Chọn một ngành học để bắt đầu</p>
            <p className="empty-state-desc">
              Tra cứu điểm chuẩn và lộ trình đào tạo của{" "}
              <strong>{majors.length}</strong> ngành học tại Đại học Kinh tế Quốc dân
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
