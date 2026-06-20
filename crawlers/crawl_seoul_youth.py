"""
youth.seoul.go.kr (서울청년센터) — 프로그램 신청 크롤러
--------------------------------------------------------
실행:
  pip install httpx beautifulsoup4
  python crawl_seoul_youth.py

  ※ SSR — Playwright 불필요
  ※ 목록에서 모든 정보 추출 (상세 링크가 JS라 목록 전용)

결과: seoul_youth_programs.json

구조:
  - 목록: /orang/infoData/sprtInfo/list.do?key=2309210005&pageIndex=N
  - 총 3,890건 / 325페이지 — 최신 2페이지(24건)만 수집
  - 항목당: 상태, 유형, 제목, 신청기간, 진행일정, 장소 포함
  - 유형: 일자리/진로/창업/주거/금융/교육/마음건강/신체건강/생활지원/문화·예술 등
  - 공간: 강동/강북/강서/관악 등 서울 각 구 센터
"""

import json
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import httpx
from bs4 import BeautifulSoup
from crawler_utils import (
    clean, extract_deadline, extract_method,
    extract_qual_chip, build_chips,
)

BASE_URL  = "https://youth.seoul.go.kr"
LIST_URL  = f"{BASE_URL}/orang/infoData/sprtInfo/list.do"
MAX_PAGES = 2
MAX_ITEMS = 20

ORG_NAME = "서울청년센터"
ORG_INFO = {
    "name":     ORG_NAME,
    "region":   "서울",
    "phone":    "02-731-2120",
    "email":    "",
    "kakao":    "",
    "homepage": f"{BASE_URL}/orang/index.do",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": f"{BASE_URL}/orang/infoData/sprtInfo/list.do?key=2309210005",
}

# 유형 → tag 매핑
TYPE_TAG = {
    "일자리": "일경험",
    "진로":   "일경험",
    "창업":   "창업",
    "주거":   "생활지원",
    "금융":   "생활지원",
    "교육":   "교육",
    "마음건강": "상담",
    "신체건강": "프로그램",
    "생활지원": "생활지원",
    "문화/예술": "문화예술",
    "문화·예술": "문화예술",
    "대외활동": "프로그램",
    "공간":   "프로그램",
    "사회참여": "자조모임",
    "커뮤니티": "자조모임",
}

def parse_status(status_text: str) -> tuple:
    s = status_text.strip()
    if "모집중" in s or "접수중" in s:
        return "open", "모집 중"
    if "마감" in s or "종료" in s or "접수종료" in s:
        return "closed", "마감"
    return "open", "모집 중"

