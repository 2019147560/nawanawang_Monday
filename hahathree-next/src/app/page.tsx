'use client';

import { useState, useMemo, useEffect } from 'react';
import Link from 'next/link';
import { Icon } from '@/components/ui/Icon';
import ReviewStrip from '@/components/ReviewStrip';
//import { PROGRAMS, FILTERS, FILTER_OPTIONS, REVIEWS } from '@/lib/data';
// 변경
import { FILTERS, FILTER_OPTIONS, REVIEWS } from '@/lib/data';
import { fetchPrograms } from '@/lib/fetchPrograms';

import type { FilterValues } from '@/types';

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
function ProgramCard({ p }: { p: Program) {
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
  // ✅ 이 줄만 새로 추가
  const [programs, setPrograms] = useState<Program[]>([]);
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
  const [sort, setSort] = useState('추천순');

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
          /* {filtered.map(p => <ProgramCard key={p.id} p={p} />)} */
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

      <SupabaseHello />
    </main>
  );
}
