import type { Metadata } from 'next';
import Crumb from '@/components/Crumb';
import { SUPPORT_POLICIES } from '@/lib/data';

export const metadata: Metadata = { title: '제도 안내 — 나와나망' };

const CATEGORY_COLOR: Record<string, { bg: string; fg: string }> = {
  정책: { bg: '#e7f0ff', fg: 'var(--brand-600)' },
  경제: { bg: '#e6f4ec', fg: '#1f7a4d' },
  심리: { bg: '#f0eaff', fg: '#6b21a8' },
  주거: { bg: '#fff4d6', fg: '#7a5b00' },
};

export default function SupportPage() {
  return (
    <main style={{ maxWidth: 1240, margin: '0 auto', padding: '0 32px 60px' }}>
      <Crumb items={[{ label: '제도 안내' }]} />

      <h1 style={{ margin: '0 0 8px', fontSize: 32, fontWeight: 800, color: 'var(--ink-900)', letterSpacing: '-0.03em' }}>
        제도 안내
      </h1>
      <p style={{ margin: '0 0 36px', fontSize: 14, color: 'var(--ink-500)', lineHeight: 1.6 }}>
        고립·은둔청년을 위한 주요 정책과 지원 제도를 안내합니다.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 20 }}>
        {SUPPORT_POLICIES.map(policy => {
          const color = CATEGORY_COLOR[policy.category] ?? { bg: '#f3f4f7', fg: 'var(--ink-700)' };
          return (
            <div key={policy.id} style={{
              border: '1px solid var(--line)', borderRadius: 14, padding: '24px 28px',
              background: '#fff', boxShadow: 'var(--shadow-card)',
            }}>
              <span style={{
                display: 'inline-block', padding: '4px 10px', borderRadius: 999,
                background: color.bg, color: color.fg,
                fontSize: 11, fontWeight: 700, marginBottom: 14,
              }}>{policy.category}</span>
              <h2 style={{ margin: '0 0 10px', fontSize: 18, fontWeight: 800, color: 'var(--ink-900)', letterSpacing: '-0.02em', lineHeight: 1.4 }}>
                {policy.title}
              </h2>
              <p style={{ margin: 0, fontSize: 13, color: 'var(--ink-600)', lineHeight: 1.7 }}>
                {policy.summary}
              </p>
              <button style={{
                marginTop: 20, height: 38, padding: '0 16px',
                border: '1px solid var(--line)', background: '#fff',
                borderRadius: 8, fontSize: 13, fontWeight: 600, color: 'var(--ink-700)',
              }}>
                자세히 보기
              </button>
            </div>
          );
        })}
      </div>
    </main>
  );
}
