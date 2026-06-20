"""
neetconnect.kr (닛커넥트) — 우주 정거장 프로그램 크롤러
--------------------------------------------------------
실행:
  pip install httpx beautifulsoup4
  python crawl_neetconnect.py

  ※ SSR 사이트라 Playwright 없이 httpx + BS4만으로 동작합니다.

결과: neetconnect_programs.json

구조:
  - 목록: /browse/{페이지번호}
  - 상세: /meet/{slug}
  - 상태 뱃지: 모집중 / 비행중 / 비행종료 / 모집예정
  - 상세 페이지에 모집기간, 운영기간, 대상, 장소 등 구조화된 정보 존재
"""

import json
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import httpx
from bs4 import BeautifulSoup
from crawler_utils import (
    clean, extract_qual_chip, extract_method, extract_region,
    build_chips, extract_curriculum,
)

BASE_URL  = "https://neetconnect.kr"
MAX_PAGES = 5
MAX_ITEMS = 20

ORG_NAME = "닛커넥트 (사단법인 니트생활자)"
ORG_INFO = {
    "name":     ORG_NAME,
    "region":   "서울",
    "phone":    "",
    "email":    "admin@neetpeople.kr",
    "kakao":    "닛커넥트",
    "homepage": BASE_URL,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# 상태 뱃지 → statusVariant 매핑
STATUS_MAP = {
    "모집중":   ("open",    "모집 중"),
    "모집예정": ("upcoming","모집 예정"),
    "비행중":   ("ongoing", "진행 중"),
    "비행종료": ("closed",  "종료"),
}

# 분류 키워드 → tag
TAG_MAP = [
    ("루틴", ["루틴", "습관", "매일", "daily"]),
    ("관계", ["관계", "모임", "커뮤니티", "소셜", "친구", "동료"]),
    ("경험", ["경험", "체험", "클래스", "공연", "워크숍", "제작", "베이킹", "요가"]),
    ("상담", ["상담", "심리", "마음"]),
    ("일경험", ["인턴", "일경험", "취업", "직무"]),
]

def infer_tag_neet(title: str, desc: str) -> str:
    combined = title + desc
    for tag, keywords in TAG_MAP:
        if any(k in combined for k in keywords):
            return tag
    return "프로그램"

# ── 목록 크롤 ─────────────────────────────────────────────────────────────────
def collect_links(client) -> list:
    """(slug, status_variant, status_label, thumbnail_url) 목록 반환"""
    items = []
    seen  = set()

    for p_num in range(1, MAX_PAGES + 1):
        url = f"{BASE_URL}/browse/{p_num}" if p_num > 1 else f"{BASE_URL}/browse"
        print(f"  [목록 p{p_num}] {url}")
        try:
            resp = client.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"    !! {e}"); break

        soup = BeautifulSoup(resp.text, "html.parser")

        # 카드 단위: /meet/{slug} 링크를 기준으로
        for a in soup.select("a[href*='/meet/']"):
            href = a.get("href", "")
            m = re.search(r'/meet/([A-Za-z0-9]+)$', href)
            if not m:
                continue
            slug = m.group(1)
            if slug in seen:
                continue
            seen.add(slug)

            # 카드 컨테이너에서 상태 뱃지 찾기
            card = a.find_parent()
            status_text = ""
            if card:
                for _ in range(5):   # 최대 5단계 부모까지 탐색
                    badge = card.find(string=re.compile(r'모집중|비행중|비행종료|모집예정'))
                    if badge:
                        status_text = badge.strip()
                        break
                    card = card.parent
                    if not card:
                        break

            status_v, status = STATUS_MAP.get(status_text, ("open", "모집 중"))

            # 썸네일
            thumb = ""
            img = a.find("img")
            if img:
                src = img.get("src", "")
                if src and "uploads" in src:
                    thumb = src if src.startswith("http") else BASE_URL + src

            items.append((slug, status_v, status, thumb))

        if len(items) >= MAX_ITEMS:
            break

    print(f"  → {len(items)}개 링크 수집")
    return items[:MAX_ITEMS]

