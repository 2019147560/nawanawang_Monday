"""crawlers/crawl_cbhope.py — 충북청년희망센터 래퍼"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from cbhope_scraper import get_post_links, parse_detail
import json, time, random

def main():
    hints = get_post_links()
    results = []
    for hint in hints:
        d = parse_detail(hint)
        if d:
            results.append(d)
        time.sleep(random.uniform(0.4, 0.9))
    with open("cbhope_programs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ cbhope: {len(results)}개 → cbhope_programs.json")

if __name__ == "__main__":
    main()
