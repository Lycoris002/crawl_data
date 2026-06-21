"""
backend/api.py
==============
FastAPI backend — chỉ chứa route definitions.
Tất cả crawl logic -> crawler/neu_crawler.py
Tất cả DB logic   -> db/database.py
"""

import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# Đảm bảo project root nằm trong sys.path (để import crawler và db)
_project_root = os.path.dirname(os.path.dirname(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from crawler.neu_crawler import crawl_neu_data
from db.database import insert_majors, search_majors, get_major_by_id

app = FastAPI(
    title="NEU Courses API",
    description="API lấy dữ liệu chương trình đào tạo Đại học Kinh tế Quốc dân (NEU).",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/api/sync")
def sync_data():
    """
    Kích hoạt crawl toàn bộ dữ liệu từ NEU và lưu vào MongoDB.
    Tách biệt hoàn toàn: crawler chỉ crawl, db chỉ insert.
    """
    try:
        raw_data = crawl_neu_data()        # 1. Crawl
        count    = insert_majors(raw_data)  # 2. Insert DB
        return {
            "status":  "success",
            "message": f"Đã crawl và lưu {count} ngành vào MongoDB Atlas.",
            "count":   count,
        }
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {e}")


@app.get("/api/search")
def search(query: str = ""):
    """
    Tìm kiếm ngành theo mã hoặc tên (dropdown gợi ý).
    """
    try:
        return search_majors(query)
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn DB: {e}")


@app.get("/api/curriculum/{major_id}")
def get_curriculum(major_id: str):
    """
    Lấy chi tiết chương trình đào tạo của một ngành theo ID.
    """
    try:
        item = get_major_by_id(major_id)
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn DB: {e}")

    if item is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy ngành với id='{major_id}'")
    return item
