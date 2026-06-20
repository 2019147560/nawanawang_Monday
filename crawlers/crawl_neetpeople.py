"""
neetpeople.kr (니트생활자) — RECRUITING 게시판 크롤러
------------------------------------------------------
실행:
  pip install httpx beautifulsoup4
  python crawl_neetpeople.py

  ※ SSR 사이트 — Playwright 불필요, httpx + BS4만으로 동작

결과: neetpeople_programs.json

구조:
  - 목록: /recruiting/?q=...&page=N  (SSR)
  - 상세: /recruiting/?q=...&bmode=view&idx={숫자}&t=board
  - 카테고리 뱃지: 마감 / 니트컴퍼니 / 니트인베스트먼트 / 니트워킹데이
  - 페이지네이션 있음 (2페이지 이상)
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

BASE_URL  = "https://neetpeople.kr"
LIST_BASE = f"{BASE_URL}/recruiting/"
Q_PARAM   = "YToxOntzOjEyOiJrZXl3b3JkX3R5cGUiO3M6MzoiYWxsIjt9"
MAX_PAGES = 3
MAX_ITEMS = 20

ORG_NAME = "니트생활자"
ORG_INFO = {
    "name":     ORG_NAME,
    "region":   "서울",
    "phone":    "",
    "email":    "admin@neetpeople.kr",
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

# 카테고리 뱃지 → tag 매핑
CATEGORY_TAG = {
    "니트컴퍼니":       "일경험",
    "니트인베스트먼트": "일경험",
    "니트워킹데이":     "자조모임",
    "마감":             None,   # tag는 본문에서 판단
}

# ── 목록 수집 ─────────────────────────────────────────────────────────────────
def collect_links(client) -> list:
    items = []
    seen  = set()

    for p_num in range(1, MAX_PAGES + 1):
        url = f"{LIST_BASE}?q={Q_PARAM}&page={p_num}"
        print(f"  [목록 p{p_num}] {url}")
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
            detail_url = f"{LIST_BASE}?q={Q_PARAM}&bmode=view&idx={idx}&t=board"
            if detail_url in seen:
                continue
            seen.add(detail_url)

            # 썸네일
            thumb = ""
            img = a.find("img")
            if img:
                src = img.get("src", "")
                thumb = src if src.startswith("http") else BASE_URL + src

            # 부모 행에서 카테고리 뱃지 + 상태 파악
            row = a.find_parent("li") or a.find_parent("tr") or a
            row_text = row.get_text()

            # 카테고리
            category = ""
            for cat in CATEGORY_TAG:
                if cat in row_text:
                    category = cat
                    break

            # 상태
            if "마감" in row_text:
                pre_status = ("closed", "마감")
            elif "모집" in row_text:
                pre_status = ("open", "모집 중")
            else:
                pre_status = None

            items.append((detail_url, pre_status, thumb, category))
            found += 1

        if found == 0:
            break
        if len(items) >= MAX_ITEMS:
            break

    print(f"  → {len(items)}개 링크 수집")
    return items[:MAX_ITEMS]

# ── 상세 크롤 ─────────────────────────────────────────────────────────────────
def crawl_detail(client, url: str, pre_status, thumb: str, category: str) -> dict:
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
    title = re.sub(r'\s*:?\s*니트생활자.*$', '', og_title).strip() if og_title else ""
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

    # tag: 카테고리 뱃지 우선, 없으면 본문 키워드
    tag = CATEGORY_TAG.get(category) or _infer_tag(title, full_text)

    if pre_status:
        status_v, status = pre_status
    else:
        status_v, status = infer_status(full_text)

    chips = build_chips(status, qual, region, method)
    # 카테고리가 있으면 chips 앞에 추가
    if category and category != "마감" and category not in chips:
        chips.insert(0 if status != "마감" else 1, category)

    phone_m = re.search(r'(\d{2,3}[-)\s]\d{3,4}[-]\d{4})', full_text)
    email_m = re.search(r'([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', full_text)
    og_image = get_meta("og:image") or thumb

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

def _infer_tag(title: str, body: str) -> str:
    combined = title + body[:300]
    if any(k in combined for k in ["상담", "심리", "마음"]):         return "상담"
    if any(k in combined for k in ["일경험", "취업", "직무", "사원"]): return "일경험"
    if any(k in combined for k in ["모임", "걷기", "커뮤니티"]):      return "자조모임"
    return "프로그램"

# ── 메인 ─────────────────────────────────────────────────────────────────────
def main():
    results = []

    with httpx.Client(headers=HEADERS, follow_redirects=True) as client:
        items = collect_links(client)
        print(f"\n상세 크롤 시작 ({len(items)}개)...")
        for url, pre_status, thumb, category in items:
            r = crawl_detail(client, url, pre_status, thumb, category)
            if r:
                results.append(r)

    with open("neetpeople_programs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(results)}개 완료 → neetpeople_programs.json")
    for r in results:
        print(f"  [{r['tag']}] {r['title'][:40]}")
        print(f"         chips={r['chips']}  deadline={r['deadline']}")

if __name__ == "__main__":
    main()
