"""
crawler_utils.py — 공통 유틸리티
---------------------------------
모든 크롤러에서 import해서 사용.
- 텍스트 파싱 헬퍼
- 데이터 구조 빌더
"""

import re
import httpx

# ────────────────────────────────────────────────────────────
# 상수
# ────────────────────────────────────────────────────────────
REGION_LIST = [
    "서울", "경기", "인천", "부산", "대구", "광주", "대전",
    "울산", "세종", "강원", "충북", "충남", "전북", "전남",
    "경북", "경남", "제주", "전국",
]

QUAL_KEYWORDS = [
    ("전체 신청 가능", ["누구나", "제한 없", "상관없이", "모두 신청"]),
    ("은둔·고립 청년",  ["은둔", "고립", "외톨이", "히키코모리"]),
    ("무직·구직자",    ["무직", "무업", "니트", "NEET", "구직"]),
    ("청년",           ["청년", "만 19", "만 34", "만 39"]),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# ────────────────────────────────────────────────────────────
# 텍스트 헬퍼
# ────────────────────────────────────────────────────────────
def clean(text: str) -> str:
    return re.sub(r'\n{3,}', '\n\n', text).strip()

def extract_deadline(text: str, post_date: str = "") -> tuple:
    """
    마감일을 최대한 추출. 못 찾으면 post_date(게시날짜)로 추측.
    반환: (deadline_display, dDay)

    탐색 순서:
    1. 마감/신청 기간 문맥 근처 날짜  (~MM/DD, 까지, 마감 등)
    2. YYYY.MM.DD / YYYY-MM-DD 형식 날짜
    3. 한국어 날짜 (MM월 DD일)
    4. 상시/연중 키워드
    5. post_date 있으면 +30일 추측
    6. 빈 문자열
    """
    from datetime import datetime, timedelta

    # ── 1. 마감 문맥 근처 날짜 (~까지, 마감일, 신청기간 끝) ──
    # ~YYYY/MM/DD, ~MM/DD, YYYY.MM.DD까지 등
    ctx_patterns = [
        r'[~～]\s*(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})',   # ~2026.05.30
        r'[~～]\s*(\d{1,2})[./](\d{1,2})',                    # ~5/30 또는 ~05.30
        r'(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})\s*(?:까지|마감|접수마감)',
        r'(?:마감일|신청마감|접수마감|모집마감|신청기간\s*종료)[^\d]*(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})',
        r'(?:신청기간|접수기간|모집기간)[^\d]*\d{4}[.\-/]\d{1,2}[.\-/]\d{1,2}\s*[~～\-]\s*(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})',
    ]
    for pat in ctx_patterns:
        m = re.search(pat, text)
        if m:
            groups = m.groups()
            if len(groups) == 3:
                y, mo, d = groups
                # ~MM/DD 패턴은 연도 없음 → 2026 기본
                if len(y) <= 2:
                    y = "2026"
                s = f"{y}.{mo.zfill(2)}.{d.zfill(2)}"
                return f"마감 {s}", s
            elif len(groups) == 2:
                mo, d = groups
                s = f"2026.{mo.zfill(2)}.{d.zfill(2)}"
                return f"마감 {s}", s

    # ── 2. YYYY.MM.DD / YYYY-MM-DD 형식 — 가장 마지막 날짜 (기간 끝) ──
    all_dates = re.findall(r'(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})', text)
    if all_dates:
        # 여러 날짜 중 가장 마지막 날짜를 마감으로 추정
        parsed = []
        for y, mo, d in all_dates:
            try:
                dt = datetime(int(y), int(mo), int(d))
                parsed.append((dt, y, mo, d))
            except Exception:
                continue
        if parsed:
            parsed.sort(key=lambda x: x[0])
            # 현재보다 미래 날짜 우선, 없으면 가장 최근 날짜
            now = datetime.now()
            future = [p for p in parsed if p[0] >= now]
            chosen = future[0] if future else parsed[-1]
            _, y, mo, d = chosen
            s = f"{y}.{mo.zfill(2)}.{d.zfill(2)}"
            return f"마감 {s}", s

    # ── 3. 한국어 날짜 (MM월 DD일) ──
    m = re.search(r'(\d{1,2})월\s*(\d{1,2})일', text)
    if m:
        s = f"2026.{m.group(1).zfill(2)}.{m.group(2).zfill(2)}"
        return f"마감 {s}", s

    # ── 4. 상시/연중 ──
    if re.search(r'상시|연중|수시', text):
        return "상시 모집", "상시"

    # ── 5. 마감 키워드만 있고 날짜 없음 ──
    if re.search(r'마감|종료|접수\s*마감', text):
        return "마감", "마감"

    # ── 6. post_date로 추측 (+30일) ──
    if post_date:
        try:
            # YYYY-MM-DD 또는 YYYY.MM.DD 형식
            post_date_clean = re.sub(r'[.\-/]', '-', post_date.strip()[:10])
            dt = datetime.strptime(post_date_clean, "%Y-%m-%d")
            estimated = dt + timedelta(days=30)
            s = estimated.strftime("%Y.%m.%d")
            return f"마감 {s} (추정)", s
        except Exception:
            pass

    return "", ""

def extract_region(text: str, default: str = "") -> str:
    for r in REGION_LIST:
        if r in text:
            return r
    return default

def extract_method(text: str) -> str:
    online  = bool(re.search(r'온라인|비대면|zoom|줌|유튜브', text, re.I))
    offline = bool(re.search(r'오프라인|대면|현장|방문|직접', text, re.I))
    if online and offline: return "온·오프라인"
    if online:  return "온라인"
    if offline: return "오프라인"
    return ""

def extract_qual_chip(text: str) -> str:
    for label, keywords in QUAL_KEYWORDS:
        if any(kw in text for kw in keywords):
            return label
    return ""

def infer_status(text: str) -> tuple:
    if re.search(r'마감|종료|접수\s*마감|신청\s*마감', text):
        return "closed", "마감"
    if re.search(r'모집\s*중|신청\s*가능|접수\s*중|모집합니다|신청\s*받', text):
        return "open", "모집 중"
    return "open", "모집 중"

def build_chips(status: str, qual: str, region: str, method: str) -> list:
    chips = []
    if status == "마감": chips.append("마감")
    if qual:   chips.append(qual)
    if region: chips.append(region)
    if method: chips.append(method)
    return chips

def extract_weeks(text: str) -> str:
    m = re.search(r'\d+주\s*[·/]\s*주\s*\d+회|\d+주\s*프로그램|\d+주\s*과정|\d+주', text)
    return m.group(0).strip() if m else ""

def extract_curriculum(text: str) -> list:
    items = []
    for m in re.finditer(r'(\d+[~\-～]\d*\s*주차?|\d+\s*주차)[^\n]*\n([^\n]+)', text):
        items.append({"weeks": m.group(1).strip(), "desc": m.group(2).strip()})
        if len(items) >= 8: break
    return items

def extract_title_from_page(page, org_name: str = "") -> str:
    """Playwright page에서 제목 추출. 반드시 무언가를 반환."""
    for sel in ["h1", "h2", "h3", ".title", ".post-title",
                "[class*='title']", "[class*='heading']"]:
        for el in page.locator(sel).all():
            t = el.inner_text().strip()
            if 3 < len(t) < 100 and org_name not in t:
                return t
    raw = page.title()
    for noise in [org_name, "–", "-", "|", "·"]:
        raw = raw.replace(noise, "").strip()
    return raw or page.url.rstrip("/").split("/")[-1]

def infer_tag(title: str, body: str) -> str:
    combined = title + body[:300]
    if any(k in combined for k in ["상담", "심리", "마음돌봄"]):          return "상담"
    if any(k in combined for k in ["일경험", "취업", "직무", "일자리"]):  return "일경험"
    if any(k in combined for k in ["모임", "자조", "커뮤니티"]):           return "자조모임"
    if any(k in combined for k in ["회복", "치유", "힐링"]):               return "회복 프로그램"
    return "프로그램"
