#!/usr/bin/env python3
"""
고립·은둔 청년 블로그 글 생성기
GitHub Actions 또는 로컬에서 실행 가능합니다.

동작 방식:
  grok-research-results 폴더(그록 조사 스크립트가 만들어낸 .md 결과물들)에서
  랜덤으로 하나를 골라 그 내용을 실제 소스 자료로 삼아 블로그 글을 씁니다.
  즉, 이 글은 지어낸 내용이 아니라 실제 조사 파일에 있는 사실을 재구성한 것입니다.

필요한 환경변수:
  ANTHROPIC_API_KEY  — Anthropic API 키 (필수)
선택적 환경변수:
  BLOG_TONE          — 글의 방향 (공감형 | 정보형 | 희망형, 기본: 공감형)
  BLOG_KEYWORDS      — 쉼표로 구분된 강조 키워드 목록 (기본: 없음. 소스 선택에는 쓰이지 않고,
                        글 작성 시 강조하면 좋은 키워드로만 전달됩니다)
  BLOG_LENGTH        — 목표 글자 수 (기본: 3000)
  OUTPUT_FILE        — 저장할 파일 경로 (기본: output/blog_post.md)
  SOURCE_DIR         — grok-research-results 폴더 경로를 직접 지정 (기본: 아래 후보 경로들을
                        순서대로 탐색: $GITHUB_WORKSPACE/grok-research-results ,
                        ./grok-research-results , ~/grok-research-results)
"""

import os
import sys
import json
import random
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# ── 설정 ──────────────────────────────────────────────────────────────────────
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"

TONE = os.environ.get("BLOG_TONE", "공감형")
KEYWORDS_RAW = os.environ.get("BLOG_KEYWORDS", "")
KEYWORDS = [k.strip() for k in KEYWORDS_RAW.split(",") if k.strip()]
TARGET_LENGTH = int(os.environ.get("BLOG_LENGTH", "4000"))
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "output/blog_post.md")

MAX_SOURCE_CHARS = 6000  # 프롬프트에 넣을 소스 자료 최대 길이(안전장치)


# ── 소스 자료 탐색/선택 ────────────────────────────────────────────────────────
def find_source_dir() -> Path:
    """grok-research-results 폴더를 여러 후보 경로에서 찾습니다."""
    candidates = []

    env_dir = os.environ.get("SOURCE_DIR")
    if env_dir:
        candidates.append(Path(env_dir))

    workspace = os.environ.get("GITHUB_WORKSPACE")
    if workspace:
        candidates.append(Path(workspace) / "grok-research-results")

    candidates.append(Path.cwd() / "grok-research-results")
    candidates.append(Path.home() / "grok-research-results")

    for c in candidates:
        if c.is_dir():
            return c

    tried = "\n".join(f"  - {c}" for c in candidates)
    raise FileNotFoundError(
        "grok-research-results 폴더를 찾을 수 없습니다. 다음 경로들을 확인했습니다:\n"
        f"{tried}\n"
        "SOURCE_DIR 환경변수로 직접 경로를 지정할 수 있습니다."
    )


def pick_random_source(source_dir: Path) -> Path:
    """폴더(하위 폴더 포함) 안의 .md 파일 중 하나를 무작위로 선택합니다."""
    md_files = sorted(source_dir.rglob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"'{source_dir}' 안에 .md 파일이 없습니다.")
    return random.choice(md_files)


def extract_title(md_text: str) -> str:
    """소스 md에서 '제목:'으로 시작하는 줄을 찾아 제목을 뽑아냅니다."""
    for line in md_text.splitlines():
        line = line.strip()
        if line.startswith("제목:"):
            return line[len("제목:"):].strip()
    for line in md_text.splitlines():
        line = line.strip()
        if line and not line.startswith("---"):
            return line
    return "(제목 없음)"


