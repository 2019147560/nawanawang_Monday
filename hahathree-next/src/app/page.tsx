'use client';

import { useState, useMemo, useEffect } from 'react';
import Link from 'next/link';
import { Icon } from '@/components/ui/Icon';
import ReviewStrip from '@/components/ReviewStrip';
//import { PROGRAMS, FILTERS, FILTER_OPTIONS, REVIEWS } from '@/lib/data';
// 변경
import { FILTERS, FILTER_OPTIONS, REVIEWS } from '@/lib/data';
import { fetchPrograms } from '@/lib/fetchPrograms';
import type { Program, FilterValues } from '@/types';

 

/* ── Mock 횡 스크롤 데이터 ── */
const MOCK_DEADLINE_PROGRAMS: Program[] = [
  { id: 101, tag: '회복 프로그램', dDay: 'D-2', title: '천천히, 다시 만나는 일상', org: '경기 청년센터', status: '모집 중', bg: 'var(--card-blue)', chips: ['전체 신청 가능', '경기', '온·오프라인'], weeks: '8주 · 주 1회', deadline: '마감 2026.05.17', statusVariant: 'open' },
  { id: 102, tag: '온라인 모임', dDay: 'D-1', title: '방 안에서 세상으로,\n온라인 살롱', org: '나나센터 수원', status: '모집 중', bg: 'var(--card-yellow)', chips: ['전체 신청 가능', '경기', '온라인'], weeks: '4주 · 주 1회', deadline: '마감 2026.05.16', statusVariant: 'open' },
  { id: 103, tag: '사회 적응', dDay: 'D-3', title: '취업 전, 나를\n알아가는 워크숍', org: '인천 청년센터', status: '모집 중', bg: 'var(--card-mustard)', chips: ['전체 신청 가능', '인천', '오프라인'], weeks: '8주 · 주 2회', deadline: '마감 2026.05.18', statusVariant: 'open' },
  { id: 104, tag: '일경험', dDay: 'D-2', title: '타이틀이 없으면 어떡해', org: '두더지땅굴', status: '모집 중', bg: 'var(--card-mint)', chips: ['전체 신청 가능', '서울', '오프라인'], weeks: '5주', deadline: '마감 2026.05.17', statusVariant: 'open' },
  { id: 105, tag: '회복 프로그램', dDay: 'D-1', title: '식물 돌봄, 나도 돌봄', org: '부산 청년정책연구원', status: '모집 중', bg: 'var(--card-purple)', chips: ['전체 신청 가능', '부산', '오프라인'], weeks: '8주 · 주 1회', deadline: '마감 2026.05.16', statusVariant: 'open' },
  { id: 106, tag: '온라인 모임', dDay: 'D-3', title: '늦은 밤 라디오, 청년 사연함', org: '광주 청년재단', status: '모집 중', bg: 'var(--card-lemon)', chips: ['전체 신청 가능', '광주', '온라인'], weeks: '4주 · 주 1회', deadline: '마감 2026.05.18', statusVariant: 'open' },
];

const MOCK_ONEDAY_PROGRAMS: Program[] = [
  { id: 201, tag: '월데이', dDay: 'D-7', title: '글쓰기로 나를 정리하는 시간', org: '서울 청년허브', status: '모집 중', bg: 'var(--card-orange)', chips: ['전체 신청 가능', '서울', '오프라인'], weeks: '하루 · 4시간', deadline: '마감 2026.05.22', statusVariant: 'open' },
  { id: 202, tag: '월데이', dDay: 'D-9', title: '동네 한 바퀴, 산책 클럽', org: '대전 청년정책본부', status: '모집 중', bg: 'var(--card-pink)', chips: ['전체 신청 가능', '대전', '오프라인'], weeks: '하루 · 3시간', deadline: '마감 2026.05.24', statusVariant: 'open' },
  { id: 203, tag: '월데이', dDay: 'D-5', title: '요리로 잇는 우리, 쿠킹클래스', org: '부산 청년지원센터', status: '모집 중', bg: 'var(--card-mint)', chips: ['전체 신청 가능', '부산', '오프라인'], weeks: '하루 · 5시간', deadline: '마감 2026.05.20', statusVariant: 'open' },
  { id: 204, tag: '월데이', dDay: 'D-11', title: '사진으로 보는 내 일상', org: '강원 청년허브', status: '모집 중', bg: 'var(--card-blue)', chips: ['전체 신청 가능', '강원', '오프라인'], weeks: '하루 · 6시간', deadline: '마감 2026.05.26', statusVariant: 'open' },
  { id: 205, tag: '월데이', dDay: 'D-6', title: '도자기로 빚는 나만의 그릇', org: '경기 청년센터', status: '모집 중', bg: 'var(--card-yellow)', chips: ['전체 신청 가능', '경기', '오프라인'], weeks: '하루 · 4시간', deadline: '마감 2026.05.21', statusVariant: 'open' },
  { id: 206, tag: '월데이', dDay: 'D-14', title: '보드게임으로 만나는 청년들', org: '인천 청년센터', status: '모집 중', bg: 'var(--card-purple)', chips: ['전체 신청 가능', '인천', '오프라인'], weeks: '하루 · 3시간', deadline: '마감 2026.05.29', statusVariant: 'open' },
];

