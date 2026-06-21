"use client";

interface OutcomesTabProps {
  summary?: string;
}

export default function OutcomesTab({ summary }: OutcomesTabProps) {
  return (
    <div className="tab-pane active" id="outcomes-pane" style={{ animation: "fadeIn 0.3s ease-out" }}>
      <h3 style={{ marginBottom: "1rem", color: "var(--text-primary)" }}>🎯 Chuẩn đầu ra chương trình</h3>
      
      {!summary ? (
        <div className="alert alert-warning">
          ⏳ Đang cập nhật dữ liệu tóm tắt chuẩn đầu ra...
        </div>
      ) : (
        <div 
          style={{ 
            padding: "20px", 
            borderRadius: "12px", 
            background: "var(--bg-card)",
            border: "1px solid var(--border-color)",
            lineHeight: "1.6",
            color: "var(--text-secondary)",
            fontSize: "1rem"
          }}
        >
          {summary.split('\n').map((paragraph, index) => (
            <p key={index} style={{ marginBottom: index !== summary.split('\n').length - 1 ? "1rem" : 0 }}>
              {paragraph}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
