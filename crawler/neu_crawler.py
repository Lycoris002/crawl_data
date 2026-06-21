import requests
import re
import sys

# Fix terminal encoding
sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------------------------------------------------------
# Cấu hình crawl
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

YEARS_CONFIG = [
    {
        "label":     "2025",
        "list_url":  "https://courses.neu.edu.vn/?year=K67%20-%202025",
        "year_param": "K67%20-%202025",
    },
    {
        "label":     "2026",
        "list_url":  "https://courses.neu.edu.vn/?year=K68%20-%202026",
        "year_param": "K68%20-%202026",
    },
]

TARGET_CODES = [
    "7310104", "7340409", "CLC2", "CLC3",
    "EP06", "EP23", "7340205",
    "POHE5", "POHE 5", "EP05", "7340121",
]


# ---------------------------------------------------------------------------
# Hàm phụ trợ
# ---------------------------------------------------------------------------

def _is_target_major(code: str) -> bool:
    norm = code.strip().replace(" ", "").upper()
    return any(t.replace(" ", "").upper() == norm for t in TARGET_CODES)


def _parse_curriculum_from_html(html: str) -> dict:
    """
    Parse chương trình đào tạo từ HTML của NEU.

    Next.js nhúng dữ liệu dạng RSC payload bên trong HTML với chuỗi
    bị double-escape (\\\" thay vì \"). Sau khi unescape, ta có thể
    dùng regex để extract các trường: semester, name, subjectCode, credits.

    Returns:
        dict { semester_number (int) -> list[{"code", "name", "credits"}] }
    """
    # Bước 1: Unescape lớp double-escape của Next.js
    unescaped = html.replace('\\"', '"')

    # Bước 2: Regex tìm từng subject entry trong curriculum
    # Pattern từ HTML thực tế:
    # "semester":5,...,"name":"Tên môn","subjectCode":"TMQT1133","credits":3
    subject_pattern = re.compile(
        r'"semester"\s*:\s*(\d+)'       # (1) số học kỳ
        r'.{1,1500}?'                   # nội dung ở giữa (lazy)
        r'"name"\s*:\s*"([^"]+)"'       # (2) tên môn học
        r'.{0,300}?'
        r'"subjectCode"\s*:\s*"([^"]+)"'# (3) mã môn học
        r'.{0,100}?'
        r'"credits"\s*:\s*(\d+)',        # (4) số tín chỉ
        re.DOTALL,
    )

    by_semester: dict = {}
    seen = set()  # tránh duplicate: (semester, code)

    for sem_s, name, code, cred_s in subject_pattern.findall(unescaped):
        sem  = int(sem_s)
        cred = int(cred_s)
        key  = (sem, code)
        if key in seen:
            continue
        seen.add(key)

        by_semester.setdefault(sem, []).append({
            "code":    code,
            "name":    name,
            "credits": cred,
        })

    return by_semester


def _fetch_majors_for_year(year_cfg: dict) -> dict:
    """
    Lấy danh sách ngành từ trang chủ NEU theo năm.
    Returns: { slug -> {id, school, major_code, major_name, slug, year_label} }
    """
    print(f"\n--- Fetching major list for year: {year_cfg['label']} ---")
    r = requests.get(year_cfg["list_url"], headers=HEADERS, timeout=30)
    clean = r.text.replace('\\"', '"')

    pattern = r'"attributes":\{(.*?)\}'

    majors_map = {}
    for m in re.finditer(pattern, clean, re.DOTALL):
        chunk = m.group(1)
        name_m  = re.search(r'"name"\s*:\s*"([^"]+)"', chunk)
        slug_m  = re.search(r'"slug"\s*:\s*"([^"]+)"', chunk)
        admit_m = re.search(r'"admissionCode"\s*:\s*"([^"]+)"', chunk)
        major_m = re.search(r'"majorCode"\s*:\s*"([^"]+)"', chunk)

        if not (name_m and slug_m):
            continue

        code = (admit_m.group(1) if admit_m else
                major_m.group(1) if major_m else "")

        if not code or not _is_target_major(code):
            continue

        slug = slug_m.group(1)
        year_label = year_cfg["label"]

        majors_map[slug] = {
            "id":         f"{code}_{year_label}",
            "school":     "NEU",
            "major_code": code,
            "major_name": f"{name_m.group(1)} ({year_label})",
            "slug":       slug,
            "scores":     {"2024": 26.0},
            "year_label": year_label,
        }

    print(f"  Found {len(majors_map)} target majors for {year_cfg['label']}.")
    return majors_map