const MOCK_DEADLINE_PROGRAMS_2: Program[] = [
  { id: 301, tag: '심리 지원', dDay: 'D-2', title: '나를 이해하는\n심리 탐구 모임', org: '서울 청년허브', status: '모집 중', bg: 'var(--card-purple)', chips: ['전체 신청 가능', '서울', '온라인'], weeks: '6주 · 주 1회', deadline: '마감 2026.05.17', statusVariant: 'open' },
  { id: 302, tag: '회복 프로그램', dDay: 'D-1', title: '커피 한 잔,\n작은 대화 모임', org: '광주 청년재단', status: '모집 중', bg: 'var(--card-lemon)', chips: ['전체 신청 가능', '광주', '오프라인'], weeks: '4주 · 주 2회', deadline: '마감 2026.05.16', statusVariant: 'open' },
  { id: 303, tag: '자립 지원', dDay: 'D-3', title: '주거 독립 첫걸음\n세미나', org: '인천 청년센터', status: '모집 중', bg: 'var(--card-mint)', chips: ['전체 신청 가능', '인천', '오프라인'], weeks: '2주 · 주 1회', deadline: '마감 2026.05.18', statusVariant: 'open' },
  { id: 304, tag: '사회 적응', dDay: 'D-2', title: '게임으로 만나는\n또래 살롱', org: '강원 청년허브', status: '모집 중', bg: 'var(--card-blue)', chips: ['전체 신청 가능', '강원', '온라인'], weeks: '8주 · 주 1회', deadline: '마감 2026.05.17', statusVariant: 'open' },
  { id: 305, tag: '일경험', dDay: 'D-3', title: '나의 첫 직무 경험\n인턴십', org: '경기 청년센터', status: '모집 중', bg: 'var(--card-mustard)', chips: ['전체 신청 가능', '경기', '오프라인'], weeks: '4주', deadline: '마감 2026.05.18', statusVariant: 'open' },
  { id: 306, tag: '온라인 모임', dDay: 'D-1', title: '취미로 잇는\n온라인 모임방', org: '부산 청년정책연구원', status: '모집 중', bg: 'var(--card-pink)', chips: ['전체 신청 가능', '부산', '온라인'], weeks: '6주 · 주 1회', deadline: '마감 2026.05.16', statusVariant: 'open' },
];

