#!/usr/bin/env python3
"""
고립·은둔 청년 블로그 글 생성기
GitHub Actions 또는 로컬에서 실행 가능합니다.

필요한 환경변수:
  ANTHROPIC_API_KEY  — Anthropic API 키 (필수)

선택적 환경변수:
  BLOG_TONE          — 글의 방향 (공감형 | 정보형 | 희망형, 기본: 공감형)
  BLOG_KEYWORDS      — 쉼표로 구분된 키워드 목록 (기본: 사회적 고립,관계 단절)
  BLOG_LENGTH        — 목표 글자 수 (기본: 1000)
  OUTPUT_FILE        — 저장할 파일 경로 (기본: output/blog_post.md)
"""

import os
import sys
import json
import urllib.request
import urllib.error
import random
from datetime import datetime
from pathlib import Path


# ── 설정 ────────────────────────────────────────────────────────────

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

TONE = os.environ.get("BLOG_TONE", "공감형")
KEYWORDS_RAW = os.environ.get("BLOG_KEYWORDS", "사회적 고립,관계 단절")
KEYWORDS = [k.strip() for k in KEYWORDS_RAW.split(",") if k.strip()]
TARGET_LENGTH = int(os.environ.get("BLOG_LENGTH", "1000"))
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "output/blog_post.md")
GROK_RESEARCH_DIR = Path(__file__).parent / "grok-research-results"


# ── Grok 리서치 파일 로드 ────────────────────────────────────────────────────────

def load_random_grok_research() -> str:
    """grok-research-results 폴더에서 랜덤으로 마크다운 파일을 선택하고 읽습니다."""
    if not GROK_RESEARCH_DIR.exists():
        print(f"   ⚠️  {GROK_RESEARCH_DIR} 디렉토리가 없습니다.")
        return ""
    
    md_files = list(GROK_RESEARCH_DIR.glob("*.md"))
    if not md_files:
        print(f"   ⚠️  {GROK_RESEARCH_DIR}에 마크다운 파일이 없습니다.")
        return ""
    
    selected_file = random.choice(md_files)
    print(f"   📄 선택된 리서치: {selected_file.name}")
    
    try:
        content = selected_file.read_text(encoding="utf-8")
        return content
    except Exception as e:
        print(f"   ⚠️  파일 읽기 실패: {e}")
        return ""


# ── 참고 이야기 데이터베이스 ──────────────────────────────────────────────────

STORY_DB = [
    {
        "tags": ["통계", "사회적 고립", "NEET"],
        "title": "한국 고립·은둔 청년 약 54만 명 추산 — 전체 청년의 5%",
        "body": (
            "2023년 청년정책연구원 조사에서 19~34세 청년 중 약 54만 명이 "
            "사회적 고립 상태로 파악됐습니다. 이들은 평균 2.3년 이상 은둔 생활을 "
            "이어간 것으로 나타났습니다."
        ),
    },
    {
        "tags": ["당사자", "은둔형 외톨이", "취업 좌절"],
        "title": '"처음엔 딱 하루만 쉬려 했어요" — 은둔 4년차 청년의 고백',
        "body": (
            "취업 준비 실패 후 방 안에 틀어박힌 26세 남성의 인터뷰. "
            "외부 자극이 줄어들수록 다시 나가는 것이 더 두렵게 느껴진다는 "
            "악순환을 담담하게 설명합니다."
        ),
    },
    {
        "tags": ["정책", "정부 지원"],
        "title": "서울시 청년 마음건강 지원사업 — 고립 청년 대상 월 20만원 지원",
        "body": (
            "서울시는 2024년부터 사회적 고립 청년에게 심리상담비 및 사회참여 "
            "프로그램 비용을 지원합니다. 신청 첫 달 연인원 3,000명을 초과했습니다."
        ),
    },
    {
        "tags": ["당사자", "관계 단절", "정신건강"],
        "title": '"SNS는 늘 켜 있지만 대화 상대가 없어요" — 디지털 고립의 역설',
        "body": (
            "스마트폰을 하루 10시간 쓰면서도 진짜 대화를 못 한다는 청년들의 이야기. "
            "알고리즘이 만든 정보 거품 안에서 오히려 더 외로워지는 구조를 짚습니다."
        ),
    },
    {
        "tags": ["연구", "사회적 고립", "NEET"],
        "title": "은둔 기간이 길수록 재진입 비용 급증 — 경제적 손실 연 수조 원",
        "body": (
            "한국보건사회연구원 보고서에 따르면 1년 이상 은둔 상태가 지속될 경우 "
            "사회 복귀까지 평균 3배 이상의 시간과 비용이 소요되며, "
            "국가 차원의 GDP 손실도 상당합니다."
        ),
    },
    {
        "tags": ["회복", "희망형", "관계 단절"],
        "title": '"요리 모임 하나로 3년 만에 집 밖으로" — 당사자 회복 스토리',
        "body": (
            "주 1회 소규모 요리 커뮤니티에 참여하며 점진적으로 관계를 회복한 "
            "27세 여성의 사례. 목표 없이 그냥 같이 있는 시간이 "
            "회복의 시작이었다고 말합니다."
        ),
    },
    {
        "tags": ["가족", "은둔형 외톨이", "자기방 청년"],
        "title": '"무슨 말을 해도 상처가 돼서" — 은둔 자녀를 둔 부모의 하루',
        "body": (
            "자녀가 방에서 나오지 않는 걸 지켜보는 부모들의 무력감과 자책감. "
            "전문가들은 '왜 안 나와'보다 '뭐 먹고 싶어?'가 "
            "더 효과적인 첫 문장이라고 말합니다."
        ),
    },
    {
        "tags": ["정신건강", "사회적 고립"],
        "title": "고립 청년 70% '우울·불안 경험' — 정신건강 연계 지원 시급",
        "body": (
            "청년재단 설문에서 고립 경험 청년의 70.3%가 우울 또는 불안 증상을 "
            "경험했다고 답했습니다. 그러나 실제 상담을 받은 비율은 18%에 그쳤습니다."
        ),
    },
]


