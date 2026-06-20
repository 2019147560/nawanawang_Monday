"""
youth.incheon.go.kr (유유기지 인천) — 프로그램 신청 크롤러
-----------------------------------------------------------
실행:
  pip install httpx beautifulsoup4
  python crawl_incheon.py

  ※ SSR — Playwright 불필요

결과: incheon_programs.json

구조:
  - 목록: /program/programInfoList.do?cate2=all&prgmdiv=inuu&pgno=N
  - 상세: /program/programInfoDetail.do?prgm_seq={숫자}
  - 목록에 제목/신청기간/진행기간/카테고리/상태/썸네일 전부 포함
  - 카테고리: 문화예술 / 진로·취업 / 창업 / 생활지원 / 소모임
  - 상태: 접수중 / 마감 / 강의 마감 / 특강 마감 등
"""

import json
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import httpx
from bs4 import BeautifulSoup
from crawler_utils import (
    clean, extract_method, extract_qual_chip, build_chips,
    extract_weeks, extract_curriculum,
)

BASE_URL   = "https://youth.incheon.go.kr"
LIST_URL   = f"{BASE_URL}/program/programInfoList.do"
DETAIL_URL = f"{BASE_URL}/program/programInfoDetail.do"
MAX_PAGES  = 2
MAX_ITEMS  = 20

ORG_NAME = "유유기지 인천 (인천광역시 청년지원센터)"
ORG_INFO = {
    "name":     ORG_NAME,
    "region":   "인천",
    "phone":    "032-246-1380",
    "email":    "",
    "kakao":    "",
    "homepage": f"{BASE_URL}/space/inuu",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": f"{BASE_URL}/space/inuu/support/program_request.jsp",
}

# 카테고리 → tag 매핑
CATE_TAG = {
    "문화예술": "문화예술",
    "진로·취업": "일경험",
    "창업":     "창업",
    "생활지원": "생활지원",
    "소모임":   "자조모임",
}

# 상태 텍스트 → (statusVariant, status)
def parse_status(status_text: str) -> tuple:
    s = status_text.strip()
    if "접수중" in s:
        return "open", "모집 중"
    if "마감" in s or "접수종료" in s or "정원초과" in s:
        return "closed", "마감"
    return "open", "모집 중"

# ── 목록 수집 ─────────────────────────────────────────────────────────────────
def collect_items(client) -> list:
    """
    목록에서 바로 대부분의 정보를 추출.
    반환: list of dict (상세 크롤 전 기본 데이터)
    """
    items = []
    seen  = set()

    for p_num in range(1, MAX_PAGES + 1):
        url = f"{LIST_URL}?cate2=all&prgmdiv=inuu&pgno={p_num}"
        print(f"  [목록 p{p_num}] {url}")
        try:
            resp = client.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"    !! {e}"); break

        soup = BeautifulSoup(resp.text, "html.parser")

        # 각 프로그램 카드: li 단위
        for li in soup.select("ul li"):
            # prgm_seq 링크 찾기
            a = li.find("a", href=re.compile(r'prgm_seq=\d+'))
            if not a:
                continue
            m = re.search(r'prgm_seq=(\d+)', a["href"])
            if not m:
                continue
            seq = m.group(1)
            detail_url = f"{DETAIL_URL}?prgm_seq={seq}&cate2=all&prgmdiv=inuu"
            if detail_url in seen:
                continue
            seen.add(detail_url)

            # ── 제목 ──
            title_el = li.find(class_=re.compile(r'tit|title|name')) or a
            title = title_el.get_text(strip=True) if title_el else ""
            # 이미지 alt에서도 시도
            if not title:
                img = li.find("img")
                if img:
                    title = img.get("alt", "").replace("모집마감", "").strip()

            # ── 썸네일 ──
            thumb = ""
            img = li.find("img")
            if img:
                src = img.get("src", "")
                thumb = src if src.startswith("http") else BASE_URL + src

            # ── 신청기간 / 진행기간 ──
            recruit_period = ""
            operate_period = ""
            for span in li.find_all(["span", "li", "p", "dd"]):
                t = span.get_text(strip=True)
                if "신청기간" in t:
                    recruit_period = re.sub(r'신청기간\s*', '', t).strip()
                elif "진행기간" in t:
                    operate_period = re.sub(r'진행기간\s*', '', t).strip()

            # ── 마감일 (신청기간 끝 날짜) ──
            dday, deadline_str = "", ""
            dates = re.findall(r'(\d{4}-\d{2}-\d{2})', recruit_period)
            if len(dates) >= 2:
                dday = dates[1].replace("-", ".")
                deadline_str = f"마감 {dday}"
            elif len(dates) == 1:
                dday = dates[0].replace("-", ".")
                deadline_str = f"마감 {dday}"

            # ── 카테고리 ──
            category = ""
            cate_el = li.find(string=re.compile(r'#(문화예술|진로|취업|창업|생활지원|소모임)'))
            if cate_el:
                category = cate_el.strip().lstrip("#")
            else:
                for cate in CATE_TAG:
                    if cate in li.get_text():
                        category = cate
                        break

            # ── 상태 ──
            status_text = ""
            for el in li.find_all(class_=re.compile(r'state|status|badge|label')):
                status_text = el.get_text(strip=True)
                if status_text:
                    break
            if not status_text:
                txt = li.get_text()
                if "접수중" in txt:
                    status_text = "접수중"
                elif "접수종료" in txt or "마감" in txt or "정원초과" in txt:
                    status_text = "마감"

            status_v, status = parse_status(status_text)
            tag = CATE_TAG.get(category, "프로그램")

            items.append({
                "seq":            seq,
                "detail_url":     detail_url,
                "title":          title,
                "thumb":          thumb,
                "recruit_period": recruit_period,
                "operate_period": operate_period,
                "dday":           dday,
                "deadline_str":   deadline_str,
                "category":       category,
                "tag":            tag,
                "status_v":       status_v,
                "status":         status,
            })

        if len(items) >= MAX_ITEMS:
            break

    print(f"  → {len(items)}개 수집")
    return items[:MAX_ITEMS]