const MOCK_ONEDAY_PROGRAMS_2: Program[] = [
  { id: 401, tag: '월데이', dDay: 'D-8', title: '힐링 숲 캠핑 원데이', org: '강원 청년허브', status: '모집 중', bg: 'var(--card-mint)', chips: ['전체 신청 가능', '강원', '오프라인'], weeks: '하루 · 전일', deadline: '마감 2026.05.23', statusVariant: 'open' },
  { id: 402, tag: '월데이', dDay: 'D-10', title: '나만의 향수 만들기\n원데이 클래스', org: '서울 청년허브', status: '모집 중', bg: 'var(--card-orange)', chips: ['전체 신청 가능', '서울', '오프라인'], weeks: '하루 · 3시간', deadline: '마감 2026.05.25', statusVariant: 'open' },
  { id: 403, tag: '월데이', dDay: 'D-4', title: '드로잉으로 표현하는\n내 감정', org: '인천 청년센터', status: '모집 중', bg: 'var(--card-yellow)', chips: ['전체 신청 가능', '인천', '오프라인'], weeks: '하루 · 4시간', deadline: '마감 2026.05.19', statusVariant: 'open' },
  { id: 404, tag: '월데이', dDay: 'D-12', title: '플리마켓 셀러 체험\n원데이', org: '대전 청년정책본부', status: '모집 중', bg: 'var(--card-blue)', chips: ['전체 신청 가능', '대전', '오프라인'], weeks: '하루 · 5시간', deadline: '마감 2026.05.27', statusVariant: 'open' },
  { id: 405, tag: '월데이', dDay: 'D-6', title: '책으로 잇는\n독서 모임 데이', org: '경기 청년센터', status: '모집 중', bg: 'var(--card-purple)', chips: ['전체 신청 가능', '경기', '오프라인'], weeks: '하루 · 3시간', deadline: '마감 2026.05.21', statusVariant: 'open' },
  { id: 406, tag: '월데이', dDay: 'D-13', title: '수제 캔들 만들기\n원데이 클래스', org: '광주 청년재단', status: '모집 중', bg: 'var(--card-lemon)', chips: ['전체 신청 가능', '광주', '오프라인'], weeks: '하루 · 4시간', deadline: '마감 2026.05.28', statusVariant: 'open' },
];

/* ── Hero ── */
function Hero() {
  return (
    <section style={{
      position: 'relative', overflow: 'hidden',
      borderRadius: 18, marginTop: 28,
      background: 'linear-gradient(135deg, #eaf2ff 0%, #f4f8ff 60%, #f0eaff 100%)',
      padding: '40px 44px',
      minHeight: 200,
    }}>
      <div aria-hidden style={{ position: 'absolute', right: -40, top: -60, width: 280, height: 280, borderRadius: '50%', background: 'rgba(125,155,255,0.18)' }} />
      <div aria-hidden style={{ position: 'absolute', right: 120, top: 30, width: 110, height: 110, borderRadius: '50%', background: 'rgba(125,155,255,0.22)' }} />
      <div aria-hidden style={{ position: 'absolute', right: 180, top: 90, width: 14, height: 14, borderRadius: '50%', background: 'var(--brand-500)' }} />
      <div aria-hidden style={{ position: 'absolute', right: 60, bottom: -50, width: 160, height: 160, borderRadius: '50%', background: 'rgba(174,145,255,0.20)' }} />

      <div style={{ position: 'relative', maxWidth: 640 }}>
        <span style={{
          display: 'inline-block',
          background: 'var(--brand-500)', color: '#fff',
          padding: '5px 12px', borderRadius: 999,
          fontWeight: 600, fontSize: 12, marginBottom: 14,
        }}>특별 안내</span>
        <h2 style={{ margin: 0, fontSize: 30, fontWeight: 800, color: 'var(--brand-700)', letterSpacing: '-0.025em' }}>
          2026년 청년 자립 지원 프로그램 모집
        </h2>
        <p style={{ marginTop: 12, marginBottom: 22, fontSize: 14, color: 'var(--ink-600)', lineHeight: 1.6, letterSpacing: '-0.01em' }}>
          고립·은둔청년을 위한 맞춤형 지원 프로그램이 시작됩니다. 주거, 일자리, 심리상담까지 종합 지원!
        </p>
        <button style={{
          background: 'var(--ink-900)', color: '#fff', border: 'none',
          padding: '12px 22px', borderRadius: 999, fontWeight: 600, fontSize: 14,
          display: 'inline-flex', alignItems: 'center', gap: 6,
        }}>
          자세히 보기
          <Icon.ArrowUpRight width={14} height={14} />
        </button>
      </div>
    </section>
  );
}

