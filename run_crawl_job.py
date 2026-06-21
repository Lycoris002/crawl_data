"""
run_crawl_job.py
================
Job thủ công: crawl dữ liệu NEU rồi insert vào MongoDB.

Chạy:
    python run_crawl_job.py

Cấu hình ngành cần crawl nằm trong crawler/neu_crawler.py (TARGET_CODES).
Cấu hình DB nằm trong .env (MONGODB_URI, DB_NAME, COLLECTION_NAME).
"""

import sys
import time

# Fix terminal encoding cho Windows
sys.stdout.reconfigure(encoding="utf-8")

from crawler.neu_crawler import crawl_neu_data
from db.database import insert_majors


def main():
    print("=" * 60)
    print("  NEU CRAWL JOB — bắt đầu")
    print("=" * 60)

    t0 = time.time()

    # ---- Bước 1: Crawl ------------------------------------------------
    print("\n[1/2] Crawling dữ liệu từ courses.neu.edu.vn ...")
    try:
        data = crawl_neu_data()
    except Exception as e:
        print(f"\n[ERROR] Crawl thất bại: {e}")
        sys.exit(1)

    if not data:
        print("\n[WARN] Crawler không trả về dữ liệu. Kiểm tra lại TARGET_CODES.")
        sys.exit(0)

    # ---- Bước 2: Insert vào DB ----------------------------------------
    print(f"\n[2/2] Inserting {len(data)} ngành vào MongoDB ...")
    try:
        inserted = insert_majors(data)
    except Exception as e:
        print(f"\n[ERROR] Insert DB thất bại: {e}")
        sys.exit(1)

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"  ✅  Hoàn thành! Đã insert {inserted} bản ghi ({elapsed:.1f}s)")
    print("=" * 60)


if __name__ == "__main__":
    main()
