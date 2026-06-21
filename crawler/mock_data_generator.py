import json
import os

def generate_mock_data():
    data = [
        {
            "id": "NEU-IT",
            "school": "NEU",
            "major_code": "IT101",
            "major_name": "Khoa học Máy tính",
            "scores": {
                "2021": 26.5,
                "2022": 27.0,
                "2023": 27.5
            },
            "curriculum": [
                {
                    "year": 1,
                    "subjects": [
                        {"code": "MI101", "name": "Toán cao cấp 1", "credits": 3},
                        {"code": "IT102", "name": "Nhập môn lập trình", "credits": 3},
                        {"code": "LL101", "name": "Triết học Mác - Lênin", "credits": 3}
                    ]
                },
                {
                    "year": 2,
                    "subjects": [
                        {"code": "IT201", "name": "Cấu trúc dữ liệu và Giải thuật", "credits": 3},
                        {"code": "IT202", "name": "Cơ sở dữ liệu", "credits": 3},
                        {"code": "EN201", "name": "Tiếng Anh chuyên ngành", "credits": 3}
                    ]
                },
                {
                    "year": 3,
                    "subjects": [
                        {"code": "IT301", "name": "Mạng máy tính", "credits": 3},
                        {"code": "IT302", "name": "Trí tuệ nhân tạo", "credits": 3}
                    ]
                },
                {
                    "year": 4,
                    "subjects": [
                        {"code": "IT401", "name": "Thực tập tốt nghiệp", "credits": 6},
                        {"code": "IT402", "name": "Khóa luận tốt nghiệp", "credits": 9}
                    ]
                }
            ]
        },
        {
            "id": "HVNH-FIN",
            "school": "HVNH",
            "major_code": "FIN201",
            "major_name": "Tài chính ngân hàng",
            "scores": {
                "2021": 25.0,
                "2022": 25.5,
                "2023": 26.1
            },
            "curriculum": [
                {
                    "year": 1,
                    "subjects": [
                        {"code": "ECO101", "name": "Kinh tế vi mô", "credits": 3},
                        {"code": "FIN101", "name": "Nhập môn tài chính tiền tệ", "credits": 3}
                    ]
                },
                {
                    "year": 2,
                    "subjects": [
                        {"code": "FIN202", "name": "Tài chính doanh nghiệp", "credits": 3},
                        {"code": "FIN203", "name": "Thị trường chứng khoán", "credits": 3}
                    ]
                },
                {
                    "year": 3,
                    "subjects": [
                        {"code": "FIN301", "name": "Quản trị rủi ro tài chính", "credits": 3},
                        {"code": "FIN302", "name": "Định giá tài sản", "credits": 3}
                    ]
                },
                {
                    "year": 4,
                    "subjects": [
                        {"code": "FIN401", "name": "Thực tập chuyên môn", "credits": 6},
                        {"code": "FIN402", "name": "Khóa luận tốt nghiệp", "credits": 9}
                    ]
                }
            ]
        }
    ]

    import os
    from dotenv import load_dotenv
    from pymongo import MongoClient

    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    MONGODB_URI = os.getenv("MONGODB_URI")
    DB_NAME = os.getenv("DB_NAME", "neu_courses_db")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "majors")

    if not MONGODB_URI:
        print("MONGODB_URI không tồn tại trong file .env. Vẫn lưu vào JSON tạm thời.")
        os.makedirs('d:/Crawl_data/db', exist_ok=True)
        with open('d:/Crawl_data/db/data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Mock data generated successfully at db/data.json")
    else:
        try:
            client = MongoClient(MONGODB_URI)
            db = client[DB_NAME]
            collection = db[COLLECTION_NAME]
            
            # Xóa dữ liệu cũ để tránh trùng lặp
            collection.delete_many({})
            # Insert dữ liệu mới
            collection.insert_many(data)
            print("Mock data pushed to MongoDB Atlas successfully!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

if __name__ == "__main__":
    generate_mock_data()
