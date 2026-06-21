# KIẾN TRÚC HỆ THỐNG — NEU Curriculum Explorer

> **Phiên bản:** 2.0 | **Cập nhật:** 2026-06-21

---

## 1. Mục tiêu & Nghiệp vụ

### Bài toán
Sinh viên và phụ huynh muốn tra cứu **chương trình đào tạo** (lộ trình học theo từng học kỳ, danh sách môn, số tín chỉ) và **điểm chuẩn** các ngành của trường **Đại học Kinh tế Quốc dân (NEU)** — nhưng website chính thức của trường (courses.neu.edu.vn) render bằng Next.js RSC, chậm và khó điều hướng.

### Giải pháp
Xây dựng hệ thống **thu thập dữ liệu định kỳ** (crawler) → **lưu vào DB** → **phục vụ qua API** → **hiển thị giao diện thân thiện** dưới dạng web app.

### Người dùng mục tiêu
- Học sinh THPT đang xem xét ngành học tại NEU
- Sinh viên NEU muốn tra cứu lộ trình học
- Phụ huynh nghiên cứu điểm chuẩn

---

## 2. Kiến trúc Tổng quan

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA PIPELINE                            │
│                                                             │
│  courses.neu.edu.vn  ──►  crawler/neu_crawler.py           │
│  (Next.js RSC site)         (HTTP GET + regex parse)        │
│                                    │                        │
│                                    ▼                        │
│                             db/database.py                  │
│                             (insert_majors)                 │
│                                    │                        │
│                                    ▼                        │
│                          MongoDB Atlas (Cloud)              │
└─────────────────────────────────────────────────────────────┘
                                     │
                                     │ (pymongo read)
                                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND API                              │
│                                                             │
│              backend/api.py (FastAPI)                       │
│                                                             │
│   POST /api/sync        → trigger crawl + insert            │
│   GET  /api/search      → tìm kiếm ngành (dropdown)        │
│   GET  /api/curriculum/{id} → chi tiết 1 ngành             │
└─────────────────────────────────────────────────────────────┘
                                     │
                                     │ (HTTP REST)
                                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND                                 │
│                                                             │
│                  app.py (Streamlit)                         │
│                                                             │
│   - Dropdown tìm kiếm ngành                                 │
│   - Tab điểm chuẩn (chart + metric)                        │
│   - Tab lộ trình học (accordion theo học kỳ)               │
│   - Sidebar: nút Sync data (admin)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Cấu trúc File

```
Crawl_data/
├── .env                        # Biến môi trường (MONGODB_URI, DB_NAME, ...)
├── app.py                      # Frontend Streamlit
│
├── crawler/
│   └── neu_crawler.py          # Crawler: CHỈ crawl, trả về raw data list
│
├── db/
│   ├── database.py             # DB layer: CHỈ tương tác MongoDB
│   └── data.json               # Mock data tĩnh (backup/testing)
│
├── backend/
│   └── api.py                  # FastAPI: CHỈ định nghĩa routes
│
└── scratch/                    # Scripts thử nghiệm (không dùng trong production)
```

---

## 4. Tech Stack Thực tế

| Tầng | Công nghệ | Lý do chọn |
|------|-----------|------------|
| **Crawler** | Python + `requests` + `re` | NEU dùng Next.js RSC — data nhúng trong HTML dạng double-escaped JSON, không cần browser automation |
| **Database** | MongoDB Atlas (Free tier) | Schema linh hoạt, lưu curriculum JSON phân cấp theo học kỳ tự nhiên |
| **Backend API** | FastAPI | Nhẹ, async, tự sinh docs `/docs` |
| **Frontend** | Streamlit | Rapid prototype, đủ dùng cho MVP |
| **Config** | python-dotenv + `.env` | Tách credentials khỏi code |

---

## 5. Cơ chế Crawl — Kỹ thuật quan trọng

### Vấn đề
`courses.neu.edu.vn` dùng **Next.js App Router (RSC)**:
- Không có `__NEXT_DATA__` truyền thống
- Data được nhúng trong HTML dưới dạng **chuỗi double-escaped**:
  ```
  \\\"subjectCode\\\":\\\"TMQT1133\\\",\\\"credits\\\":3
  ```

