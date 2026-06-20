"""
gjtory.kr (광주광역시은둔형외톨이지원센터) — 프로그램 신청 크롤러
-----------------------------------------------------------------
실행:
  pip install playwright httpx
  playwright install chromium
  python crawl_gjtory.py

결과: gjtory_programs.json

구조 분석:
  - 목록: https://gjtory.kr/50/?q=...&page=N  (SSR, Playwright 필요)
  - 상세: https://gjtory.kr/50/?bmode=view&idx={숫자}&t=board
  - og:description에 본문 전체 포함 → meta 태그에서 직접 추출 가능
  - og:image에 포스터 이미지 URL 포함
  - 2페이지 구성
"""

import json
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright
from crawler_utils import (
    clean, extract_deadline, extract_region,
    extract_method, extract_qual_chip, infer_status, build_chips,
    extract_weeks, extract_curriculum, infer_tag,
)

BASE_URL   = "https://gjtory.kr"
LIST_BASE  = f"{BASE_URL}/50/"
Q_PARAM    = "YToxOntzOjEyOiJrZXl3b3JkX3R5cGUiO3M6MzoiYWxsIjt9"
MAX_PAGES  = 2
MAX_ITEMS  = 20

ORG_NAME = "광주광역시은둔형외톨이지원센터"
ORG_INFO = {
    "name":     ORG_NAME,
    "region":   "광주",
    "phone":    "062-511-0522",
    "email":    "",
    "kakao":    "gjtory",
    "homepage": BASE_URL,
}

# ── 목록에서 idx 수집 ─────────────────────────────────────────────────────────
def collect_links(page) -> list:
    links = []
    seen  = set()

    for p_num in range(1, MAX_PAGES + 1):
        url = f"{LIST_BASE}?q={Q_PARAM}&page={p_num}"
        print(f"  [목록 p{p_num}] {url}")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_selector("a[href*='bmode=view']", timeout=10000)
        except Exception as e:
            print(f"    !! {e}"); continue

        # bmode=view&idx={숫자} 패턴 링크 수집
        for el in page.locator("a[href*='bmode=view']").all():
            href = el.get_attribute("href") or ""
            m = re.search(r'idx=(\d+)', href)
            if not m:
                continue
            idx = m.group(1)
            detail_url = f"{LIST_BASE}?q={Q_PARAM}&bmode=view&idx={idx}&t=board"
            if detail_url not in seen:
                seen.add(detail_url)
                links.append(detail_url)

        if len(links) >= MAX_ITEMS:
            break

    print(f"  → {len(links)}개 링크 수집")
    return links[:MAX_ITEMS]

# ── meta 태그에서 정보 추출 ───────────────────────────────────────────────────
def get_meta(page, name: str) -> str:
    """og: 또는 name= 메타 태그 값 반환"""
    for attr in [f'meta[property="{name}"]', f'meta[name="{name}"]']:
        el = page.locator(attr).first
        if el.count() > 0:
            val = el.get_attribute("content") or ""
            if val.strip():
                return val.strip()
    return ""

# ── 제목 추출 ─────────────────────────────────────────────────────────────────
def extract_title(page) -> str:
    # og:title이 가장 정확 (기관명 제거)
    og_title = get_meta(page, "og:title")
    if og_title:
        title = og_title.replace(f": {ORG_NAME}", "").replace(ORG_NAME, "").strip(" :-|·")
        if title:
            return title

    for sel in ["h1", "h2", ".board-view-title", "[class*='title']"]:
        for el in page.locator(sel).all():
            t = el.inner_text().strip()
            if 3 < len(t) < 100 and ORG_NAME not in t:
                return t

    raw = page.title().replace(f": {ORG_NAME}", "").replace(ORG_NAME, "").strip(" :-|·")
    return raw or page.url.rstrip("/").split("idx=")[-1]

# ── 상세 크롤 ─────────────────────────────────────────────────────────────────
def crawl_detail(page, url: str) -> dict:
    print(f"\n  → {url}")
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_selector("meta[property='og:title']", timeout=8000)
    except Exception as e:
        print(f"    !! {e}"); return None

    title = extract_title(page)

    # og:description에 본문 전체가 들어있음 → 우선 사용
    og_desc = get_meta(page, "og:description")
    og_desc = re.sub(r'&nbsp;', ' ', og_desc)

    # 본문 텍스트 (fallback)
    body_text = ""
    for sel in [".board-view-contents", ".view_cont", ".contents", "article", "main"]:
        el = page.locator(sel).first
        if el.count() > 0:
            body_text = el.inner_text()
            break
    if not body_text:
        body_text = page.locator("body").inner_text()
    body_text = clean(body_text)

    # og:description이 더 깔끔하면 우선
    full_text = og_desc if len(og_desc) > len(body_text) * 0.3 else body_text

    # 게시날짜 추출 (마감일 추정용)
    post_date = ""
    for sel in ["time", ".date", ".wr_date", ".write-date", "[class*='date']", "[class*='time']"]:
        try:
            m_date = re.search(r'(\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2})', soup.get_text() if hasattr(soup, 'get_text') else "")
            if m_date:
                post_date = m_date.group(1)
                break
        except Exception:
            pass

    deadline_str, dday = extract_deadline(full_text, post_date)
    region             = extract_region(full_text, ORG_INFO["region"])
    method             = extract_method(full_text)
    status_v, status   = infer_status(full_text)
    qual               = extract_qual_chip(full_text)
    chips              = build_chips(status, qual, region, method)
    weeks              = extract_weeks(full_text)
    curriculum         = extract_curriculum(body_text)
    tag                = infer_tag(title, full_text)

    phone_m = re.search(r'(\d{2,3}[)\-]\d{3,4}[)\-\-]\d{4})', full_text)
    email_m = re.search(r'([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', full_text)

    # og:image → 포스터
    og_image = get_meta(page, "og:image")

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
            "intro":         full_text[:120].replace("\n", " "),
            "description":   full_text[:400].replace("\n", " "),
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

    with open("gjtory_programs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(results)}개 완료 → gjtory_programs.json")
    for r in results:
        print(f"  [{r['tag']}] {r['title'][:40]}")
        print(f"         chips={r['chips']}  deadline={r['deadline']}")

if __name__ == "__main__":
    main()
