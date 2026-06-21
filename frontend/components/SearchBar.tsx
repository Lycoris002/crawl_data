"use client";

import { Major } from "@/lib/api";

interface SearchBarProps {
  options: Major[];
  value: string;
  onChange: (id: string) => void;
  loading: boolean;
}

export default function SearchBar({ options, value, onChange, loading }: SearchBarProps) {
  return (
    <div className="search-wrap">
      <label className="search-label" htmlFor="major-select">
        🔍 Tìm ngành học
      </label>
      <div style={{ position: "relative" }}>
        <select
          id="major-select"
          className="search-select"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={loading}
        >
          <option value="">
            {loading ? "⏳ Đang tải danh sách ngành..." : "🔍  Chọn mã xét tuyển hoặc tên ngành..."}
          </option>
          {options.map((m) => (
            <option key={m.id} value={m.id}>
              {m.display_name}
            </option>
          ))}
        </select>
        <span className="search-select-icon">▼</span>
      </div>
    </div>
  );
}