/* ── FilterChip ── */
function FilterChip({ f, value, onChange }: {
  f: { id: string; label: string };
  value: string[];
  onChange: (v: string[]) => void;
}) {
  const [open, setOpen] = useState(false);
  const options = FILTER_OPTIONS[f.id];
  const selected = Array.isArray(value) ? value : [];
  const allSelected = selected.length === options.length;
  const noneSelected = selected.length === 0;
  const active = !noneSelected && !allSelected;

  let display = f.label;
  if (active) display = selected.length === 1 ? selected[0] : `${f.label} ${selected.length}`;

  const toggleAll = () => { if (allSelected) onChange([]); else onChange(options.slice()); };
  const toggleOne = (opt: string) => {
    if (selected.includes(opt)) onChange(selected.filter(x => x !== opt));
    else onChange([...selected, opt]);
  };

  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={() => setOpen(o => !o)}
        onBlur={(e) => { if (!e.currentTarget.parentElement?.contains(e.relatedTarget as Node)) setTimeout(() => setOpen(false), 150); }}
        style={{
          height: 36, padding: '0 14px', borderRadius: 999,
          border: `1px solid ${active ? 'var(--brand-500)' : 'var(--line)'}`,
          background: active ? 'var(--brand-50)' : '#fff',
          color: active ? 'var(--brand-500)' : 'var(--ink-700)',
          fontSize: 13, fontWeight: active ? 600 : 500,
          display: 'inline-flex', alignItems: 'center', gap: 6,
        }}
      >
        {display}
        <Icon.Chevron width={14} height={14} />
      </button>
      {open && (
        <div tabIndex={-1} style={{
          position: 'absolute', top: 'calc(100% + 6px)', left: 0, zIndex: 5,
          minWidth: 200, background: '#fff',
          border: '1px solid var(--line)', borderRadius: 12,
          boxShadow: '0 12px 32px rgba(15,23,42,0.10)', padding: 6,
          maxHeight: 360, overflowY: 'auto',
        }}>
          <CheckRow label="전체선택" checked={allSelected} indeterminate={!allSelected && !noneSelected} onToggle={toggleAll} />
          <div style={{ height: 1, background: 'var(--line-2)', margin: '4px 6px' }} />
          {options.map(opt => (
            <CheckRow key={opt} label={opt} checked={selected.includes(opt)} onToggle={() => toggleOne(opt)} />
          ))}
        </div>
      )}
    </div>
  );
}

