"""
db/database.py
==============
Module duy nhất chịu trách nhiệm tương tác với MongoDB.
Không chứa logic crawl, không chứa logic business.
"""

import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient, errors

sys.stdout.reconfigure(encoding='utf-8')

# Load biến môi trường từ file .env ở thư mục gốc project
_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(_env_path)

MONGODB_URI    = os.getenv("MONGODB_URI")
DB_NAME        = os.getenv("DB_NAME",        "neu_courses_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "majors")


# ---------------------------------------------------------------------------
# Kết nối
# ---------------------------------------------------------------------------

def _get_collection():
    """Trả về collection MongoDB. Raise nếu URI chưa được cấu hình."""
    if not MONGODB_URI:
        raise EnvironmentError(
            "MONGODB_URI chưa được thiết lập trong file .env. "
            "Vui lòng kiểm tra lại cấu hình."
        )
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10_000)
    return client[DB_NAME][COLLECTION_NAME]


# ---------------------------------------------------------------------------
# Write operations
# ---------------------------------------------------------------------------

def insert_majors(data: list) -> int:
    """
    Insert danh sách ngành mới vào MongoDB, bỏ qua nếu đã tồn tại (check duplicate theo id).

    Args:
        data: list[dict] — raw data từ crawler

    Returns:
        int — số lượng bản ghi mới đã insert

    Raises:
        EnvironmentError: nếu MONGODB_URI chưa được thiết lập
        pymongo.errors.PyMongoError: nếu có lỗi từ MongoDB
    """
    if not data:
        print("[DB] Không có dữ liệu để insert.")
        return 0

    collection = _get_collection()
    print(f"[DB] Kiểm tra và inserting {len(data)} bản ghi...")
    
    count = 0
    for item in data:
        major_id = item.get("id")
        if not collection.find_one({"id": major_id}):
            collection.insert_one(item)
            count += 1
        else:
            # Duplicate
            pass

    print(f"[DB] Insert thành công {count} bản ghi mới vào '{DB_NAME}.{COLLECTION_NAME}'.")
    return count

def delete_all_majors():
    """Xóa toàn bộ dữ liệu trong DB."""
    collection = _get_collection()
    print(f"[DB] Xóa dữ liệu cũ trong collection '{COLLECTION_NAME}'...")
    collection.delete_many({})


def update_scores_for_major(major_id: str, scores: dict) -> bool:
    """
    Cập nhật (merge) điểm chuẩn cho một ngành theo ID.
    KHÔNG xóa dữ liệu curriculum hay các field khác.

    Args:
        major_id: giá trị của field "id" trong MongoDB document
        scores:   dict điểm chuẩn mới, ví dụ {"2022": 27.7, "2023": 27.0, "2024": 27.4}
                  Các năm cũ đã có sẽ được giữ nguyên nếu không có trong dict mới.

    Returns:
        True nếu tìm thấy và update, False nếu không tìm thấy document
    """
    if not scores:
        return False

    collection = _get_collection()

    # Lấy scores hiện tại để merge (không ghi đè toàn bộ)
    existing = collection.find_one({"id": major_id}, {"scores": 1})
    if existing is None:
        return False

    merged_scores = dict(existing.get("scores") or {})
    merged_scores.update(scores)  # scores mới ghi đè/thêm vào scores cũ

    result = collection.update_one(
        {"id": major_id},
        {"$set": {"scores": merged_scores}},
    )
    return result.matched_count > 0


def update_outcomes_summary(major_id: str, summary: str) -> bool:
    """
    Cập nhật tóm tắt chuẩn đầu ra cho một ngành theo ID.

    Args:
        major_id: giá trị của field "id" trong MongoDB document
        summary: chuỗi văn bản tóm tắt chuẩn đầu ra

    Returns:
        True nếu tìm thấy và update, False nếu không tìm thấy document
    """
    if not summary:
        return False

    collection = _get_collection()

    result = collection.update_one(
        {"id": major_id},
        {"$set": {"outcomesSummary": summary}},
    )
    return result.matched_count > 0


# ---------------------------------------------------------------------------
# Read operations
# ---------------------------------------------------------------------------

def get_all_major_codes() -> list[dict]:
    """
    Lấy danh sách tất cả ngành trong DB (chỉ trả về id và major_code).
    Dùng để job điểm chuẩn biết cần update ngành nào.

    Returns:
        list[dict] — mỗi phần tử gồm: {"id": str, "major_code": str}
    """
    collection = _get_collection()
    return [
        {"id": doc.get("id", ""), "major_code": doc.get("major_code", "")}
        for doc in collection.find({}, {"_id": 0, "id": 1, "major_code": 1})
    ]


def search_majors(query: str = "") -> list:
    """
    Tìm kiếm ngành theo mã ngành hoặc tên ngành (case-insensitive regex).

    Args:
        query: chuỗi tìm kiếm. Nếu rỗng → trả về tất cả.

    Returns:
        list[dict] — mỗi phần tử gồm: id, major_code, major_name, school, display_name
    """
    collection = _get_collection()

    mongo_query = {}
    if query.strip():
        mongo_query = {
            "$or": [
                {"major_code": {"$regex": query.strip(), "$options": "i"}},
                {"major_name": {"$regex": query.strip(), "$options": "i"}},
            ]
        }

    results = []
    for item in collection.find(mongo_query):
        results.append({
            "id":           str(item.get("id", "")),
            "major_code":   item.get("major_code", ""),
            "major_name":   item.get("major_name", ""),
            "school":       item.get("school", ""),
            "display_name": (
                f"{item.get('major_code', '')} - "
                f"{item.get('major_name', '')} "
                f"({item.get('school', '')})"
            ),
        })
    return results


def get_major_by_id(major_id: str) -> dict | None:
    """
    Lấy thông tin chi tiết của một ngành theo ID.

    Args:
        major_id: giá trị của field "id" trong MongoDB document

    Returns:
        dict hoặc None nếu không tìm thấy
    """
    collection = _get_collection()
    return collection.find_one({"id": major_id}, {"_id": 0})


# ---------------------------------------------------------------------------
# Entry point (test nhanh kết nối DB)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        col = _get_collection()
        count = col.count_documents({})
        print(f"[DB] Kết nối thành công. Số bản ghi hiện tại: {count}")
    except Exception as e:
        print(f"[DB] Lỗi kết nối: {e}")
