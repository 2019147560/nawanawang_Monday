# 나와나망 — 고립·은둔청년 통합 정보 플랫폼

Next.js 14 App Router + TypeScript 프로젝트입니다.

## 시작하기

```bash
npm install
npm run dev
```

## 배포 (Vercel)

GitHub에 push 후 Vercel에서 import하면 자동 배포됩니다.
별도 환경변수 설정 불필요.

## 파일 구조

```
src/
├── app/                   # Next.js App Router
│   ├── layout.tsx         # 루트 레이아웃 (Header, Footer 포함)
│   ├── page.tsx           # 홈 — 지원사업 검색
│   ├── support/page.tsx   # 제도 안내
│   ├── my/page.tsx        # 마이페이지
│   └── programs/[id]/
│       ├── page.tsx       # 사업 상세
│       └── apply/page.tsx # 신청 플로우
├── components/
│   ├── Header.tsx
│   ├── Footer.tsx
│   ├── Crumb.tsx
│   ├── ReviewStrip.tsx
│   ├── Poster.tsx
│   └── ui/
│       ├── Icon.tsx
│       └── Mascot.tsx
├── lib/data.ts
├── types/index.ts
└── styles/globals.css
```