function CheckRow({ label, checked, indeterminate, onToggle }: {
  label: string; checked: boolean; indeterminate?: boolean; onToggle: () => void;
}) {
  return (
    <button
      onMouseDown={(e) => { e.preventDefault(); onToggle(); }}
      style={{
        display: 'flex', alignItems: 'center', gap: 10,
        width: '100%', textAlign: 'left',
        padding: '9px 10px', borderRadius: 8, border: 'none',
        background: 'transparent', color: 'var(--ink-700)',
        fontWeight: 500, fontSize: 13,
      }}
      onMouseEnter={e => (e.currentTarget.style.background = 'var(--bg-soft)')}
      onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
    >
      <span style={{
        width: 16, height: 16, borderRadius: 4,
        border: `1.5px solid ${checked || indeterminate ? 'var(--brand-500)' : 'var(--ink-300)'}`,
        background: checked || indeterminate ? 'var(--brand-500)' : '#fff',
        display: 'inline-flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
      }}>
        {checked && <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5" /></svg>}
        {indeterminate && !checked && <span style={{ width: 8, height: 2, background: '#fff', borderRadius: 1 }} />}
      </span>
      <span>{label}</span>
    </button>
  );
}

/* ── FilterBar ── */
function FilterBar({ values, onChange, onReset, query, setQuery, onSearch }: {
  values: FilterValues;
  onChange: (k: string, v: string[]) => void;
  onReset: () => void;
  query: string;
  setQuery: (v: string) => void;
  onSearch: () => void;
}) {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
        <button onClick={onReset} style={{
          width: 36, height: 36, border: '1px solid var(--line)', background: '#fff',
          borderRadius: '50%', display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
          color: 'var(--ink-600)',
        }} aria-label="필터 초기화">
          <Icon.Refresh width={16} height={16} />
        </button>
        {FILTERS.map(f => (
          <FilterChip key={f.id} f={f} value={values[f.id as keyof FilterValues]} onChange={v => onChange(f.id, v)} />
        ))}
      </div>
      <form onSubmit={e => { e.preventDefault(); onSearch(); }} style={{ display: 'flex', gap: 10, marginTop: 14 }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="사업명을 입력하세요"
            style={{
              width: '100%', height: 48, border: '1px solid var(--line)',
              borderRadius: 10, padding: '0 18px',
              fontSize: 14, outline: 'none', color: 'var(--ink-900)',
              fontFamily: 'inherit', background: '#fff',
            }}
            onFocus={e => (e.currentTarget.style.borderColor = 'var(--brand-500)')}
            onBlur={e => (e.currentTarget.style.borderColor = 'var(--line)')}
          />
        </div>
        <button type="submit" style={{
          height: 48, padding: '0 28px',
          background: 'var(--ink-900)', color: '#fff', border: 'none', borderRadius: 10,
          fontWeight: 600, fontSize: 14, display: 'inline-flex', alignItems: 'center', gap: 8,
        }}>
          <Icon.Search width={16} height={16} />검색
        </button>
      </form>
    </div>
  );
}

/* ── ProgramCard ── */
function ProgramCard({ p }: { p: Program}) {
  const [hover, setHover] = useState(false);

  const dDayBg = p.dDay === '마감' || p.dDay === '곧오픈' ? '#fff' : 'var(--brand-500)';
  const dDayFg = p.dDay === '마감' ? 'var(--ink-700)' : p.dDay === '곧오픈' ? 'var(--ink-900)' : '#fff';
  const dDayBorder = (p.dDay === '마감' || p.dDay === '곧오픈') ? '1px solid rgba(0,0,0,0.12)' : 'none';

  const statusBg = p.statusVariant ? '#fff' : 'var(--ink-900)';
  const statusFg = p.statusVariant === 'closed' ? 'var(--ink-500)' : p.statusVariant ? 'var(--ink-900)' : '#fff';
  const statusBorder = p.statusVariant ? '1px solid rgba(0,0,0,0.08)' : 'none';

  return (
    <Link href={`/programs/${p.id}`} style={{ textDecoration: 'none' }}>
      <article
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
        style={{
          border: '1px solid var(--line)', borderRadius: 14, overflow: 'hidden',
          background: '#fff', boxShadow: hover ? '0 8px 24px rgba(15,23,42,0.08)' : 'var(--shadow-card)',
          transition: 'transform .18s ease, box-shadow .18s ease',
          transform: hover ? 'translateY(-2px)' : 'translateY(0)',
          cursor: 'pointer', display: 'flex', flexDirection: 'column',
        }}
      >
        <div style={{
          position: 'relative', background: p.bg, height: 200, padding: 18,
          display: 'flex', flexDirection: 'column', justifyContent: 'space-between', overflow: 'hidden',
        }}>
          <div aria-hidden style={{ position: 'absolute', left: -40, bottom: -40, width: 130, height: 130, borderRadius: '50%', background: 'rgba(255,255,255,0.45)' }} />
          <div aria-hidden style={{ position: 'absolute', right: -30, top: 30, width: 70, height: 70, borderRadius: '50%', background: 'rgba(255,255,255,0.30)' }} />

          <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ background: 'rgba(255,255,255,0.7)', color: 'var(--ink-900)', padding: '4px 10px', borderRadius: 999, fontSize: 11, fontWeight: 600 }}>{p.tag}</span>
            <span style={{ background: dDayBg, color: dDayFg, border: dDayBorder, padding: '4px 10px', borderRadius: 999, fontSize: 11, fontWeight: 700 }}>{p.dDay}</span>
          </div>

          <div style={{ position: 'relative' }}>
            <h3 style={{ margin: 0, fontSize: 19, fontWeight: 800, lineHeight: 1.35, color: 'var(--ink-900)', letterSpacing: '-0.02em', whiteSpace: 'pre-line' }}>{p.title}</h3>
          </div>

          <div style={{ position: 'relative', display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
            <span style={{ fontSize: 12, color: 'var(--ink-700)', fontWeight: 500 }}>{p.org}</span>
            <span style={{ background: statusBg, color: statusFg, border: statusBorder, padding: '5px 12px', borderRadius: 999, fontSize: 11, fontWeight: 700 }}>{p.status}</span>
          </div>
        </div>

        <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {p.chips.map((c, i) => {
              const isFirst = i === 0;
              const isClosed = c === '마감';
              const isSoon = c === '모집 예정';
              const bg = isClosed ? '#f0f1f4' : isSoon ? '#fff4d6' : isFirst ? '#e6f4ec' : '#f3f4f7';
              const fg = isClosed ? 'var(--ink-500)' : isSoon ? '#7a5b00' : isFirst ? '#1f7a4d' : 'var(--ink-700)';
              return <span key={i} style={{ background: bg, color: fg, padding: '4px 9px', borderRadius: 6, fontSize: 11, fontWeight: 600 }}>{c}</span>;
            })}
          </div>
          <div style={{ fontSize: 12, color: 'var(--ink-500)' }}>{p.org}</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: 10, borderTop: '1px dashed var(--line)', fontSize: 12 }}>
            <span style={{ color: 'var(--ink-700)', fontWeight: 600 }}>{p.weeks}</span>
            <span style={{ color: 'var(--ink-500)' }}>{p.deadline}</span>
          </div>
        </div>
      </article>
    </Link>
  );
}

