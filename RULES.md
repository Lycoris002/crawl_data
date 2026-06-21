# QUY TẮC PHÁT TRIỂN — NEU Curriculum Explorer

> Tài liệu này định nghĩa các nguyên tắc bắt buộc khi làm việc với codebase.  
> **Mọi thay đổi phải tuân theo các quy tắc này.**

---

## 1. Nguyên tắc Phân tầng (Bất khả xâm phạm)

Hệ thống chia làm **3 tầng độc lập**. Mỗi tầng **chỉ làm đúng 1 việc**:

| Tầng | File | Việc được làm | Việc CẤM làm |
|------|------|--------------|--------------|
| **Crawler** | `crawler/neu_crawler.py` | Fetch HTML, parse, trả về `list[dict]` | ❌ Không được import `pymongo`, không được ghi DB, không được import từ `db/` hay `backend/` |
| **DB Layer** | `db/database.py` | Kết nối MongoDB, đọc/ghi collection | ❌ Không được gọi HTTP request, không được import từ `crawler/` hay `backend/` |
| **API Layer** | `backend/api.py` | Định nghĩa routes, gọi crawler + db | ❌ Không được viết logic crawl hay query MongoDB trực tiếp — phải gọi qua hàm của 2 tầng trên |

> **Lý do:** Khi cần thay MongoDB bằng PostgreSQL, chỉ sửa `db/database.py`.  
> Khi NEU đổi cấu trúc website, chỉ sửa `crawler/neu_crawler.py`.  
> Không có gì ảnh hưởng nhau.

---

## 2. Quy tắc Crawler

### 2.1 Hàm public duy nhất
```python
# ĐÚNG — crawler chỉ expose 1 hàm public
def crawl_neu_data() -> list:
    ...
    return all_majors  # list[dict]
```
Các hàm `_fetch_*`, `_parse_*`, `_build_*` đều là **private** (prefix `_`), không được gọi trực tiếp từ ngoài crawler.

### 2.2 Kỹ thuật parse HTML của NEU
- NEU dùng **Next.js App Router (RSC)** — data nhúng trong HTML dưới dạng **double-escaped JSON**
- Bước unescape bắt buộc: `html.replace('\\"', '"')` trước khi regex
- Field cần extract: `"semester"`, `"name"`, `"subjectCode"`, `"credits"`
- **Không dùng** `courseCode` (field này không tồn tại sau unescape)
- **Không dùng** BeautifulSoup hay Selenium — `requests` + `re` là đủ

### 2.3 Cấu trúc data trả về
```python
{
    "id":         str,   # f"{major_code}_{year_label}", e.g. "7340121_2025"
    "school":     str,   # "NEU"
    "major_code": str,   # mã xét tuyển, e.g. "7340121"
    "major_name": str,   # tên ngành + năm, e.g. "Kinh doanh thương mại (2025)"
    "slug":       str,   # slug từ URL, e.g. "kinh-doanh-thuong-mai-K677340121"
    "scores":     dict,  # {"2024": 26.0} — cập nhật thực khi có nguồn
    "year_label": str,   # "2025" hoặc "2026"
    "curriculum": [
        {
            "semester": int,       # học kỳ thực (1–8), KHÔNG phải năm học
            "subjects": [
                {"code": str, "name": str, "credits": int}
            ]
        }
    ]
}
```

> ⚠️ **Quan trọng:** Field là `"semester"` (học kỳ), **KHÔNG** phải `"year"` (năm).  
> Một ngành có 8 học kỳ = 4 năm × 2 học kỳ/năm.

### 2.4 Xử lý data tĩnh
- Nếu một ngành **không crawl được** (Next.js render client-side hoàn toàn), mới được hardcode data tĩnh
- Data tĩnh phải được đặt ở **đầu file**, được comment rõ lý do và ngày kiểm tra lần cuối
- Ưu tiên tìm cách crawl được thay vì hardcode

---

## 3. Quy tắc DB Layer

### 3.1 Hàm public
```python
insert_majors(data: list) -> int      # xóa cũ + insert mới, trả về số bản ghi
search_majors(query: str = "") -> list # tìm kiếm theo mã/tên
get_major_by_id(major_id: str) -> dict | None
```

### 3.2 Chiến lược sync
- `insert_majors` luôn thực hiện **delete_many({}) trước insert_many()**
- Lý do: tránh duplicate, đảm bảo data luôn là bản mới nhất
- Nếu sau này cần giữ history → thêm field `synced_at` và dùng `upsert` theo `id`

### 3.3 Cấu hình kết nối
- MongoDB URI **bắt buộc** lấy từ `.env`, không bao giờ hardcode trong code
- Biến môi trường: `MONGODB_URI`, `DB_NAME`, `COLLECTION_NAME`
- Nếu thiếu `MONGODB_URI` → raise `EnvironmentError` rõ ràng, không silent fail

---

## 4. Quy tắc API Layer