# ── Anthropic API 호출 ────────────────────────────────────────────────────────
def call_anthropic(prompt: str, api_key: str) -> str:
    payload = json.dumps({
        "model": MODEL,
        "max_tokens": 4000,
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


# ── 프롬프트 구성 ─────────────────────────────────────────────────────────────
def build_prompt(source_content: str, source_title: str, tone: str, keywords: list[str], length: int) -> str:
    trimmed = source_content.strip()
    truncated = len(trimmed) > MAX_SOURCE_CHARS
    if truncated:
        trimmed = trimmed[:MAX_SOURCE_CHARS] + "\n...(이하 생략)"

    keyword_line = f"\n강조하면 좋은 키워드(선택 사항, 없으면 무시): {', '.join(keywords)}" if keywords else ""

    return f"""당신은 따뜻하고 공감 가는 블로그 글을 쓰는 한국어 작가입니다.
아래 [원본 조사 자료]는 실제로 조사된 내용입니다. 이 자료에 있는 사실(통계, 사례, 기관명, 인용 등)만 사용해서 "{tone}" 방향의 블로그 글을 작성해주세요.
자료에 없는 사실이나 수치를 새로 지어내지 마세요. 자료에 확실치 않다고 표시된 내용은 그 뉘앙스를 그대로 유지해주세요.

목표 분량: 약 {length}자{keyword_line}

[원본 조사 자료 - 제목: {source_title}]
{trimmed}

작성 규칙:
- Markdown 형식으로 작성하세요.
- 제목은 # 으로 시작하세요. (원본 제목을 그대로 써도 되고, 블로그 독자에게 맞게 새로 다듬어도 됩니다)
- 소제목(##)으로 단락을 2~3개 나눠주세요.
- 원본 자료의 데이터와 사례를 자연스러운 이야기 흐름으로 재구성하세요. 자료를 그대로 나열하지 마세요.
- 독자가 "나만 이런 게 아니었구나"를 느낄 수 있도록 공감 언어를 사용하세요.
- 마지막은 따뜻한 마무리 문장으로 끝내주세요.
- 출처 목록은 따로 붙이지 마세요."""


# ── 메타데이터 헤더 생성 ──────────────────────────────────────────────────────
def build_frontmatter(tone: str, keywords: list[str], source_path: Path) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        "---\n"
        f"generated_at: {now}\n"
        f"tone: {tone}\n"
        f"keywords: [{', '.join(keywords)}]\n"
        f"model: {MODEL}\n"
        f"source_file: {source_path.name}\n"
        "---\n\n"
    )


# ── 메인 ──────────────────────────────────────────────────────────────────────
def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.", file=sys.stderr)
        sys.exit(1)

    print(f"📋 설정")
    print(f"   톤:        {TONE}")
    print(f"   키워드:    {', '.join(KEYWORDS) if KEYWORDS else '(없음)'}")
    print(f"   목표 길이: {TARGET_LENGTH}자")
    print(f"   출력 파일: {OUTPUT_FILE}")
    print()

    print("🔍 grok-research-results 폴더에서 소스 자료 탐색 중...")
    try:
        source_dir = find_source_dir()
        source_path = pick_random_source(source_dir)
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

    source_content = source_path.read_text(encoding="utf-8")
    source_title = extract_title(source_content)
    print(f"   ✓ 폴더: {source_dir}")
    print(f"   ✓ 선택된 자료: {source_path.relative_to(source_dir)}")
    print(f"   ✓ 제목: {source_title}")
    print()

    print("✍️  블로그 글 생성 중 (Claude API 호출)...")
    prompt = build_prompt(source_content, source_title, TONE, KEYWORDS, TARGET_LENGTH)
    blog_text = call_anthropic(prompt, api_key)
    print()

    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    full_content = build_frontmatter(TONE, KEYWORDS, source_path) + blog_text
    output_path.write_text(full_content, encoding="utf-8")

    char_count = len(blog_text)
    print(f"✅ 완료!")
    print(f"   파일:   {output_path.resolve()}")
    print(f"   소스:   {source_path}")
    print(f"   글자수: {char_count:,}자")

    # GitHub Actions summary 출력
    github_output = os.environ.get("GITHUB_STEP_SUMMARY", "")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"## 📝 블로그 글 생성 완료\n\n")
            f.write(f"| 항목 | 내용 |\n|------|------|\n")
            f.write(f"| 톤 | {TONE} |\n")
            f.write(f"| 키워드 | {', '.join(KEYWORDS) if KEYWORDS else '(없음)'} |\n")
            f.write(f"| 소스 파일 | `{source_path.name}` |\n")
            f.write(f"| 글자 수 | {char_count:,}자 |\n")
            f.write(f"| 출력 파일 | `{OUTPUT_FILE}` |\n\n")
            f.write("### 생성된 글 미리보기\n\n")
            preview = blog_text[:500] + ("..." if len(blog_text) > 500 else "")
            f.write(preview + "\n")


if __name__ == "__main__":
    main()