function ListView({ programs }: { programs: Program[] }) {
  return (
    <div style={{ marginTop: 18, display: 'flex', flexDirection: 'column', gap: 8 }}>
      {programs.map(p => (
        <Link key={p.id} href={`/programs/${p.id}`} style={{ textDecoration: 'none' }}>
          <div style={{
            display: 'flex', gap: 18, alignItems: 'center',
            padding: 14, border: '1px solid var(--line)', borderRadius: 12, background: '#fff', cursor: 'pointer',
          }}>
            <div style={{ width: 96, height: 96, borderRadius: 10, background: p.bg, flexShrink: 0 }} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', gap: 6, marginBottom: 6 }}>
                {p.chips.map((c, i) => (
                  <span key={i} style={{ background: '#f3f4f7', color: 'var(--ink-700)', padding: '3px 8px', borderRadius: 5, fontSize: 11, fontWeight: 600 }}>{c}</span>
                ))}
              </div>
              <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 4, color: 'var(--ink-900)' }}>{p.title.replace('\n', ' ')}</div>
              <div style={{ fontSize: 12, color: 'var(--ink-500)' }}>{p.org} · {p.weeks}</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ display: 'inline-block', padding: '4px 10px', borderRadius: 999, background: 'var(--brand-500)', color: '#fff', fontSize: 11, fontWeight: 700, marginBottom: 6 }}>{p.dDay}</div>
              <div style={{ fontSize: 12, color: 'var(--ink-500)' }}>{p.deadline}</div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}

