"use client";

import { useState } from "react";
import { Semester } from "../lib/api";

interface CurriculumTabProps {
  curriculum: Semester[];
}

function Expander({
  title,
  defaultOpen,
  children,
}: {
  title: string;
  defaultOpen: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="expander">
      <button className="expander-header" onClick={() => setOpen((o) => !o)}>
        <span>{title}</span>
        <span className={`expander-icon${open ? " open" : ""}`}>▼</span>
      </button>
      {open && <div className="expander-body">{children}</div>}
    </div>
  );
}

export default function CurriculumTab({ curriculum }: CurriculumTabProps) {
  if (!curriculum || curriculum.length === 0) {
    return (
      <div className="alert alert-info">
        ℹ️ Hệ thống đang thu thập chi tiết môn học cho ngành này. Vui lòng quay lại sau!
      </div>
    );
  }

  return (
    <div>
      <h3 className="section-title">🗺️ Chương trình đào tạo</h3>
      {curriculum.map((sem, idx) => {
        const semNum = sem.semester ?? sem.year ?? idx + 1;
        const subjects = sem.subjects ?? [];
        return (
          <Expander
            key={idx}
            title={`📌  Học kỳ ${semNum} – ${subjects.length} môn học`}
            defaultOpen={idx === 0}
          >
            {subjects.length === 0 ? (
              <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
                Chưa có môn học nào.
              </p>
            ) : (
              <table className="subject-table">
                <thead>
                  <tr>
                    <th className="row-num">#</th>
                    <th>Mã môn</th>
                    <th>Tên môn học</th>
                    <th style={{ textAlign: "center" }}>Tín chỉ</th>
                  </tr>
                </thead>
                <tbody>
                  {subjects.map((subj, i) => (
                    <tr key={i}>
                      <td className="row-num">{i + 1}</td>
                      <td className="col-code">{subj.code || "—"}</td>
                      <td>{subj.name}</td>
                      <td className="col-credits">{subj.credits ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Expander>
        );
      })}
    </div>
  );
}
