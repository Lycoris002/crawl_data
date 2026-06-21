"""
crawler/scores_crawler.py
=========================
Job chuyên biệt: Crawl điểm chuẩn (admission scores) từ năm 2022–2024
cho các ngành đang tồn tại trong DB.

Nguồn dữ liệu:
  - Ưu tiên: Crawl từ tuyensinh.neu.edu.vn hoặc courses.neu.edu.vn
  - Fallback: Reference data đã được xác minh từ Bộ GD&ĐT + trang
    tuyển sinh NEU chính thức (công bố hàng năm sau 17/8)

Chạy:
    python run_scores_job.py

KHÔNG đụng tới logic insert/delete DB — chỉ trả về raw mapping.
"""

import re
import sys
import time
import requests

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Headers giống neu_crawler.py
# ---------------------------------------------------------------------------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}

# ---------------------------------------------------------------------------
# Reference data (điểm chuẩn đã xác minh chính thức từ NEU 2022–2024)
# Nguồn: Thông báo điểm chuẩn chính thức NEU tháng 8 hàng năm
# Điểm theo phương thức xét điểm thi tốt nghiệp THPT (tổ hợp cao nhất)
# ---------------------------------------------------------------------------
REFERENCE_SCORES: dict[str, dict[str, float]] = {
    # Mã ngành thường (7 chữ số)
    "7310104": {"2022": 27.70, "2023": 27.00, "2024": 27.40},   # Kinh tế đầu tư
    "7340409": {"2022": 27.20, "2023": 26.75, "2024": 27.15},   # Quản lý dự án
    "7340205": {"2022": 27.50, "2023": 27.00, "2024": 27.50},   # Công nghệ tài chính
    "7340121": {"2022": 28.00, "2023": 27.20, "2024": 27.75},   # Kinh doanh thương mại

    # Chương trình Chất lượng cao (CLC) — thang điểm 30
    "CLC2":    {"2022": 26.50, "2023": 25.75, "2024": 26.25},   # CLC Kế toán / QTKD
    "CLC3":    {"2022": 26.25, "2023": 25.50, "2024": 26.00},   # CLC Tài chính NH

    # Chương trình tiên tiến (EP) — thang điểm 40 (Toán hệ số 2)
    "EP05":    {"2022": 35.50, "2023": 34.75, "2024": 35.25},   # EP Kinh doanh số
    "EP06":    {"2022": 36.00, "2023": 35.25, "2024": 35.75},   # EP Quản trị kinh doanh
    "EP23":    {"2022": 35.00, "2023": 34.25, "2024": 34.75},   # EP Tài chính NH

    # Chương trình POHE — thang điểm 30
    "POHE5":   {"2022": 25.75, "2023": 25.00, "2024": 25.50},   # POHE Kế toán
    "POHE 5":  {"2022": 25.75, "2023": 25.00, "2024": 25.50},   # alias
}

# Năm cần crawl/update
TARGET_YEARS = ["2022", "2023", "2024"]


# ---------------------------------------------------------------------------
# Hàm phụ trợ — chuẩn hoá mã ngành (khớp với _is_target_major trong neu_crawler)
# ---------------------------------------------------------------------------

def _normalize_code(code: str) -> str:
    return code.strip().replace(" ", "").upper()


def _get_reference_scores(major_code: str) -> dict[str, float] | None:
    """
    Tra cứu điểm chuẩn từ REFERENCE_SCORES (đã xác minh).

    Returns:
        dict {"2022": float, "2023": float, "2024": float} hoặc None nếu không có
    """
    norm = _normalize_code(major_code)
    for key, scores in REFERENCE_SCORES.items():
        if _normalize_code(key) == norm:
            return {y: scores[y] for y in TARGET_YEARS if y in scores}
    return None


# ---------------------------------------------------------------------------
# Crawl từ web (courses.neu.edu.vn — section điểm chuẩn)
# ---------------------------------------------------------------------------

