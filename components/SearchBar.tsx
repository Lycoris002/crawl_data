"use client";

import { useState, useRef, useEffect, useMemo } from "react";
import { Major } from "../lib/api";

interface SearchBarProps {
  options: Major[];
  value: string;
  onChange: (id: string) => void;
  loading: boolean;
}

// Helper function to remove Vietnamese diacritics for accent-insensitive search
function removeDiacritics(str: string): string {
  return str
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/đ/g, "d")
    .replace(/Đ/g, "D");
}

export default function SearchBar({ options, value, onChange, loading }: SearchBarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Find currently selected major
  const selectedMajor = useMemo(() => {
    return options.find((m) => m.id === value);
  }, [options, value]);

  // Sync searchQuery with selectedMajor's name when not focused
  useEffect(() => {
    if (!isFocused) {
      setSearchQuery(selectedMajor ? selectedMajor.display_name : "");
    }
  }, [selectedMajor, isFocused]);

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setIsFocused(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Filter options based on query (accent-insensitive)
  const filteredOptions = useMemo(() => {
    const query = removeDiacritics(searchQuery.toLowerCase().trim());
    
    // If query is empty or matches the selected major's display name exactly (without accents), show all options
    if (!query || (selectedMajor && query === removeDiacritics(selectedMajor.display_name.toLowerCase()))) {
      return options;
    }
    
    return options.filter((m) => {
      const code = removeDiacritics(m.major_code.toLowerCase());
      const name = removeDiacritics(m.major_name.toLowerCase());
      const school = m.school ? removeDiacritics(m.school.toLowerCase()) : "";
      const display = removeDiacritics(m.display_name.toLowerCase());
      
      return (
        code.includes(query) ||
        name.includes(query) ||
        display.includes(query) ||
        school.includes(query)
      );
    });
  }, [options, searchQuery, selectedMajor]);

  const handleSelect = (major: Major) => {
    onChange(major.id);
    setSearchQuery(major.display_name);
    setIsOpen(false);
    setIsFocused(false);
    inputRef.current?.blur();
  };

  const handleInputFocus = () => {
    setIsFocused(true);
    setIsOpen(true);
    
    // Select all text when clicking into an already populated search box to let them type immediately
    setTimeout(() => {
      inputRef.current?.select();
    }, 50);
  };

  const handleInputChange = (val: string) => {
    setSearchQuery(val);
    setIsOpen(true);
  };

  const handleChevronClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (loading) return;
    if (isOpen) {
      setIsOpen(false);
      setIsFocused(false);
      inputRef.current?.blur();
    } else {
      inputRef.current?.focus();
    }
  };

  const clearSelection = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange("");
    setSearchQuery("");
    inputRef.current?.focus();
  };

  return (
    <div className="search-wrap" ref={containerRef}>
      <span className="search-label">🔍 Tìm ngành học</span>
      <div className={`modern-search-box${isFocused ? " focused" : ""}${loading ? " disabled" : ""}`}>
        {/* Left Search Icon */}
        <span className="modern-search-icon">🔍</span>

        {/* Input combobox */}
        <input
          ref={inputRef}
          type="text"
          className="modern-search-input"
          placeholder={loading ? "Đang tải danh sách ngành..." : "Tìm mã xét tuyển, tên ngành hoặc khoa..."}
          value={searchQuery}
          onChange={(e) => handleInputChange(e.target.value)}
          onFocus={handleInputFocus}
          disabled={loading}
          autoComplete="off"
        />

        {/* Action Buttons: Clear selection + Dropdown Arrow */}
        <div className="modern-actions-wrap">
          {value && (
            <button
              type="button"
              className="modern-clear-btn"
              onClick={clearSelection}
              title="Xoá lựa chọn"
            >
              ✕
            </button>
          )}
          <button
            type="button"
            className={`modern-arrow-btn${isOpen ? " open" : ""}`}
            onClick={handleChevronClick}
            disabled={loading}
          >
            ▼
          </button>
        </div>

        {/* Floating Dropdown Panel */}
        {isOpen && !loading && (
          <div className="modern-dropdown-panel">
            <ul className="modern-options-list">
              {filteredOptions.length === 0 ? (
                <li className="modern-no-options">
                  <span style={{ fontSize: "1.2rem", display: "block", marginBottom: "4px" }}>🔍</span>
                  Không tìm thấy ngành nào phù hợp
                </li>
              ) : (
                filteredOptions.map((m) => {
                  const isSelected = m.id === value;
                  return (
                    <li
                      key={m.id}
                      className={`modern-option-item${isSelected ? " selected" : ""}`}
                      onClick={() => handleSelect(m)}
                    >
                      <div className="option-info">
                        <span className="option-code">{m.major_code}</span>
                        <span className="option-name">{m.major_name}</span>
                      </div>
                      {m.school && <span className="option-tag">{m.school}</span>}
                    </li>
                  );
                })
              )}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
