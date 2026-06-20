"""
dgdream45.or.kr (대구청소년창의센터 꿈&꿈) — 프로그램 게시판 크롤러
-------------------------------------------------------------------
실행:
  pip install playwright httpx beautifulsoup4
  playwright install chromium
  python crawl_dgdream45.py

결과: dgdream45_programs.json

구조:
  - 그누보드 기반 (/bbs/board.php?bo_table=program)
  - 봇 감지 있음 → Playwright로 우회
  - 게시글 URL: ?bo_table=program&wr_id={숫자}
"""

import json
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from playwright.sync_api import sync_playwright
from crawler_utils import (
    clean, extract_deadline, extract_region, extract_method,
    extract_qual_chip, infer_status, build_chips,
    extract_weeks, extract_curriculum, infer_tag,
)

BASE_URL  = "https://dgdream45.or.kr"
LIST_URL  = f"{BASE_URL}/bbs/board.php?bo_table=program"
MAX_PAGES = 2
MAX_ITEMS = 20

ORG_NAME = "대구청소년창의센터 꿈&꿈"
ORG_INFO = {
    "name":     ORG_NAME,
    "region":   "대구",
    "phone":    "053-628-1318",
    "email":    "",
    "kakao":    "",
    "homepage": BASE_URL,
}

# ── 봇 감지 우회 브라우저 컨텍스트 ────────────────────────────────────────────
def make_context(p):
    ctx = p.chromium.launch(headless=True).new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        extra_http_headers={
            "Accept-Language": "ko-KR,ko;q=0.9",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
            "Referer": BASE_URL,
        }
    )
    return ctx

INIT_SCRIPT = """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'languages', { get: () => ['ko-KR', 'ko'] });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
"""

# ── 페이지 로드 헬퍼 ──────────────────────────────────────────────────────────
def goto_safe(page, url: str) -> bool:
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_timeout(1500)
        body = page.locator("body").inner_text()
        if "보안절차" in body or "Please prove" in body:
            print(f"    ⚠️  봇 감지 화면")
            return False
        return True
    except Exception as e:
        print(f"    !! {e}")
        return False

# ── 목록에서 링크 수집 ────────────────────────────────────────────────────────
def collect_links(page) -> list:
    items = []
    seen  = set()

    for p_num in range(1, MAX_PAGES + 1):
        url = f"{LIST_URL}&page={p_num}"
        print(f"  [목록 p{p_num}] {url}")

        if not goto_safe(page, url):
            break

        # 그누보드: a[href*='wr_id'] 패턴
        for el in page.locator("a[href*='wr_id']").all():
            href = el.get_attribute("href") or ""
            if "bo_table" not in href:
                continue
            m = re.search(r'wr_id=(\d+)', href)
            if not m:
                continue
            wr_id = m.group(1)
            detail_url = f"{BASE_URL}/bbs/board.php?bo_table=program&wr_id={wr_id}"
            if detail_url in seen:
                continue
            seen.add(detail_url)

            # 제목
            title_text = el.inner_text().strip()

            # 썸네일
            thumb = ""
            img = el.locator("img").first
            if img.count() > 0:
                src = img.get_attribute("src") or ""
                thumb = src if src.startswith("http") else BASE_URL + src

            # 목록에서 상태 파악
            try:
                row_text = el.locator("xpath=ancestor::tr[1]").inner_text()
            except Exception:
                row_text = title_text

            if "마감" in row_text or "종료" in row_text:
                pre_status = ("closed", "마감")
            elif "모집" in row_text:
                pre_status = ("open", "모집 중")
            else:
                pre_status = None

            items.append((detail_url, pre_status, thumb, title_text))

        if len(items) >= MAX_ITEMS:
            break

    print(f"  → {len(items)}개 링크 수집")
    return items[:MAX_ITEMS]