# ── 상세 크롤 ─────────────────────────────────────────────────────────────────
def crawl_detail(client, slug: str, status_v: str, status: str, thumb: str) -> dict:
    url = f"{BASE_URL}/meet/{slug}"
    print(f"\n  → {url}")
    try:
        resp = client.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"    !! {e}"); return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # ── 제목 ──
    title = ""
    h3 = soup.find("h3")
    if h3:
        title = h3.get_text(strip=True)
    if not title:
        og = soup.find("meta", property="og:title")
        title = og["content"].replace(" - 닛커넥트", "").strip() if og else slug

    # ── 구조화 정보 파싱 (📆 모집기간, 🗓 운영기간, 👫 대상, 🌎 장소) ──
    recruit_period = ""
    operate_period = ""
    target         = ""
    place          = ""

    for li in soup.select("li"):
        txt = li.get_text(" ", strip=True)
        if "모집기간" in txt:
            recruit_period = re.sub(r'.*모집기간\s*', '', txt).strip()
        elif "운영기간" in txt:
            operate_period = re.sub(r'.*운영기간\s*', '', txt).strip()
        elif "대상" in txt and not target:
            target = re.sub(r'.*대상\s*', '', txt).strip()
        elif "장소" in txt and not place:
            place = re.sub(r'.*장소\s*', '', txt).strip()

    # ── 마감일 추출 (모집기간 끝 날짜) ──
    dday = ""
    deadline_str = ""
    if recruit_period:
        dates = re.findall(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', recruit_period)
        if len(dates) >= 2:
            y, mo, d = dates[1]
            dday = f"{y}.{mo.zfill(2)}.{d.zfill(2)}"
            deadline_str = f"마감 {dday}"
        elif len(dates) == 1:
            y, mo, d = dates[0]
            dday = f"{y}.{mo.zfill(2)}.{d.zfill(2)}"
            deadline_str = f"마감 {dday}"

    # ── 운영 기간 → weeks ──
    weeks = ""
    if operate_period:
        w_m = re.search(r'총\s*(\d+회)', operate_period)
        weeks = w_m.group(1) if w_m else operate_period[:30]

    # ── 장소 → method ──
    method = ""
    if place:
        if "온라인" in place:
            method = "온라인"
        elif "오프라인" in place:
            method = "오프라인"
        else:
            method = "오프라인"   # 장소명 있으면 오프라인

    # ── 본문 전체 텍스트 ──
    main_div = soup.find("main") or soup.find("article") or soup.body
    body_text = clean(main_div.get_text("\n", strip=True)) if main_div else ""

    region = extract_region(body_text + place, ORG_INFO["region"])
    qual   = extract_qual_chip(body_text + target)
    tag    = infer_tag_neet(title, body_text[:300])

    # ── 대상 → qual chip 보완 ──
    if not qual and target:
        if "누구나" in target:
            qual = "전체 신청 가능"
        elif "회원" in target:
            qual = "전체 신청 가능"

    chips = build_chips(status, qual, region, method)

    # ── og:image ──
    og_img = soup.find("meta", property="og:image")
    og_image = og_img["content"] if og_img else thumb

    curriculum = extract_curriculum(body_text)

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
            "qualification": qual or target,
            "curriculum":    curriculum,
            "org": {
                **ORG_INFO,
                "region": region,
                "homepage": url,
            }
        }
    }

    return result

# ── 메인 ─────────────────────────────────────────────────────────────────────
def main():
    results = []

    with httpx.Client(headers=HEADERS, follow_redirects=True) as client:
        items = collect_links(client)
        print(f"\n상세 크롤 시작 ({len(items)}개)...")

        for slug, status_v, status, thumb in items:
            r = crawl_detail(client, slug, status_v, status, thumb)
            if r:
                results.append(r)

    with open("neetconnect_programs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(results)}개 완료 → neetconnect_programs.json")
    for r in results:
        print(f"  [{r['tag']}] {r['title'][:40]}")
        print(f"         chips={r['chips']}  deadline={r['deadline']}")

if __name__ == "__main__":
    main()
