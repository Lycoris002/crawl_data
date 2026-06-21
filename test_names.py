import requests
import re
from crawler.neu_crawler import HEADERS

def get_names():
    r = requests.get("https://courses.neu.edu.vn/?year=K67%20-%202025", headers=HEADERS, timeout=30)
    clean = r.text.replace('\\"', '"')
    pattern = r'"attributes":\{(.*?)\}'
    for m in re.finditer(pattern, clean, re.DOTALL):
        chunk = m.group(1)
        name_m  = re.search(r'"name"\s*:\s*"([^"]+)"', chunk)
        slug_m  = re.search(r'"slug"\s*:\s*"([^"]+)"', chunk)
        admit_m = re.search(r'"admissionCode"\s*:\s*"([^"]+)"', chunk)
        major_m = re.search(r'"majorCode"\s*:\s*"([^"]+)"', chunk)
        if name_m and (admit_m or major_m):
            code = (admit_m.group(1) if admit_m else major_m.group(1) if major_m else "")
            print(f"Code: {code}, Name: {name_m.group(1)}")

get_names()