def _fetch_curriculum(slug: str, major_code: str, year_cfg: dict) -> dict:
    """
    Crawl chương trình đào tạo chi tiết của một ngành.

    Returns:
        dict { semester_int -> list[subject] }
    """
    url = (
        f"https://courses.neu.edu.vn/curriculum/{slug}"
        f"?year={year_cfg['year_param']}"
        f"&admission={major_code}"
    )
    print(f"       GET {url}")
    r = requests.get(url, headers=HEADERS, timeout=30)

    by_semester = _parse_curriculum_from_html(r.text)

    total = sum(len(v) for v in by_semester.values())
    print(f"       -> {total} môn, {len(by_semester)} học kỳ")
    return by_semester


def _build_curriculum_list(by_semester: dict) -> list:
    """
    Chuyển dict {semester -> [subjects]} thành list có thứ tự theo học kỳ.

    Returns:
        [{"semester": int, "subjects": [...]}, ...]
    """
    return [
        {"semester": sem, "subjects": subjects}
        for sem, subjects in sorted(by_semester.items())
    ]


# ---------------------------------------------------------------------------
# Hàm public: chỉ crawl, trả về raw data — KHÔNG đụng tới DB
# ---------------------------------------------------------------------------

def crawl_neu_data() -> list:
    """
    Crawl toàn bộ dữ liệu chương trình đào tạo NEU từ courses.neu.edu.vn.

    Kỹ thuật:
        - Trang NEU dùng Next.js App Router / RSC: dữ liệu nằm trong HTML
          dưới dạng chuỗi double-escaped JSON payload.
        - Sau khi unescape, regex extract được semester, subjectCode, name, credits.

    Returns:
        list[dict] — mỗi phần tử:
        {
            "id":         str,   # e.g. "7340121_2025"
            "school":     str,   # "NEU"
            "major_code": str,
            "major_name": str,
            "slug":       str,
            "scores":     dict,
            "year_label": str,
            "curriculum": [
                {
                    "semester": int,
                    "subjects": [{"code": str, "name": str, "credits": int}]
                }
            ]
        }
    """
    print("=" * 60)
    print("NEU Crawler — bắt đầu crawl dữ liệu...")
    print("=" * 60)

    all_majors = []

    for year_cfg in YEARS_CONFIG:
        majors_map = _fetch_majors_for_year(year_cfg)
        
        # Cache curriculum theo tên gốc của ngành trong cùng một năm
        # Key: base_name, Value: curriculum list
        curriculum_cache = {}

        for slug, major_info in majors_map.items():
            print(f"\n  -> {major_info['major_name']} | slug={slug}")

            # Extract base name by removing " (year_label)" from major_name
            # e.g., "Kinh tế đầu tư (2025)" -> "kinh tế đầu tư"
            base_name = major_info["major_name"].rsplit(" (", 1)[0].strip().lower()

            if base_name in curriculum_cache:
                print(f"       -> [CACHE] Dùng lại chương trình đào tạo từ ngành trùng tên: {base_name}")
                curriculum = curriculum_cache[base_name]
            else:
                by_semester    = _fetch_curriculum(slug, major_info["major_code"], year_cfg)
                curriculum     = _build_curriculum_list(by_semester)
                curriculum_cache[base_name] = curriculum

            major_info["curriculum"] = curriculum
            all_majors.append(major_info)

    print(f"\n{'='*60}")
    print(f"Crawl hoàn thành. Tổng số ngành: {len(all_majors)}")
    print("=" * 60)
    return all_majors


# ---------------------------------------------------------------------------
# Entry point — để test riêng crawler (không insert DB)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    data = crawl_neu_data()
    print("\n" + json.dumps(data, ensure_ascii=False, indent=2))
