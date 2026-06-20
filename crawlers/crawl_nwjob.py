"""
nwjob.kr (노원구 청년일자리센터 청년내일) — 크롤러
----------------------------------------------------
실행:
  pip install httpx beautifulsoup4
  python crawl_nwjob.py

  ※ SSR 사이트 — Playwright 불필요

결과: nwjob_programs.json

크롤 대상:
  /18  취업정보 게시판 (외부 프로그램 공고 모음, 9페이지 이상)
  /about 자체 프로그램 안내 페이지
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

BASE_URL  = "https://nwjob.kr"
LIST_BASE = f"{BASE_URL}/18/"
Q_PARAM   = "YToxOntzOjEyOiJrZXl3b3JkX3R5cGUiO3M6MzoiYWxsIjt9"
MAX_PAGES = 2
MAX_ITEMS = 20

ORG_NAME = "노원구 청년일자리센터 청년내일"
ORG_INFO = {
    "name":     ORG_NAME,
    "region":   "서울",
    "phone":    "02-932-2500",
    "email":    "nwyouthjob@gmail.com",
    "kakao":    "pf.kakao.com/_xiRBnxj",
    "homepage": BASE_URL,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# ── 제목에서 마감일 추출 ([~6/7], [~5/26 16:00] 패턴) ────────────────────────
def extract_deadline_from_title(title: str) -> tuple:
    # [~MM/DD], [~YYYY/MM/DD], [~MM/DD HH:MM] 패턴
    m = re.search(r'[~～]\s*(\d{4}[./]\d{1,2}[./]\d{1,2})', title)
    if m:
        s = re.sub(r'[./]', '.', m.group(1))
        parts = s.split('.')
        s = f"{parts[0]}.{parts[1].zfill(2)}.{parts[2].zfill(2)}"
        return f"마감 {s}", s
    m = re.search(r'[~～]\s*(\d{1,2})[./](\d{1,2})', title)
    if m:
        # 연도 없으면 2026 기본
        s = f"2026.{m.group(1).zfill(2)}.{m.group(2).zfill(2)}"
        return f"마감 {s}", s
    return "", ""

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

            # 제목 텍스트 (링크 텍스트에서)
            title_text = a.get_text(strip=True)

            # 썸네일
            thumb = ""
            img = a.find("img")
            if img:
                src = img.get("src", "")
                thumb = src if src.startswith("http") else BASE_URL + src

            # 제목에서 마감일 미리 추출
            deadline_str, dday = extract_deadline_from_title(title_text)

            # 상태: 제목에 마감일 있으면 모집중, 없으면 본문에서 판단
            pre_status = None
            if deadline_str:
                pre_status = ("open", "모집 중")

            items.append((detail_url, pre_status, thumb, title_text, deadline_str, dday))
            found += 1

        if found == 0:
            break
        if len(items) >= MAX_ITEMS:
            break

    print(f"  → {len(items)}개 링크 수집")
    return items[:MAX_ITEMS]

# ── 상세 크롤 ─────────────────────────────────────────────────────────────────
def crawl_detail(client, url, pre_status, thumb, title_hint, deadline_hint, dday_hint) -> dict:
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
    title = re.sub(r'\s*:?\s*노원구.*$', '', og_title).strip() if og_title else ""
    if not title:
        h = soup.find(["h1", "h2", "h3"])
        title = h.get_text(strip=True) if h else title_hint

    # ── 본문 ──
    og_desc = re.sub(r'&nbsp;|&amp;', ' ', get_meta("og:description"))
    body_el = (soup.find(class_=re.compile(r'board.view|view.cont|contents'))
               or soup.find("article") or soup.find("main"))
    body_text = clean(body_el.get_text("\n") if body_el else soup.get_text("\n"))
    full_text = og_desc if len(og_desc) > 100 else body_text

    # 마감일: 제목 힌트 우선 → 본문 추출
    if deadline_hint:
        deadline_str, dday = deadline_hint, dday_hint
    else:
        # 게시날짜 추출 (fallback용)
        post_date_m = re.search(r'(\d{4}[-.\-]\d{1,2}[-.\-]\d{1,2})', full_text)
        post_date = post_date_m.group(1) if post_date_m else ""
        deadline_str, dday = extract_deadline(title + " " + full_text, post_date)

    region = extract_region(full_text, ORG_INFO["region"])
    method = extract_method(full_text)
    qual   = extract_qual_chip(full_text)
    weeks  = extract_weeks(full_text)
    curriculum = extract_curriculum(body_text)
    tag    = _infer_tag(title, full_text)

    if pre_status:
        status_v, status = pre_status
    else:
        status_v, status = infer_status(full_text)

    chips = build_chips(status, qual, region, method)

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
    if any(k in combined for k in ["상담", "심리", "마음"]):                return "상담"
    if any(k in combined for k in ["취업", "채용", "일경험", "직무", "인턴",
                                    "사관학교", "새싹", "코딩", "개발"]):    return "일경험"
    if any(k in combined for k in ["창업", "스타트업"]):                    return "창업"
    if any(k in combined for k in ["모임", "커뮤니티", "클럽"]):            return "자조모임"
    return "프로그램"

# ── 메인 ─────────────────────────────────────────────────────────────────────
def main():
    results = []

    with httpx.Client(headers=HEADERS, follow_redirects=True) as client:
        items = collect_links(client)
        print(f"\n상세 크롤 시작 ({len(items)}개)...")
        for url, pre_status, thumb, title_hint, deadline_hint, dday_hint in items:
            r = crawl_detail(client, url, pre_status, thumb,
                             title_hint, deadline_hint, dday_hint)
            if r:
                results.append(r)

    with open("nwjob_programs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(results)}개 완료 → nwjob_programs.json")
    for r in results:
        print(f"  [{r['tag']}] {r['title'][:40]}")
        print(f"         chips={r['chips']}  deadline={r['deadline']}")

if __name__ == "__main__":
    main()
