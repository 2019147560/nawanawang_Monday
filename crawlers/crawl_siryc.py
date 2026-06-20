"""
siryc.or.kr (서울청년기지개센터) — 사업신청 크롤러
---------------------------------------------------
실행:
  pip install playwright httpx
  playwright install chromium
  python crawl_siryc.py

결과: siryc_programs.json

구조:
  - 목록: /boards/apply?page=1~2
  - 게시글: /posts/{slug} 패턴
  - 포스터 이미지 → Claude Vision OCR로 정보 보완
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
    extract_weeks, extract_curriculum, infer_tag,
)

BASE_URL  = "https://siryc.or.kr"
LIST_URL  = f"{BASE_URL}/boards/apply"
MAX_PAGES = 2
MAX_ITEMS = 20
ORG_NAME  = "서울청년기지개센터"

ORG_INFO = {
    "name":     ORG_NAME,
    "region":   "서울",
    "phone":    "02-6953-2520",
    "email":    "seoulyouthlife@daum.net",
    "kakao":    "@기지개센터",
    "homepage": BASE_URL,
}

# ── 목록에서 링크 수집 ────────────────────────────────────────────────────────
def collect_links(page) -> list:
    links = []
    seen  = set()

    for p_num in range(1, MAX_PAGES + 1):
        url = f"{LIST_URL}?page={p_num}"
        print(f"  [목록 p{p_num}] {url}")
        try:
            page.goto(url, wait_until="networkidle", timeout=25000)
            page.wait_for_timeout(2000)
        except Exception as e:
            print(f"    !! {e}"); continue

        for el in page.locator("a[href*='/posts/']").all():
            href = el.get_attribute("href") or ""
            # /posts/{slug} 형태만 (col_x 등 API 제외)
            if re.search(r'/posts/[A-Za-z0-9]+$', href):
                full = href if href.startswith("http") else BASE_URL + href
                if full not in seen:
                    seen.add(full)
                    links.append(full)

        if len(links) >= MAX_ITEMS:
            break

    print(f"  → {len(links)}개 링크 수집")
    return links[:MAX_ITEMS]

# ── 상세 페이지 크롤 ──────────────────────────────────────────────────────────
def crawl_detail(page, url: str) -> dict:
    print(f"\n  → {url}")
    try:
        page.goto(url, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(1500)
    except Exception as e:
        print(f"    !! {e}"); return None

    title = extract_title_from_page(page, ORG_NAME)

    # 본문 텍스트
    body_text = ""
    for sel in [".prose", ".content", "article", ".post-content", "main"]:
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
    tag                = infer_tag(title, body_text)

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
                "phone": phone_m.group(1) if phone_m else ORG_INFO["phone"],
                "email": email_m.group(1) if email_m else ORG_INFO["email"],
                "region": region,
                "homepage": url,
            }
        }
    }

    return result

# ── 메인 ─────────────────────────────────────────────────────────────────────
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

        links = collect_links(pg)
        print(f"\n상세 크롤 시작 ({len(links)}개)...")
        for url in links:
            r = crawl_detail(pg, url)
            if r:
                results.append(r)

        browser.close()

    with open("siryc_programs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(results)}개 완료 → siryc_programs.json")
    for r in results:
        print(f"  [{r['tag']}] {r['title'][:40]}")
        print(f"         chips={r['chips']}  deadline={r['deadline']}")

if __name__ == "__main__":
    main()
