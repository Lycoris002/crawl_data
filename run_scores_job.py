"""
run_scores_job.py
=================
Job lấy điểm chuẩn 2022–2026 cho CÁC NGÀNH ĐANG TỒN TẠI trong DB
và cập nhật (merge) vào field "scores" của từng document.

  ✅ KHÔNG xóa curriculum hay dữ liệu khác
  ✅ KHÔNG xóa điểm chuẩn các năm đã có trước đó
  ✅ Tự động đọc danh sách ngành từ DB (không cần cấu hình thủ công)

Chạy:
    python run_scores_job.py

Cấu hình DB nằm trong .env (MONGODB_URI, DB_NAME, COLLECTION_NAME).
"""

import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

from crawler.scores_crawler import crawl_scores
from db.database import get_all_major_codes, update_scores_for_major


def main():
    print("=" * 60)
    print("  SCORES JOB — Cập nhật điểm chuẩn 2022–2026")
    print("=" * 60)

    t0 = time.time()

    # ---- Bước 1: Lấy danh sách ngành từ DB ----------------------------
    print("\n[1/3] Đọc danh sách ngành từ MongoDB...")
    try:
        majors = get_all_major_codes()
    except Exception as e:
        print(f"\n[ERROR] Không đọc được DB: {e}")
        sys.exit(1)

    if not majors:
        print("\n[WARN] DB rỗng. Hãy chạy run_crawl_job.py trước để import ngành.")
        sys.exit(0)

    print(f"  Tìm thấy {len(majors)} ngành trong DB:")
    for m in majors:
        print(f"    - {m['id']}  (mã: {m['major_code']})")

    # ---- Bước 2: Crawl điểm chuẩn -------------------------------------
    print("\n[2/3] Crawling điểm chuẩn từ nguồn dữ liệu...")
    all_codes = [m["major_code"] for m in majors]
    try:
        scores_map = crawl_scores(all_codes)
    except Exception as e:
        print(f"\n[ERROR] Crawl điểm chuẩn thất bại: {e}")
        sys.exit(1)

    if not scores_map:
        print("\n[WARN] Crawler không trả về điểm chuẩn nào.")
        sys.exit(0)

    # ---- Bước 3: Update vào DB ----------------------------------------
    print("\n[3/3] Cập nhật điểm chuẩn vào MongoDB...")

    updated = 0
    skipped = 0
    failed  = 0

    for major in majors:
        major_id   = major["id"]
        major_code = major["major_code"]

        new_scores = scores_map.get(major_code)
        if not new_scores:
            print(f"  [SKIP] {major_id} — không có điểm chuẩn mới")
            skipped += 1
            continue

        try:
            ok = update_scores_for_major(major_id, new_scores)
            if ok:
                years_str = ", ".join(
                    f"{y}: {v}" for y, v in sorted(new_scores.items())
                )
                print(f"  [OK]   {major_id} — cập nhật: {{{years_str}}}")
                updated += 1
            else:
                print(f"  [MISS] {major_id} — không tìm thấy document trong DB")
                failed += 1
        except Exception as e:
            print(f"  [ERR]  {major_id} — lỗi: {e}")
            failed += 1

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"  ✅  Hoàn thành! ({elapsed:.1f}s)")
    print(f"      Đã cập nhật : {updated} ngành")
    print(f"      Bỏ qua      : {skipped} ngành (không có dữ liệu mới)")
    print(f"      Thất bại    : {failed} ngành")
    print("=" * 60)


if __name__ == "__main__":
    main()
