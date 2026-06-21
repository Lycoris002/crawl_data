import requests
from bs4 import BeautifulSoup
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}

url = "https://courses.neu.edu.vn/curriculum/ke-toan?year=K68%20-%202026&admission=7340301"
r = requests.get(url, headers=HEADERS, timeout=10)

# The html contains Next.js JSON payload which is double escaped. Let's unescape it first.
html_content = r.text.replace('\\"', '"').replace('\\n', '\n')

soup = BeautifulSoup(html_content, 'html.parser')

# In Next.js RSC payload, we can just search for "programOutcomes" or something similar.
# Let's use regex to find all long strings that look like outcomes.
outcomes_pattern = re.search(r'"programOutcomes"\s*:\s*"([^"]+)"', html_content)
if outcomes_pattern:
    print("FOUND programOutcomes:", outcomes_pattern.group(1)[:500])

career_pattern = re.search(r'"careerOpportunities"\s*:\s*"([^"]+)"', html_content)
if career_pattern:
    print("FOUND careerOpportunities:", career_pattern.group(1)[:500])

# Wait, the field names might be different. Let's look for known text.
# The previous test found "Cơ hội việc làm và khả năng học tập nâng cao" as a label.
# The actual data might be right after it. Let's just find "section-outcomes"
match = re.search(r'section-outcomes', html_content)
if match:
    print("FOUND section-outcomes in text")
    start = max(0, match.start() - 200)
    end = min(len(html_content), match.end() + 1000)
    print(html_content[start:end])

