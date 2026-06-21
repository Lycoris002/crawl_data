"use client";

import { MajorDetail } from "../lib/api";

interface MajorCardProps {
  detail: MajorDetail;
}

export default function MajorCard({ detail }: MajorCardProps) {
  return (
    <div className="glass-card">
      <h2 className="major-name">
        {detail.major_name || "Chưa có tên"}
        {detail.school && <span className="school-tag">{detail.school}</span>}
      </h2>
      <p className="major-code">
        🏷️ Mã xét tuyển:{" "}
        <span>{detail.major_code || "N/A"}</span>
      </p>
    </div>
  );
}