# ── 이야기 선택 로직 ──────────────────────────────────────────────────────

def select_stories(keywords: list[str], tone: str, max_stories: int = 4) -> list[dict]:
    """키워드와 톤에 맞는 이야기를 점수 기반으로 선택합니다."""
    scored = []
    for story in STORY_DB:
        score = 0
        for kw in keywords:
            if any(kw in tag for tag in story["tags"]):
                score += 2
            if kw in story["title"] or kw in story["body"]:
                score += 1
        if tone == "희망형" and "희망형" in story["tags"]:
            score += 3
        if tone == "정보형" and any(t in story["tags"] for t in ["통계", "연구", "정책"]):
            score += 2
        if tone == "공감형" and any(t in story["tags"] for t in ["당사자", "가족"]):
            score += 2
        scored.append((score, story))

    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [s for _, s in scored[:max_stories] if _ > 0]

    # 점수 0이어도 최소 2개는 보장
    if len(selected) < 2:
        selected = [s for _, s in scored[:2]]

    return selected


# ── Anthropic API 호출 ───────────────────────────────────────────────────────

def call_anthropic(prompt: str, api_key: str) -> str:
    payload = json.dumps({
        "model": MODEL,
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"API 오류 {e.code}: {body}") from e

    if "content" not in data or not data["content"]:
        raise RuntimeError(f"예상치 못한 응답 형식: {data}")

    return data["content"][0]["text"]


# ── 프롬프트 구성 ───────────────────────────────────────────────────────

def build_prompt(stories: list[dict], tone: str, keywords: list[str], length: int, grok_research: str = "") -> str:
    stories_text = "\n\n".join(
        f"[{i+1}] {s['title']}\n{s['body']}"
        for i, s in enumerate(stories)
    )

    grok_section = ""
    if grok_research.strip():
        grok_section = f"""

## 리서치 자료 (grok-research-results에서 선택됨)

{grok_research[:2000]}

---

위 리서치 자료를 참고하여 블로그 글에 깊이 있는 통찰을 담아주세요."""

    return f"""당신은 따뜻하고 공감 가는 블로그 글을 쓰는 한국어 작가입니다.

아래 참고 이야기를 바탕으로 "{tone}" 방향의 블로그 글을 작성해주세요.
다룰 키워드: {', '.join(keywords)}
목표 분량: 약 {length}자

참고 이야기:
{stories_text}{grok_section}

작성 규칙:
- Markdown 형식으로 작성하세요.
- 제목은 # 으로 시작하세요.
- 소제목(##)으로 단락을 2~3개 나눠주세요.
- 데이터와 당사자 목소리를 자연스럽게 녹여주세요.
- 독자가 "나만 이런 게 아니었구나"를 느낄 수 있도록 공감 언어를 사용하세요.
- 마지막은 따뜻한 마무리 문장으로 끝내주세요.
- 자료를 그대로 나열하지 말고, 이야기 흐름으로 재구성해주세요.
- 출처 목록은 따로 붙이지 마세요."""


# ── 메타데이터 헤더 생성 ────────────────────────────────────────────────────

def build_frontmatter(tone: str, keywords: list[str]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        "---\n"
        f"generated_at: {now}\n"
        f"tone: {tone}\n"
        f"keywords: [{', '.join(keywords)}]\n"
        f"model: {MODEL}\n"
        "---\n\n"
    )


# ── 메인 ───────────────────────────────────────────────────────────

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.", file=sys.stderr)
        sys.exit(1)

    print(f"📋 설정")
    print(f"   톤:        {TONE}")
    print(f"   키워드:    {', '.join(KEYWORDS)}")
    print(f"   목표 길이: {TARGET_LENGTH}자")
    print(f"   출력 파일: {OUTPUT_FILE}")
    print()

    print("📚 리서치 자료 로드 중...")
    grok_research = load_random_grok_research()
    print()

    print("🔍 이야기 선택 중...")
    stories = select_stories(KEYWORDS, TONE)
    for s in stories:
        print(f"   ✓ {s['title'][:40]}...")
    print()

    print("✍️  블로그 글 생성 중 (Claude API 호출)...")
    prompt = build_prompt(stories, TONE, KEYWORDS, TARGET_LENGTH, grok_research)
    blog_text = call_anthropic(prompt, api_key)
    print()

    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    full_content = build_frontmatter(TONE, KEYWORDS) + blog_text
    output_path.write_text(full_content, encoding="utf-8")

    char_count = len(blog_text)
    print(f"✅ 완료!")
    print(f"   파일:   {output_path.resolve()}")
    print(f"   글자수: {char_count:,}자")

    # GitHub Actions summary 출력
    github_output = os.environ.get("GITHUB_STEP_SUMMARY", "")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"## 📝 블로그 글 생성 완료\n\n")
            f.write(f"| 항목 | 내용 |\n|------|------|\n")
            f.write(f"| 톤 | {TONE} |\n")
            f.write(f"| 키워드 | {', '.join(KEYWORDS)} |\n")
            f.write(f"| 글자 수 | {char_count:,}자 |\n")
            f.write(f"| 출력 파일 | `{OUTPUT_FILE}` |\n\n")
            f.write("### 생성된 글 미리보기\n\n")
            preview = blog_text[:500] + ("..." if len(blog_text) > 500 else "")
            f.write(preview + "\n")


if __name__ == "__main__":
    main()
