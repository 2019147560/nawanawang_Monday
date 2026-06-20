"""
jejuyouth.com (제주청소년활동진흥센터) — SSL 우회 크롤러
---------------------------------------------------------
실행:
  pip install httpx beautifulsoup4
  python crawl_jejuyouth.py

  ※ SSL 인증서 검증 비활성화 (verify=False) — 서버 TLS 설정 오류 우회
  ※ 로컬 환경에서만 동작 가능

결과: jejuyouth_programs.json

크롤 대상 (그누보드 게시판):
  1_2_1_1  청소년 프로그램
  1_2_2_1  청소년 활동 프로그램
  4_1_1_1  공지사항
"""

import json
import re
import sys
import os
import urllib3
sys.path.insert(0, os.path.dirname(__file__))

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import httpx
from bs4 import BeautifulSoup
from crawler_utils import (
    clean, extract_deadline, extract_region, extract_method,
    extract_qual_chip, infer_status, build_chips,
    extract_weeks, extract_curriculum, infer_tag,
)

BASE_URL  = "https://jejuyouth.com"
MAX_PAGES = 2
MAX_ITEMS = 20

BOARDS = [
    ("1_2_1_1", "청소년 프로그램"),
    ("1_2_2_1", "청소년 활동"),
    ("4_1_1_1", "공지사항"),
]

ORG_NAME = "제주청소년활동진흥센터"
ORG_INFO = {
    "name":     ORG_NAME,
    "region":   "제주",
    "phone":    "064-729-5880",
    "email":    "",
    "kakao":    "",
    "homepage": BASE_URL,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9",
}

# ── 목록 수집 ─────────────────────────────────────────────────────────────────
def collect_links(client, bo_table: str, board_tag: str, seen: set) -> list:
    items = []

    for p_num in range(1, MAX_PAGES + 1):
        page_param = (p_num - 1) * 10  # 그누보드 page 파라미터는 offset
        url = (f"{BASE_URL}/bbs/board.php"
               f"?bo_table={bo_table}&page={p_num}")
        print(f"  [목록 {bo_table} p{p_num}] {url}")
        try:
            resp = client.get(url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"    !! {e}"); break

        soup = BeautifulSoup(resp.text, "html.parser")

        # 그누보드: wr_id 파라미터로 개별 글 접근
        found = 0
        for a in soup.select("a[href*='wr_id']"):
            href = a.get("href", "")
            if "bo_table" not in href:
                continue
            m = re.search(r'wr_id=(\d+)', href)
            if not m:
                continue
            wr_id = m.group(1)
            detail_url = (f"{BASE_URL}/bbs/board.php"
                          f"?bo_table={bo_table}&wr_id={wr_id}")
            if detail_url in seen:
                continue
            seen.add(detail_url)

            # 썸네일
            thumb = ""
            img = a.find("img")
            if img:
                src = img.get("src", "")
                thumb = src if src.startswith("http") else BASE_URL + src

            # 제목 텍스트
            title_text = a.get_text(strip=True)

            items.append((detail_url, thumb, title_text, board_tag))
            found += 1

        if found == 0:
            break
        if len(items) >= MAX_ITEMS:
            break

    return items

# ── 상세 크롤 ─────────────────────────────────────────────────────────────────
def crawl_detail(client, url: str, thumb: str, title_hint: str, board_tag: str) -> dict:
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
    title = re.sub(r'\s*[-|]\s*제주청소년.*$', '', og_title).strip() if og_title else ""
    if not title:
        # 그누보드 제목 셀렉터
        h = (soup.find(class_=re.compile(r'view.tit|board.view.tit|bv_subject'))
             or soup.find("h1") or soup.find("h2"))
        title = h.get_text(strip=True) if h else title_hint

    # ── 본문 ──
    body_el = (soup.find(id=re.compile(r'bo_v_con|view_content'))
               or soup.find(class_=re.compile(r'view.cont|bo_v_con|board.view.con'))
               or soup.find("article") or soup.find("main"))
    body_text = clean(body_el.get_text("\n") if body_el else soup.get_text("\n"))

    og_desc = re.sub(r'&nbsp;|&amp;', ' ', get_meta("og:description"))
    full_text = og_desc if len(og_desc) > 100 else body_text

    deadline_str, dday = extract_deadline(full_text)
    region             = extract_region(full_text, ORG_INFO["region"])
    method             = extract_method(full_text)
    qual               = extract_qual_chip(full_text)
    weeks              = extract_weeks(full_text)
    curriculum         = extract_curriculum(body_text)
    tag                = board_tag
    status_v, status   = infer_status(full_text)
    chips              = build_chips(status, qual, region, method)

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

# ── 메인 ─────────────────────────────────────────────────────────────────────
def main():
    results   = []
    all_items = []
    seen      = set()

    # SSL 검증 비활성화 클라이언트
    with httpx.Client(
        headers=HEADERS,
        follow_redirects=True,
        verify=False,          # ← SSL 인증서 검증 skip
        timeout=15,
    ) as client:

        # 먼저 접속 테스트
        print("접속 테스트 중...")
        try:
            test = client.get(f"{BASE_URL}/bbs/board.php?bo_table=1_2_1_1")
            if "보안절차" in test.text or "Please prove" in test.text:
                print("❌ 봇 감지 화면 — 로컬 Playwright가 필요합니다.")
                return
            print(f"✅ 접속 성공 (status {test.status_code})")
        except Exception as e:
            print(f"❌ 접속 실패: {e}")
            return

        for bo_table, board_tag in BOARDS:
            items = collect_links(client, bo_table, board_tag, seen)
            all_items.extend(items)
            if len(all_items) >= MAX_ITEMS:
                break

        all_items = all_items[:MAX_ITEMS]
        print(f"\n상세 크롤 시작 ({len(all_items)}개)...")

        for url, thumb, title_hint, board_tag in all_items:
            r = crawl_detail(client, url, thumb, title_hint, board_tag)
            if r:
                results.append(r)

    if not results:
        print("\n⚠️  결과 없음 — SSL 우회도 차단된 경우 Playwright headless=False 방식이 필요합니다.")
        return

    with open("jejuyouth_programs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(results)}개 완료 → jejuyouth_programs.json")
    for r in results:
        print(f"  [{r['tag']}] {r['title'][:40]}")
        print(f"         chips={r['chips']}  deadline={r['deadline']}")

if __name__ == "__main__":
    main()
