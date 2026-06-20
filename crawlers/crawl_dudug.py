"""
dudug.kr (두더지땅굴) 프로그램 크롤러
--------------------------------------
실행:
  pip install playwright httpx
  playwright install chromium
  python crawl_dudug.py

결과: dudug_programs.json
"""

import json
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright
from crawler_utils import (
    clean, extract_title_from_page, extract_deadline, extract_region,
    extract_method, extract_qual_chip, infer_status, build_chips,
    extract_weeks, extract_curriculum,
)

PROGRAM_PAGES = [
    {"url": "https://dudug.kr/196", "tag": "일경험"},
    {"url": "https://dudug.kr/197", "tag": "일경험"},
    {"url": "https://dudug.kr/184", "tag": "일경험"},
    {"url": "https://dudug.kr/192", "tag": "일경험"},
    {"url": "https://dudug.kr/194", "tag": "일경험"},
    {"url": "https://dudug.kr/93",  "tag": "자조모임"},
    {"url": "https://dudug.kr/151", "tag": "자조모임"},
    {"url": "https://dudug.kr/153", "tag": "자조모임"},
    {"url": "https://dudug.kr/195", "tag": "상담"},
    {"url": "https://dudug.kr/179", "tag": "상담"},
    {"url": "https://dudug.kr/181", "tag": "일경험"},
]

BASE_URL = "https://dudug.kr"
ORG_NAME = "두더지땅굴 (사단법인 씨즈)"
ORG_INFO = {
    "name":     ORG_NAME,
    "region":   "서울",
    "phone":    "",
    "email":    "duduzi@seeds.or.kr",
    "kakao":    "@두더지땅굴",
    "homepage": BASE_URL,
}

def crawl_page(page, url: str, tag: str) -> dict:
    print(f"\n  → {url}")
    try:
        page.goto(url, wait_until="networkidle", timeout=25000)
        page.wait_for_timeout(2500)
    except Exception as e:
        print(f"    !! {e}"); return None

    title = extract_title_from_page(page, "두더지땅굴")

    body_text = ""
    for sel in [".board-view-contents", ".contents", "article", "main", ".content"]:
        el = page.locator(sel).first
        if el.count() > 0:
            body_text = el.inner_text()
            break
    if not body_text:
        body_text = page.locator("body").inner_text()
    body_text = clean(body_text)

    # 게시날짜 추출
    import re as _re
    post_date_m = _re.search(r'(\d{4}[.\-]\d{1,2}[.\-]\d{1,2})', body_text)
    post_date = post_date_m.group(1) if post_date_m else ""

    deadline_str, dday = extract_deadline(body_text, post_date)
    region             = extract_region(body_text, ORG_INFO["region"])
    method             = extract_method(body_text)
    status_v, status   = infer_status(body_text)
    qual               = extract_qual_chip(body_text)
    chips              = build_chips(status, qual, region, method)
    weeks              = extract_weeks(body_text)
    curriculum         = extract_curriculum(body_text)

    phone_m = re.search(r'(\d{2,3}-\d{3,4}-\d{4})', body_text)
    email_m = re.search(r'([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', body_text)

    result = {
        "tag":           tag,
        "dDay":          dday,
        "title":         title,
        "org":           ORG_NAME,
        "status":        status,
        "statusVariant": status_v,
        "chips":         chips,
        "weeks":         weeks,
        "deadline":      deadline_str,
        "sourceUrl":     url,
        "detail": {
            "intro":         body_text[:120].replace("\n", " "),
            "description":   body_text[:400].replace("\n", " "),
            "qualification": qual,
            "curriculum":    curriculum,
            "org": {
                **ORG_INFO,
                "phone":  phone_m.group(1) if phone_m else ORG_INFO["phone"],
                "email":  email_m.group(1) if email_m else ORG_INFO["email"],
                "region": region,
                "homepage": url,
            }
        }
    }

    return result

def main():
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ))
        pg = ctx.new_page()

        for item in PROGRAM_PAGES:
            r = crawl_page(pg, item["url"], item["tag"])
            if r:
                results.append(r)

        browser.close()

    with open("dudug_programs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(results)}개 완료 → dudug_programs.json")
    for r in results:
        print(f"  [{r['tag']}] {r['title'][:40]}")
        print(f"         chips={r['chips']}  deadline={r['deadline']}")

if __name__ == "__main__":
    main()