# ── 상세 크롤 ─────────────────────────────────────────────────────────────────
def crawl_detail(page, url: str, pre_status, thumb: str, title_hint: str) -> dict:
    print(f"\n  → {url}")
    if not goto_safe(page, url):
        return None

    # ── 제목 ──
    title = ""
    for sel in [
        ".view_title", ".bv_subject", ".bo_v_tit",
        "h1", "h2", "#bo_v_con h3"
    ]:
        el = page.locator(sel).first
        if el.count() > 0:
            t = el.inner_text().strip()
            if 3 < len(t) < 120 and ORG_NAME not in t:
                title = t
                break
    if not title:
        og = page.locator("meta[property='og:title']").first
        if og.count() > 0:
            raw = og.get_attribute("content") or ""
            title = re.sub(r'\s*[-|]\s*꿈.*$', '', raw).strip()
    if not title:
        title = title_hint

    # ── 본문 ──
    body_text = ""
    for sel in ["#bo_v_con", ".bo_v_con", ".view_content",
                ".board_view", "article", "main"]:
        el = page.locator(sel).first
        if el.count() > 0:
            body_text = el.inner_text()
            break
    if not body_text:
        body_text = page.locator("body").inner_text()
    body_text = clean(body_text)

    # og:description
    og_desc_el = page.locator("meta[property='og:description']").first
    og_desc = ""
    if og_desc_el.count() > 0:
        og_desc = re.sub(r'&nbsp;|&amp;', ' ',
                         og_desc_el.get_attribute("content") or "")
    full_text = og_desc if len(og_desc) > 100 else body_text

    deadline_str, dday = extract_deadline(full_text)
    region             = extract_region(full_text, ORG_INFO["region"])
    method             = extract_method(full_text)
    qual               = extract_qual_chip(full_text)
    weeks              = extract_weeks(full_text)
    curriculum         = extract_curriculum(body_text)
    tag                = infer_tag(title, full_text)

    if pre_status:
        status_v, status = pre_status
    else:
        status_v, status = infer_status(full_text)

    chips = build_chips(status, qual, region, method)

    phone_m = re.search(r'(\d{2,3}[-)\s]\d{3,4}[-]\d{4})', full_text)
    email_m = re.search(r'([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', full_text)

    # og:image
    og_img_el = page.locator("meta[property='og:image']").first
    og_image = (og_img_el.get_attribute("content") or "") if og_img_el.count() > 0 else thumb

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
                "phone":  phone_m.group(1) if phone_m else ORG_INFO["phone"],
                "email":  email_m.group(1) if email_m else ORG_INFO["email"],
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
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            extra_http_headers={
                "Accept-Language": "ko-KR,ko;q=0.9",
                "Referer": BASE_URL,
            }
        )
        pg = ctx.new_page()
        pg.add_init_script(INIT_SCRIPT)

        # 접속 테스트
        print("접속 테스트 중...")
        if not goto_safe(pg, LIST_URL):
            print("❌ headless=True 차단 → headless=False 재시도...")
            browser.close()

            browser2 = p.chromium.launch(headless=False)
            ctx2 = browser2.new_context(user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
            ))
            pg2 = ctx2.new_page()
            pg2.add_init_script(INIT_SCRIPT)

            if not goto_safe(pg2, LIST_URL):
                print("❌ headless=False도 차단 — 크롤링 불가")
                browser2.close()
                return

            print("✅ headless=False 통과 — 크롤 시작")
            items = collect_links(pg2)
            for url, pre_status, thumb, title_hint in items:
                r = crawl_detail(pg2, url, pre_status, thumb, title_hint)
                if r:
                    results.append(r)
            browser2.close()

        else:
            print("✅ headless=True 통과 — 크롤 시작")
            items = collect_links(pg)
            print(f"\n상세 크롤 시작 ({len(items)}개)...")
            for url, pre_status, thumb, title_hint in items:
                r = crawl_detail(pg, url, pre_status, thumb, title_hint)
                if r:
                    results.append(r)
            browser.close()

    if not results:
        print("\n⚠️  결과 없음")
        return

    with open("dgdream45_programs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(results)}개 완료 → dgdream45_programs.json")
    for r in results:
        print(f"  [{r['tag']}] {r['title'][:40]}")
        print(f"         chips={r['chips']}  deadline={r['deadline']}")

if __name__ == "__main__":
    main()