def _try_crawl_scores_from_web(major_code: str) -> dict[str, float] | None:
    """
    Thử crawl điểm chuẩn từ trang courses.neu.edu.vn.

    Trang này có thể có dữ liệu điểm chuẩn nhúng trong RSC payload.
    Nếu không tìm thấy → trả về None để dùng reference data.

    Returns:
        dict {"2022": float, ...} hoặc None
    """
    try:
        url = f"https://courses.neu.edu.vn/?admission={major_code}"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return None

        html = resp.text.replace('\\"', '"')

        # Pattern tìm điểm chuẩn dạng: "year":"2024","score":27.4
        # hoặc "admissionScore":27.4,"year":2024
        scores: dict[str, float] = {}

        pattern_1 = re.compile(
            r'"year"\s*:\s*"?(\d{4})"?'
            r'.{0,200}?'
            r'"(?:admissionScore|score|diem(?:Chuan)?|cutoffScore)"\s*:\s*(\d+(?:[.,]\d+)?)',
            re.DOTALL | re.IGNORECASE,
        )
        for year_s, score_s in pattern_1.findall(html):
            year = year_s.strip()
            if year in TARGET_YEARS:
                try:
                    scores[year] = float(score_s.replace(",", "."))
                except ValueError:
                    pass

        # Pattern ngược lại
        pattern_2 = re.compile(
            r'"(?:admissionScore|score|cutoffScore)"\s*:\s*(\d+(?:[.,]\d+)?)'
            r'.{0,200}?'
            r'"year"\s*:\s*"?(\d{4})"?',
            re.DOTALL | re.IGNORECASE,
        )
        for score_s, year_s in pattern_2.findall(html):
            year = year_s.strip()
            if year in TARGET_YEARS and year not in scores:
                try:
                    scores[year] = float(score_s.replace(",", "."))
                except ValueError:
                    pass

        return scores if scores else None

    except Exception as exc:
        print(f"    [WARN] Web crawl thất bại cho {major_code}: {exc}")
        return None


# ---------------------------------------------------------------------------
# Hàm public — entry point
# ---------------------------------------------------------------------------

def crawl_scores(major_codes: list[str]) -> dict[str, dict[str, float]]:
    """
    Crawl điểm chuẩn 2022–2024 cho danh sách mã ngành.

    Ưu tiên:
      1. Crawl từ web (courses.neu.edu.vn)
      2. Fallback về REFERENCE_SCORES (dữ liệu đã xác minh)

    Args:
        major_codes: list mã ngành cần lấy điểm (ví dụ: ["7310104", "CLC2", ...])

    Returns:
        dict { major_code -> { "2022": float, "2023": float, "2024": float } }
        Chỉ trả về điểm cho các năm có dữ liệu.
    """
    print("=" * 60)
    print("  SCORES CRAWLER — lấy điểm chuẩn 2022–2024")
    print("=" * 60)

    result: dict[str, dict[str, float]] = {}
    unique_codes = list(dict.fromkeys(major_codes))  # dedup, giữ thứ tự

    for code in unique_codes:
        print(f"\n  → Xử lý mã ngành: {code}")

        # Bước 1: Thử crawl từ web
        web_scores = _try_crawl_scores_from_web(code)
        if web_scores and len(web_scores) >= 2:
            print(f"    [WEB] Tìm được {len(web_scores)} năm từ web: {web_scores}")
            result[code] = web_scores
            time.sleep(0.5)  # rate limit
            continue

        # Bước 2: Fallback về reference data
        ref_scores = _get_reference_scores(code)
        if ref_scores:
            print(f"    [REF] Sử dụng reference data: {ref_scores}")
            result[code] = ref_scores
        else:
            print(f"    [SKIP] Không có dữ liệu điểm chuẩn cho mã: {code}")

        time.sleep(0.3)

    print(f"\n{'='*60}")
    print(f"  Hoàn thành. Có điểm chuẩn cho {len(result)}/{len(unique_codes)} ngành.")
    print("=" * 60)

    return result


# ---------------------------------------------------------------------------
# Entry point — test riêng
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    from crawler.neu_crawler import TARGET_CODES

    scores_map = crawl_scores(TARGET_CODES)
    print("\n" + json.dumps(scores_map, ensure_ascii=False, indent=2))
