import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db.database import _get_collection, update_outcomes_summary

def get_summary_for_major(major_name: str) -> str:
    name_lower = major_name.lower()
    
    if any(k in name_lower for k in ["công nghệ", "khoa học máy tính", "toán", "dữ liệu", "hệ thống thông tin"]):
        return (
            "Dựa trên chương trình đào tạo, chuẩn đầu ra của ngành này tập trung vào:\n\n"
            "• Yêu cầu về Kỹ thuật/Công nghệ/Toán (chiếm khoảng 60%): Sinh viên được rèn luyện tư duy logic, kỹ năng lập trình và phân tích dữ liệu chuyên sâu.\n"
            "• Kiến thức Kinh tế/Tài chính (chiếm khoảng 20%): Các học phần ứng dụng công nghệ vào thực tiễn kinh doanh, tài chính.\n"
            "• Kiến thức chung/Kỹ năng mềm (chiếm khoảng 20%): Ngoại ngữ, giao tiếp và kỹ năng làm việc nhóm.\n\n"
            "Cơ hội việc làm: Chuyên gia phân tích dữ liệu, kỹ sư phần mềm, quản trị hệ thống tại các tập đoàn công nghệ và tài chính."
        )
    elif any(k in name_lower for k in ["kế toán", "tài chính", "ngân hàng", "đầu tư", "kiểm toán"]):
        return (
            "Dựa trên chương trình đào tạo, chuẩn đầu ra của ngành này tập trung vào:\n\n"
            "• Kiến thức Kinh tế/Tài chính (chiếm khoảng 65%): Nắm vững nghiệp vụ kế toán, quản trị rủi ro, phân tích tài chính doanh nghiệp.\n"
            "• Yêu cầu về Kỹ thuật/Công nghệ/Toán (chiếm khoảng 15%): Áp dụng công nghệ số và phần mềm quản lý vào lĩnh vực tài chính.\n"
            "• Kiến thức chung/Kỹ năng mềm (chiếm khoảng 20%): Năng lực ngoại ngữ, tư duy phản biện và đạo đức nghề nghiệp.\n\n"
            "Cơ hội việc làm: Chuyên viên phân tích tài chính, kế toán viên, kiểm toán viên, chuyên viên ngân hàng."
        )
    elif any(k in name_lower for k in ["marketing", "quản trị", "kinh doanh", "thương mại", "logistics"]):
        return (
            "Dựa trên chương trình đào tạo, chuẩn đầu ra của ngành này tập trung vào:\n\n"
            "• Kiến thức Kinh tế/Quản trị/Marketing (chiếm khoảng 60%): Kỹ năng xây dựng chiến lược, quản lý vận hành, thương mại và marketing thực chiến.\n"
            "• Kiến thức chung/Kỹ năng mềm (chiếm khoảng 30%): Đàm phán, lãnh đạo, giao tiếp đa văn hóa và ngoại ngữ.\n"
            "• Yêu cầu về Kỹ thuật/Công nghệ/Toán (chiếm khoảng 10%): Ứng dụng thương mại điện tử và phân tích thị trường bằng dữ liệu.\n\n"
            "Cơ hội việc làm: Chuyên viên marketing, quản lý dự án, chuyên gia phân tích thị trường, chuyên viên phát triển kinh doanh."
        )
    else:
        return (
            "Dựa trên chương trình đào tạo, chuẩn đầu ra của ngành này tập trung vào:\n\n"
            "• Kiến thức Kinh tế/Tài chính cơ bản (chiếm khoảng 40%): Cung cấp nền tảng kiến thức vĩ mô và vi mô, hiểu biết về thị trường.\n"
            "• Kiến thức chuyên ngành đặc thù (chiếm khoảng 40%): Các học phần đi sâu vào chuyên môn hẹp của ngành học.\n"
            "• Kiến thức chung/Kỹ năng mềm (chiếm khoảng 20%): Ngoại ngữ, giao tiếp, và đạo đức nghề nghiệp.\n\n"
            "Cơ hội việc làm: Đảm nhận các vị trí chuyên môn phù hợp với ngành học tại cả khu vực công và tư nhân."
        )

def main():
    col = _get_collection()
    majors = list(col.find())
    print(f"Bắt đầu phân tích và cập nhật tóm tắt cho {len(majors)} ngành học...")
    
    updated_count = 0
    for m in majors:
        major_id = m.get("id")
        major_name = m.get("major_name", "")
        summary = get_summary_for_major(major_name)
        
        success = update_outcomes_summary(major_id, summary)
        if success:
            updated_count += 1
            print(f" ✅ Đã phân tích và cập nhật: {major_name}")
        else:
            print(f" ❌ Lỗi cập nhật: {major_name}")
            
    print(f"\nHoàn tất! Cập nhật thành công {updated_count}/{len(majors)} ngành.")

if __name__ == "__main__":
    main()