/* ── HorizontalCardSection ── */
function HorizontalCardSection({ title, programs, badge }: {
  title: string;
  programs: Program[];
  badge?: { text: string; color: string; bg: string };
}) {
  return (
    <div style={{ marginTop: 40 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16, paddingLeft: 2 }}>
        {badge && (
          <span style={{
            background: badge.bg, color: badge.color,
            fontSize: 11, fontWeight: 700, padding: '3px 10px',
            borderRadius: 999,
          }}>{badge.text}</span>
        )}
        <h2 style={{
          margin: 0, fontSize: 18, fontWeight: 800,
          color: 'var(--ink-900)', letterSpacing: '-0.025em',
        }}>{title}</h2>
      </div>
      <div style={{
        display: 'flex', gap: 14, overflowX: 'auto', paddingBottom: 12,
        scrollbarWidth: 'none',
        // webkit scrollbar hidden via inline style trick
        msOverflowStyle: 'none',
      }}>
        {programs.map(p => (
          <div key={p.id} style={{ flexShrink: 0, width: 220 }}>
            <ProgramCard p={p} />
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── SectionDivider ── */
function SectionDivider() {
  return (
    <div style={{
      margin: '48px 0 0',
      borderTop: '1px solid var(--line)',
    }} />
  );
}

function Pagination({ page, setPage, total }: { page: number; setPage: (n: number) => void; total: number }) {
  const pageBtn = (active: boolean): React.CSSProperties => ({
    width: 36, height: 36, borderRadius: 8, border: 'none',
    background: active ? 'var(--ink-900)' : 'transparent',
    color: active ? '#fff' : 'var(--ink-600)',
    fontSize: 13, fontWeight: 600,
    display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
  });
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 6, marginTop: 36 }}>
      <button onClick={() => setPage(Math.max(1, page - 1))} style={pageBtn(false)} aria-label="이전"><Icon.ChevronL width={16} height={16} /></button>
      {Array.from({ length: total }, (_, i) => i + 1).map(n => (
        <button key={n} onClick={() => setPage(n)} style={pageBtn(n === page)}>{n}</button>
      ))}
      <button onClick={() => setPage(Math.min(total, page + 1))} style={pageBtn(false)} aria-label="다음"><Icon.ChevronR width={16} height={16} /></button>
    </div>
  );
}

/* ── SupabaseHello ── */
function SupabaseHello() {
  const [helloText, setHelloText] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
 const [programs, setPrograms] = useState<Program[]>([]);
  // ✅ 이 줄만 새로 추가
  //const [programs, setPrograms] = useState<Program[]>([]);
  // ✅ useEffect 전체를 아래로 교체
useEffect(() => {
  const load = async () => {
    try {
      const data = await fetchPrograms();
      setPrograms(data);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error('❌ fetchPrograms Error:', msg);
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  };
  load();
}, []);

if (loading) {
  return (
    <div style={{ padding: '20px', color: 'var(--ink-500)', textAlign: 'center' }}>
      로딩 중...
    </div>
  );
}

// 에러가 있으면 무조건 표시
if (errorMessage) {
  return (
    <div style={{
      padding: '20px 0',
      borderTop: '1px solid var(--line)',
      marginTop: 32,
      color: '#ef4444',
      fontWeight: 600,
      fontSize: 14,
    }}>
      ❌ Error: {errorMessage}
    </div>
  );
}

// 데이터 없을 때도 에러 우선 유지 구조
if (!helloText) {
  return (
    <div style={{
      padding: '20px 0',
      borderTop: '1px solid var(--line)',
      marginTop: 32,
      color: '#ef4444',
      fontWeight: 600,
      fontSize: 14,
    }}>
      ❌ Error: No data received from API
    </div>
  );
}

return (
  <div style={{ padding: '20px 0', borderTop: '1px solid var(--line)', marginTop: 32 }}>
    <span style={{ color: '#0066cc', fontWeight: 600, fontSize: 16 }}>
      {helloText}
    </span>
  </div>
);
}

/* ── Page ── */
export default function HomePage() {
  //const [filters, setFilters] = useState<FilterValues>({ region: [], level: [], mode: [], period: [], status: [], people: [] });
  // 변경: 위에 programs 상태 추가
const [programs, setPrograms] = useState<Program[]>([]);
  const [query, setQuery] = useState('');
  const [appliedQuery, setAppliedQuery] = useState('');
  const [view, setView] = useState<'grid' | 'list'>('grid');
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<FilterValues>({ region: [], level: [], mode: [], period: [], status: [], people: [] });
  const [sort, setSort] = useState('추천순');
    // ✅ 이거 추가
  useEffect(() => {
    fetchPrograms().then(setPrograms).catch(console.error);
  }, []);

  const handleFilter = (k: string, v: string[]) => { setFilters(f => ({ ...f, [k]: v })); setPage(1); };
  const reset = () => { setFilters({ region: [], level: [], mode: [], period: [], status: [], people: [] }); setQuery(''); setAppliedQuery(''); setPage(1); };
  const search = () => { setAppliedQuery(query); setPage(1); };

  const filtered = useMemo(() => programs.filter(p => {
    if (appliedQuery && !p.title.includes(appliedQuery) && !p.org.includes(appliedQuery)) return false;
    const anySelected = (arr: string[]) => arr.length > 0;
    const someChip = (arr: string[], matchFn: (c: string, v: string) => boolean) => arr.some(v => p.chips.some(c => matchFn(c, v)));
    if (anySelected(filters.region) && !someChip(filters.region, (c, v) => c.includes(v))) return false;
    if (anySelected(filters.mode) && !someChip(filters.mode, (c, v) => c === v || c.includes(v))) return false;
    if (anySelected(filters.status)) {
      const map: Record<string, string> = { '모집 중': '현재 신청 가능', '모집 예정': '모집 예정', '마감': '마감' };
      if (!filters.status.includes(map[p.status] || p.status)) return false;
    }
    return true;
  }), [programs, filters, appliedQuery]);

  const viewBtn = (active: boolean): React.CSSProperties => ({
    height: 34, padding: '0 12px',
    background: active ? 'var(--ink-900)' : '#fff',
    color: active ? '#fff' : 'var(--ink-600)',
    border: 'none', display: 'inline-flex', alignItems: 'center', gap: 6,
    fontSize: 12, fontWeight: 600,
  });

  return (
    <main style={{ maxWidth: 1240, margin: '0 auto', padding: '0 32px 32px' }}>
      <Hero />
      <ReviewStrip reviews={REVIEWS} />

      <div style={{ marginTop: 40 }}>
        <span style={{ display: 'inline-block', fontSize: 12, color: 'var(--ink-500)', letterSpacing: '-0.01em', marginBottom: 8, fontWeight: 500 }}>고립·은둔 예방</span>
        <h1 style={{ margin: 0, fontSize: 32, fontWeight: 800, color: 'var(--ink-900)', letterSpacing: '-0.03em' }}>지원사업 검색</h1>
      </div>

      <div style={{ marginTop: 22 }}>
        <FilterBar values={filters} onChange={handleFilter} onReset={reset} query={query} setQuery={setQuery} onSearch={search} />
      </div>

      <div style={{ marginTop: 28, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
        <div style={{ fontSize: 13, color: 'var(--ink-600)' }}>
          전체 <strong style={{ color: 'var(--ink-900)', fontWeight: 700 }}>{filtered.length}</strong>건
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <select value={sort} onChange={e => setSort(e.target.value)} style={{ height: 34, border: '1px solid var(--line)', borderRadius: 8, padding: '0 10px 0 12px', fontSize: 12, color: 'var(--ink-700)', background: '#fff', fontFamily: 'inherit' }}>
            <option>추천순</option><option>마감 임박순</option><option>최신순</option>
          </select>
          <div style={{ display: 'inline-flex', border: '1px solid var(--line)', borderRadius: 8, overflow: 'hidden' }}>
            <button onClick={() => setView('grid')} style={viewBtn(view === 'grid')}><Icon.Grid width={14} height={14} /><span>카드</span></button>
            <button onClick={() => setView('list')} style={viewBtn(view === 'list')}><Icon.List width={14} height={14} /><span>리스트</span></button>
          </div>
        </div>
      </div>

      {view === 'grid' ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 18, marginTop: 18 }}>
           {filtered.map(p => <ProgramCard key={p.id} p={p} />)} 
        </div>
      ) : (
        <ListView programs={filtered} />
      )}

      {filtered.length === 0 && (
        <div style={{ padding: '80px 0', textAlign: 'center', color: 'var(--ink-500)', fontSize: 14 }}>
          조건에 맞는 사업이 없어요. 필터를 조정해보실래요?
        </div>
      )}

      {filtered.length > 0 && <Pagination page={page} setPage={setPage} total={3} />}

      {/* ── 횡 스크롤 섹션 블록 1 ── */}
      <SectionDivider />
      <HorizontalCardSection
        title="이번주 신청 마감"
        badge={{ text: '⏰ 마감 임박', color: '#c2410c', bg: '#fff7ed' }}
        programs={MOCK_DEADLINE_PROGRAMS}
      />
      <HorizontalCardSection
        title="1회만 참여 가능해요"
        badge={{ text: '✦ 원데이', color: '#6d28d9', bg: '#f5f3ff' }}
        programs={MOCK_ONEDAY_PROGRAMS}
      />

      {/* ── 횡 스크롤 섹션 블록 2 ── */}
      <SectionDivider />
      <HorizontalCardSection
        title="이번주 신청 마감"
        badge={{ text: '⏰ 마감 임박', color: '#c2410c', bg: '#fff7ed' }}
        programs={MOCK_DEADLINE_PROGRAMS_2}
      />
      <HorizontalCardSection
        title="1회만 참여 가능해요"
        badge={{ text: '✦ 원데이', color: '#6d28d9', bg: '#f5f3ff' }}
        programs={MOCK_ONEDAY_PROGRAMS_2}
      />

      <SupabaseHello />
    </main>
  );
}
