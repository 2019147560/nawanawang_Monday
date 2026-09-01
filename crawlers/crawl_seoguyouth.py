"""crawlers/crawl_seoguyouth.py — 서구 청년정보플랫폼 래퍼"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from seoguyouth_scraper import get_post_links, parse_detail
import json, time, random

def main():
    hints = get_post_links()
    results = []
    for hint in hints:
        d = parse_detail(hint)
        if d:
            results.append(d)
        time.sleep(random.uniform(0.4, 0.8))
    with open("seoguyouth_programs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ seoguyouth: {len(results)}개 → seoguyouth_programs.json")

if __name__ == "__main__":
    main()
