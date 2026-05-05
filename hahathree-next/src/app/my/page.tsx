import type { Metadata } from 'next';
import Crumb from '@/components/Crumb';
import Mascot from '@/components/ui/Mascot';
import { PROGRAMS } from '@/lib/data';

export const metadata: Metadata = { title: '마이페이지 — 나와나망' };

const SCRAPPED = PROGRAMS.slice(0, 3);

export default function MyPage() {
  return (
    <main style={{ maxWidth: 1240, margin: '0 auto', padding: '0 32px 60px' }}>
      <Crumb items={[{ label: '마이페이지' }]} />

      {/* Profile section */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 24,
        background: 'linear-gradient(135deg, #eaf2ff, #f4f8ff)',
        borderRadius: 16, padding: '28px 36px', marginBottom: 40,
      }}>
        <Mascot size={72} />
        <div>
          <div style={{ fontSize: 13, color: 'var(--ink-500)', marginBottom: 4 }}>안녕하세요 👋</div>
          <div style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink-900)', letterSpacing: '-0.03em' }}>지○○ 님</div>
          <div style={{ fontSize: 12, color: 'var(--ink-500)', marginTop: 4 }}>가입일 2026.03.01 · 스크랩 {SCRAPPED.length}개</div>
        </div>
      </div>

      {/* Scrapped programs */}
      <h2 style={{ margin: '0 0 20px', fontSize: 20, fontWeight: 800, color: 'var(--ink-900)', letterSpacing: '-0.02em' }}>
        내 스크랩
      </h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {SCRAPPED.map(p => (
          <div key={p.id} style={{
            display: 'flex', gap: 18, alignItems: 'center',
            padding: '16px 20px', border: '1px solid var(--line)', borderRadius: 12, background: '#fff',
          }}>
            <div style={{ width: 56, height: 56, borderRadius: 10, background: p.bg, flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--ink-900)', marginBottom: 4 }}>{p.title.replace('\n', ' ')}</div>
              <div style={{ fontSize: 12, color: 'var(--ink-500)' }}>{p.org} · {p.deadline}</div>
            </div>
            <span style={{
              display: 'inline-block', padding: '4px 10px', borderRadius: 999,
              background: p.statusVariant ? '#f0f1f4' : 'var(--brand-500)',
              color: p.statusVariant ? 'var(--ink-500)' : '#fff',
              fontSize: 11, fontWeight: 700,
            }}>{p.dDay}</span>
          </div>
        ))}
      </div>

      {/* Placeholder sections */}
      <h2 style={{ margin: '40px 0 16px', fontSize: 20, fontWeight: 800, color: 'var(--ink-900)', letterSpacing: '-0.02em' }}>
        신청 현황
      </h2>
      <div style={{
        padding: '40px', border: '1px dashed var(--line)', borderRadius: 12,
        textAlign: 'center', color: 'var(--ink-400)', fontSize: 14,
      }}>
        신청한 프로그램이 없습니다
      </div>
    </main>
  );
}
