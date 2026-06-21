import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NEU Course Explorer – Tra cứu điểm chuẩn & lộ trình đào tạo",
  description:
    "Tra cứu điểm chuẩn và lộ trình đào tạo của Đại học Kinh tế Quốc dân (NEU). Cập nhật mới nhất các ngành học, chương trình đào tạo và điểm chuẩn tuyển sinh.",
  keywords: ["NEU", "Kinh tế Quốc dân", "điểm chuẩn", "chương trình đào tạo", "tuyển sinh"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" data-theme="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
