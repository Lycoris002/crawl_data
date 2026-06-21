import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db.database import _get_collection

col = _get_collection()
# Pick 3 different majors
majors = list(col.find({"curriculum": {"$exists": True, "$not": {"$size": 0}}}))

selected = []
keywords = ["Toán", "Kế toán", "Quản trị"]

for kw in keywords:
    for m in majors:
        if kw.lower() in m.get("major_name", "").lower():
            selected.append(m)
            break

for m in selected:
    print(f"\n--- MAJOR: {m.get('major_name')} ---")
    print("Nội dung Chuẩn đầu ra: (Không có trên hệ thống NEU)")
    print("Cơ hội việc làm: (Không có trên hệ thống NEU)")
    print("Danh sách môn học:")
    curriculum = m.get("curriculum", [])
    subjects = []
    for sem in curriculum:
        for sub in sem.get("subjects", []):
            subjects.append(sub.get("name"))
    print(", ".join(subjects[:20]) + " ...")
