"""
glosy.re.kr (G'L 청소년연구재단) — 모집/신청 크롤러
-----------------------------------------------------
실행:
  pip install httpx beautifulsoup4
  python crawl_glosy.py

  ※ SSR 사이트 — Playwright 불필요, httpx + BS4만으로 동작

결과: glosy_programs.json

크롤 대상 게시판:
  unispec  청년 지원 프로그램
  star     부모 지원 프로그램
  pm       은둔고립 부모지도사 자격과정
  wt       은둔고립 전문가 자격과정
  stars    심리상담
  110      관련기관 프로그램
"""

import json
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import httpx
from bs4 import BeautifulSoup
from crawler_utils import (
    clean, extract_deadline, extract_region, extract_method,
    extract_qual_chip, infer_status, build_chips,
    extract_weeks, extract_curriculum,
)

BASE_URL  = "https://www.glosy.re.kr"
Q_PARAM   = "YToxOntzOjEyOiJrZXl3b3JkX3R5cGUiO3M6MzoiYWxsIjt9"
MAX_PAGES = 2
MAX_ITEMS = 20

BOARDS = [
    ("unispec", "청년 지원"),
    ("star",    "부모 지원"),
    ("pm",      "자격과정"),
    ("wt",      "자격과정"),
    ("stars",   "상담"),
    ("110",     "관련기관"),
]

ORG_NAME = "G'L 청소년연구재단"
ORG_INFO = {
    "name":     ORG_NAME,
    "region":   "서울",
    "phone":    "",
    "email":    "",
    "kakao":    "",
    "homepage": BASE_URL,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# ── 목록 수집 ─────────────────────────────────────────────────────────────────
def collect_links(client, board_slug: str, board_tag: str, seen: set) -> list:
    items = []
    list_base = f"{BASE_URL}/{board_slug}/"

    for p_num in range(1, MAX_PAGES + 1):
        url = f"{list_base}?q={Q_PARAM}&page={p_num}"
        print(f"  [목록 {board_slug} p{p_num}] {url}")
        try:
            resp = client.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"    !! {e}"); break

        soup = BeautifulSoup(resp.text, "html.parser")
        found = 0

        for a in soup.select("a[href*='bmode=view']"):
            href = a.get("href", "")
            m = re.search(r'idx=(\d+)', href)
            if not m:
                continue
            idx = m.group(1)
            detail_url = f"{list_base}?q={Q_PARAM}&bmode=view&idx={idx}&t=board"
            if detail_url in seen:
                continue
            seen.add(detail_url)

            # 썸네일
            thumb = ""
            img = a.find("img")
            if img:
                thumb = img.get("src", "")

            # 뱃지 상태
            li = a.find_parent("li") or a
            badge_text = li.get_text()
            if "마감" in badge_text:
                pre_status = ("closed", "마감")
            elif "모집" in badge_text:
                pre_status = ("open", "모집 중")
            else:
                pre_status = None

            items.append((detail_url, pre_status, thumb, board_tag))
            found += 1

        if found == 0:
            break

    return items

# ── 상세 크롤 ─────────────────────────────────────────────────────────────────
def crawl_detail(client, url: str, pre_status, thumb: str, board_tag: str) -> dict:
    print(f"\n  → {url}")
    try:
        resp = client.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"    !! {e}"); return None

    soup = BeautifulSoup(resp.text, "html.parser")

    def get_meta(name):
        tag = soup.find("meta", property=name) or soup.find("meta", attrs={"name": name})
        return tag["content"].strip() if tag and tag.get("content") else ""

    # ── 제목 ──
    og_title = get_meta("og:title")
    title = re.sub(r"\s*:\s*G.?L\s*청소년연구재단.*$", "", og_title).strip() if og_title else ""
    if not title:
        h = soup.find(["h1", "h2", "h3"])
        title = h.get_text(strip=True) if h else url.split("idx=")[-1]

    # ── 본문 ──
    og_desc = re.sub(r'&nbsp;|&amp;', ' ', get_meta("og:description"))
    body_el = (soup.find(class_=re.compile(r'board.view|view.cont|contents'))
               or soup.find("article") or soup.find("main"))
    body_text = clean(body_el.get_text("\n") if body_el else soup.get_text("\n"))
    full_text = og_desc if len(og_desc) > 100 else body_text

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
    qual               = extract_qual_chip(full_text)
    weeks              = extract_weeks(full_text)
    curriculum         = extract_curriculum(body_text)

    if pre_status:
        status_v, status = pre_status
    else:
        status_v, status = infer_status(full_text)

    chips = build_chips(status, qual, region, method)

    phone_m = re.search(r'(\d{2,3}[-)\s]\d{3,4}[-]\d{4})', full_text)
    email_m = re.search(r'([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', full_text)
    og_image = get_meta("og:image") or thumb

    result = {
        "tag":           board_tag,
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
    results  = []
    all_items = []
    seen = set()

    with httpx.Client(headers=HEADERS, follow_redirects=True) as client:
        for board_slug, board_tag in BOARDS:
            items = collect_links(client, board_slug, board_tag, seen)
            all_items.extend(items)
            if len(all_items) >= MAX_ITEMS:
                break

        all_items = all_items[:MAX_ITEMS]
        print(f"\n상세 크롤 시작 ({len(all_items)}개)...")

        for url, pre_status, thumb, board_tag in all_items:
            r = crawl_detail(client, url, pre_status, thumb, board_tag)
            if r:
                results.append(r)

    with open("glosy_programs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(results)}개 완료 → glosy_programs.json")
    for r in results:
        print(f"  [{r['tag']}] {r['title'][:40]}")
        print(f"         chips={r['chips']}  deadline={r['deadline']}")

if __name__ == "__main__":
    main()
