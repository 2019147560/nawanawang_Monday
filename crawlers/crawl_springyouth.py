"""crawlers/crawl_springyouth.py — 늘봄청소년 래퍼 (Selenium)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from springyouth_scraper import get_post_links, parse_detail
import json, time, random

def main():
    hints = get_post_links()
    results = []
    for hint in hints:
        d = parse_detail(hint)
        if d:
            results.append(d)
        time.sleep(random.uniform(0.5, 1.0))
    with open("springyouth_programs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ springyouth: {len(results)}개 → springyouth_programs.json")

if __name__ == "__main__":
    main()