### 4.1 Route hiện tại
```
POST /api/sync             → trigger crawl + insert
GET  /api/search?query=    → dropdown suggestions
GET  /api/curriculum/{id}  → chi tiết 1 ngành
```

### 4.2 Error handling
- Mọi route phải có `try/except`
- `EnvironmentError` → HTTP 500 với message rõ ràng
- `404` khi không tìm thấy ngành → không trả 200 với body rỗng

### 4.3 Không viết logic trong route
```python
# SAI ❌ — logic crawl trong route
@app.post("/api/sync")
def sync():
    r = requests.get("https://courses.neu.edu.vn/...")
    # parse HTML...
    client = MongoClient(...)  # kết nối DB trực tiếp trong route

# ĐÚNG ✅ — route chỉ orchestrate
@app.post("/api/sync")
def sync():
    data = crawl_neu_data()
    count = insert_majors(data)
    return {"count": count}
```

---

## 5. Quy tắc Data & Schema

### 5.1 ID document
- Format: `"{major_code}_{year_label}"` — ví dụ: `"7340121_2025"`, `"POHE5_2026"`
- ID phải **unique** trong collection
- Không dùng MongoDB `_id` tự sinh cho logic nghiệp vụ

### 5.2 Ngành mục tiêu cần crawl
```python
TARGET_CODES = [
    "7310104",  # Hệ thống thông tin quản lý
    "7340409",  # Marketing
    "CLC2",     # Chất lượng cao 2
    "CLC3",     # Chất lượng cao 3
    "EP06",     # Chương trình EP06
    "EP23",     # Chương trình EP23
    "7340205",  # Kinh doanh quốc tế
    "POHE5",    # Chương trình POHE5
    "EP05",     # Chương trình EP05
    "7340121",  # Kinh doanh thương mại
]
```
Khi thêm ngành mới → cập nhật danh sách này trong `neu_crawler.py`.

### 5.3 Năm học cần crawl
Hiện tại crawl 2 năm tuyển sinh gần nhất. Khi có năm mới → thêm vào `YEARS_CONFIG` trong `neu_crawler.py`.

---

## 6. Quy tắc Frontend (app.py)

### 6.1 Không gọi DB trực tiếp
- `app.py` **chỉ** gọi API qua HTTP (`requests.get/post`)
- Không được import `pymongo` hay `crawler` trong `app.py`

### 6.2 Hiển thị curriculum
- Accordion phân theo **học kỳ** (dùng `item["semester"]`), không phải năm học
- Label: `"Học kỳ 1"`, `"Học kỳ 2"`, ..., `"Học kỳ 8"`

> ⚠️ **TODO:** `app.py` hiện đang dùng `year_data['year']` — cần update thành `year_data['semester']` sau khi data schema mới được đồng bộ vào DB.

### 6.3 Cache
- `fetch_search_options` có `@st.cache_data(ttl=60)` — đủ cho MVP
- Sau khi sync data thành công → clear cache: `fetch_search_options.clear()`

---

## 7. Quy tắc File & Thư mục

| Thư mục | Mục đích | Được commit? |
|---------|---------|-------------|
| `crawler/` | Code crawler | ✅ Có |
| `db/` | Code DB + mock data | ✅ Có |
| `backend/` | FastAPI routes | ✅ Có |
| `scratch/` | Scripts thử nghiệm, probe, debug | ❌ Không (gitignore) |
| `.env` | Credentials | ❌ Không (gitignore) |

---

## 8. Quy tắc môi trường

### `.env` bắt buộc có
```env
MONGODB_URI=mongodb+srv://...
DB_NAME=neu_courses_db
COLLECTION_NAME=majors
```

### Load .env
- Mọi file cần env var đều tự load `.env` từ **project root**:
```python
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
```
- **Không hardcode** bất kỳ credential nào trong code

---

## 9. Naming Convention

| Loại | Convention | Ví dụ |
|------|------------|-------|
| File | `snake_case.py` | `neu_crawler.py`, `database.py` |
| Hàm public | `snake_case` | `crawl_neu_data()`, `insert_majors()` |
| Hàm private | `_snake_case` | `_fetch_curriculum()`, `_parse_curriculum_from_html()` |
| Constant | `UPPER_CASE` | `HEADERS`, `TARGET_CODES`, `YEARS_CONFIG` |
| MongoDB field | `snake_case` | `major_code`, `year_label`, `subject_code` |

---

## 10. Checklist trước khi commit

- [ ] Crawler không import từ `db/` hoặc `backend/`
- [ ] DB layer không import từ `crawler/`  
- [ ] API routes không chứa logic crawl hoặc query MongoDB trực tiếp
- [ ] `.env` không bị commit
- [ ] Không còn data hardcode mà lẽ ra có thể crawl được
- [ ] `curriculum[].semester` được dùng thay vì `curriculum[].year`
- [ ] Mọi exception được catch và trả về HTTP error rõ ràng