# ── 상세 크롤 ─────────────────────────────────────────────────────────────────
def crawl_detail(client, item: dict) -> dict:
    url = item["detail_url"]
    print(f"\n  → {url}")
    try:
        resp = client.get(url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"    !! {e}"); return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # 본문
    body_el = (soup.find(id=re.compile(r'content|con'))
               or soup.find(class_=re.compile(r'view.cont|detail.cont|program.detail'))
               or soup.find("main"))
    body_text = clean(body_el.get_text("\n") if body_el else soup.get_text("\n"))

    method = extract_method(body_text)
    qual   = extract_qual_chip(body_text)
    weeks  = extract_weeks(body_text)
    curriculum = extract_curriculum(body_text)

    # operate_period → weeks 보완
    if not weeks and item["operate_period"]:
        weeks = item["operate_period"]

    # chips: [상태, 자격, 지역, 방식, 카테고리]
    chips = []
    if item["status"] == "마감":
        chips.append("마감")
    if qual:
        chips.append(qual)
    chips.append(ORG_INFO["region"])
    if method:
        chips.append(method)
    if item["category"] and item["category"] not in chips:
        chips.append(f"#{item['category']}")

    phone_m = re.search(r'(\d{2,3}[-)\s]\d{3,4}[-]\d{4})', body_text)
    email_m = re.search(r'([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})', body_text)

    # og:image
    og_img = soup.find("meta", property="og:image")
    og_image = (BASE_URL + og_img["content"] if og_img and og_img.get("content", "").startswith("/")
                else (og_img["content"] if og_img else item["thumb"]))

    result = {
        "tag":           item["tag"],
        "dDay":          item["dday"],
        "title":         item["title"],
        "org":           ORG_NAME,
        "status":        item["status"],
        "statusVariant": item["status_v"],
        "chips":         chips,
        "weeks":         weeks,
        "deadline":      item["deadline_str"],
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
                "homepage": url,
            }
        }
    }

    return result

# ── 메인 ─────────────────────────────────────────────────────────────────────
def main():
    results = []

    with httpx.Client(headers=HEADERS, follow_redirects=True) as client:
        items = collect_items(client)
        print(f"\n상세 크롤 시작 ({len(items)}개)...")
        for item in items:
            r = crawl_detail(client, item)
            if r:
                results.append(r)

    with open("incheon_programs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(results)}개 완료 → incheon_programs.json")
    for r in results:
        print(f"  [{r['tag']}] {r['title'][:40]}")
        print(f"         chips={r['chips']}  deadline={r['deadline']}")

if __name__ == "__main__":
    main()
