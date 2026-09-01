"""crawlers/crawl_jsbwelfare.py — 울산중구종합사회복지관 래퍼"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from jsbwelfare_scraper import get_post_links, parse_detail
import json, time, random

def main():
    hints = get_post_links(max_pages=50)  # 최대 50페이지로 제한
    results = []
    for hint in hints:
        d = parse_detail(hint)
        if d:
            results.append(d)
        time.sleep(random.uniform(0.4, 0.9))
    with open("jsbwelfare_programs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ jsbwelfare: {len(results)}개 → jsbwelfare_programs.json")

if __name__ == "__main__":
    main()