### Giải pháp (trong `neu_crawler.py`)
```python
# Bước 1: Unescape lớp đầu
unescaped = html.replace('\\"', '"')

# Bước 2: Regex extract theo cấu trúc thực tế
pattern = re.compile(
    r'"semester"\s*:\s*(\d+)'
    r'.{1,1500}?'
    r'"name"\s*:\s*"([^"]+)"'
    r'.{0,300}?'
    r'"subjectCode"\s*:\s*"([^"]+)"'
    r'.{0,100}?'
    r'"credits"\s*:\s*(\d+)',
    re.DOTALL,
)
```

### Kết quả
- Crawl được **đúng học kỳ** (semester 1–8), không phải giả lập năm học
- Mỗi môn có: `code`, `name`, `credits`, `semester`

---

## 6. Data Schema (MongoDB)

### Collection: `majors`
```json
{
  "id":         "7340121_2025",
  "school":     "NEU",
  "major_code": "7340121",
  "major_name": "Kinh doanh thương mại (2025)",
  "slug":       "kinh-doanh-thuong-mai-K677340121",
  "scores":     { "2024": 26.0 },
  "year_label": "2025",
  "curriculum": [
    {
      "semester": 1,
      "subjects": [
        { "code": "TOCB1110", "name": "Toán cho các nhà kinh tế", "credits": 3 },
        { "code": "KHMI1101", "name": "Kinh tế vi mô 1",          "credits": 3 }
      ]
    },
    { "semester": 2, "subjects": [ ... ] },
    ...
    { "semester": 8, "subjects": [ ... ] }
  ]
}
```

**Lưu ý:** Field `curriculum[].semester` thay thế `curriculum[].year` cũ — phản ánh đúng cấu trúc học kỳ của NEU.

---

## 7. API Endpoints

| Method | Endpoint | Chức năng |
|--------|----------|-----------|
| `POST` | `/api/sync` | Chạy crawler + xóa data cũ + insert mới vào DB |
| `GET` | `/api/search?query=...` | Tìm kiếm ngành theo mã hoặc tên (dùng cho dropdown) |
| `GET` | `/api/curriculum/{major_id}` | Lấy toàn bộ thông tin + curriculum của 1 ngành |

**Base URL (local):** `http://localhost:8000`  
**Docs:** `http://localhost:8000/docs`

---

## 8. Luồng Sync Data (Admin)

```
Admin bấm nút "Sync" trên Streamlit
    │
    ▼
POST /api/sync  (FastAPI)
    │
    ├─► crawl_neu_data()        [crawler/neu_crawler.py]
    │       Fetch HTML từ NEU → parse → list[dict]
    │
    └─► insert_majors(data)     [db/database.py]
            delete_many({}) → insert_many(data)
```

---

## 9. Cách chạy hệ thống

### Yêu cầu
```
pip install requests pymongo python-dotenv fastapi uvicorn streamlit pandas
```

### Chạy Backend API
```bash
# Từ thư mục gốc (Crawl_data/)
uvicorn backend.api:app --reload --port 8000
```

### Chạy Frontend
```bash
streamlit run app.py
```

### Chạy Crawler độc lập (test/debug)
```bash
python crawler/neu_crawler.py
```

### Test DB
```bash
python db/database.py
```

---

## 10. Kế hoạch mở rộng

| Tính năng | Ưu tiên | Ghi chú |
|-----------|---------|---------|
| Thêm trường HVNH | Cao | Cần viết `hvnh_crawler.py` riêng |
| Dữ liệu điểm chuẩn thực | Cao | Crawl từ thansố.vn hoặc nhà trường |
| Phân loại môn bắt buộc / tự chọn | Trung bình | Field `required` đã có trong HTML |
| Môn tiên quyết | Trung bình | Field `prerequisiteSubjectCode` trong HTML |
| Lọc theo khối kiến thức | Thấp | Field `knowledgeBlock` đã có trong HTML |
| Deploy lên cloud | Thấp | Vercel (frontend) + Render (API) |