# ── 목록 파싱 ─────────────────────────────────────────────────────────────────
def collect_items(client) -> list:
    items = []
    seen  = set()

    for p_num in range(1, MAX_PAGES + 1):
        url = f"{LIST_URL}?key=2309210005&pageIndex={p_num}"
        print(f"  [목록 p{p_num}] {url}")
        try:
            resp = client.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"    !! {e}"); break

        soup = BeautifulSoup(resp.text, "html.parser")

        # 각 프로그램 항목: 목록 li 안에 상태, 제목, 기간, 장소 포함
        # 텍스트 파싱으로 추출
        raw_text = soup.get_text("\n")

        # 패턴: [상태] **[유형] 제목** - 신청기간 YYYY-MM-DD ~ YYYY-MM-DD - 진행일정 ... - 장소 ...
        # 목록 구조 파싱
        for a in soup.select("a"):
            text = a.get_text("\n", strip=True)
            if not text or len(text) < 10:
                continue

            # 상태 추출
            status_text = ""
            m_status = re.search(r'^(모집중|마감|접수중|접수종료)', text)
            if not m_status:
                continue
            status_text = m_status.group(1)
            status_v, status = parse_status(status_text)

            # 유형 추출: [일자리], [진로] 등
            m_type = re.search(r'\[([가-힣/·]+)\]', text)
            prog_type = m_type.group(1) if m_type else ""
            tag = TYPE_TAG.get(prog_type, "프로그램")

            # 제목 추출: 유형 이후 첫 줄
            title = ""
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for i, line in enumerate(lines):
                if prog_type and prog_type in line:
                    # 유형 태그 제거하고 나머지가 제목
                    t = re.sub(r'\[[가-힣/·]+\]\s*', '', line).strip()
                    if t and len(t) > 3:
                        title = t
                        break
            if not title:
                # 두 번째 줄 시도
                for line in lines[1:4]:
                    if len(line) > 5 and "신청기간" not in line and "진행일정" not in line:
                        title = line
                        break

            if not title or title in seen:
                continue
            seen.add(title)

            # 신청기간 추출
            recruit_period = ""
            m_recruit = re.search(r'신청기간\s*([\d\-]+\s*~\s*[\d\-]+)', text)
            if m_recruit:
                recruit_period = m_recruit.group(1).strip()

            # 진행일정 추출
            operate_period = ""
            m_operate = re.search(r'진행일정\s*(.+?)(?:\n|장소|$)', text)
            if m_operate:
                operate_period = m_operate.group(1).strip()

            # 장소 추출
            place = ""
            m_place = re.search(r'장소\s*(.+?)(?:\n|$)', text)
            if m_place:
                place = m_place.group(1).strip()

            # 마감일: 신청기간 끝 날짜
            dday, deadline_str = "", ""
            dates = re.findall(r'(\d{4}-\d{2}-\d{2})', recruit_period)
            if len(dates) >= 2:
                dday = dates[1].replace("-", ".")
                deadline_str = f"마감 {dday}"
            elif len(dates) == 1:
                dday = dates[0].replace("-", ".")
                deadline_str = f"마감 {dday}"

            # 운영 기간 → weeks
            weeks = ""
            if operate_period and operate_period != "상시":
                op_dates = re.findall(r'(\d{4}-\d{2}-\d{2})', operate_period)
                if op_dates:
                    weeks = " ~ ".join(op_dates).replace("-", ".")
            elif operate_period == "상시":
                weeks = "상시"

            # 지역: 장소에서 서울 구 이름 추출
            region = "서울"
            gu_list = ["강동", "강북", "강서", "관악", "광진", "금천", "노원",
                       "동대문", "마포", "서초", "성동", "은평", "영등포",
                       "양천", "도봉", "성북", "구로", "중구"]
            for gu in gu_list:
                if gu in place or gu in title:
                    region = f"서울 {gu}"
                    break

            method = extract_method(place + title)
            qual   = extract_qual_chip(title)
            chips  = build_chips(status, qual, region, method)
            if prog_type and f"#{prog_type}" not in chips:
                chips.append(f"#{prog_type}")

            items.append({
                "tag":           tag,
                "dDay":          dday,
                "title":         title,
                "org":           f"서울청년센터 ({place})" if place else ORG_NAME,
                "status":        status,
                "statusVariant": status_v,
                "chips":         chips,
                "weeks":         weeks,
                "deadline":      deadline_str,
                "sourceUrl":     url,
                "detail": {
                    "intro":         f"{prog_type} 프로그램. 신청기간: {recruit_period}",
                    "description":   f"진행일정: {operate_period} | 장소: {place}",
                    "qualification": qual,
                    "curriculum":    [],
                    "org": {
                        **ORG_INFO,
                        "name":   f"서울청년센터 ({place})" if place else ORG_NAME,
                        "region": region,
                        "homepage": url,
                    }
                }
            })

            if len(items) >= MAX_ITEMS:
                break

        if len(items) >= MAX_ITEMS:
            break

    print(f"  → {len(items)}개 수집")
    return items[:MAX_ITEMS]

# ── 메인 ─────────────────────────────────────────────────────────────────────
def main():
    with httpx.Client(headers=HEADERS, follow_redirects=True) as client:
        items = collect_items(client)

    with open("seoul_youth_programs.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(items)}개 완료 → seoul_youth_programs.json")
    for r in items:
        print(f"  [{r['tag']}] {r['title'][:40]}")
        print(f"         chips={r['chips']}  deadline={r['deadline']}")

if __name__ == "__main__":
    main()
