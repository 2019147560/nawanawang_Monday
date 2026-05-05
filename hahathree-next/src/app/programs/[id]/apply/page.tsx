'use client';

import { useState } from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import Crumb from '@/components/Crumb';
import { Icon } from '@/components/ui/Icon';
import { PROGRAMS } from '@/lib/data';

const STEPS = ['기본 정보', '신청 동기', '확인 및 제출'];

export default function ApplyPage({ params }: { params: { id: string } }) {
  const p = PROGRAMS.find(p => p.id === Number(params.id));
  if (!p) notFound();

  const [step, setStep] = useState(0);
  const [form, setForm] = useState({ name: '', birth: '', phone: '', reason: '', agree: false });

  const set = (k: string, v: string | boolean) => setForm(f => ({ ...f, [k]: v }));

  const inputStyle: React.CSSProperties = {
    width: '100%', height: 46, border: '1px solid var(--line)',
    borderRadius: 8, padding: '0 14px', fontSize: 14,
    outline: 'none', fontFamily: 'inherit', color: 'var(--ink-900)',
  };
  const labelStyle: React.CSSProperties = {
    display: 'block', fontSize: 13, fontWeight: 600,
    color: 'var(--ink-700)', marginBottom: 6,
  };

  return (
    <main style={{ maxWidth: 640, margin: '0 auto', padding: '0 32px 60px' }}>
      <Crumb items={[
        { label: '지원사업 검색', href: '/' },
        { label: p.title.replace('\n', ', '), href: `/programs/${p.id}` },
        { label: '신청' },
      ]} />

      <h1 style={{ margin: '0 0 8px', fontSize: 24, fontWeight: 800, color: 'var(--ink-900)', letterSpacing: '-0.03em' }}>
        {p.title.replace('\n', ', ')}
      </h1>
      <p style={{ margin: '0 0 32px', fontSize: 13, color: 'var(--ink-500)' }}>{p.org}</p>

      {/* Step indicator */}
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 36, gap: 0 }}>
        {STEPS.map((s, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', flex: i < STEPS.length - 1 ? 1 : 'none' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
              <div style={{
                width: 28, height: 28, borderRadius: '50%',
                background: i <= step ? 'var(--brand-500)' : 'var(--line)',
                color: i <= step ? '#fff' : 'var(--ink-400)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 12, fontWeight: 700,
              }}>{i < step ? '✓' : i + 1}</div>
              <span style={{ fontSize: 11, fontWeight: 600, color: i <= step ? 'var(--brand-500)' : 'var(--ink-400)', whiteSpace: 'nowrap' }}>{s}</span>
            </div>
            {i < STEPS.length - 1 && (
              <div style={{ flex: 1, height: 1, background: i < step ? 'var(--brand-500)' : 'var(--line)', margin: '0 8px', marginBottom: 20 }} />
            )}
          </div>
        ))}
      </div>

      {/* Step 0 */}
      {step === 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div>
            <label style={labelStyle}>이름 <span style={{ color: '#ef4444' }}>*</span></label>
            <input style={inputStyle} value={form.name} onChange={e => set('name', e.target.value)} placeholder="실명을 입력하세요" />
          </div>
          <div>
            <label style={labelStyle}>생년월일 <span style={{ color: '#ef4444' }}>*</span></label>
            <input style={inputStyle} value={form.birth} onChange={e => set('birth', e.target.value)} placeholder="예: 1998-01-01" />
          </div>
          <div>
            <label style={labelStyle}>연락처 <span style={{ color: '#ef4444' }}>*</span></label>
            <input style={inputStyle} value={form.phone} onChange={e => set('phone', e.target.value)} placeholder="010-0000-0000" />
          </div>
        </div>
      )}

      {/* Step 1 */}
      {step === 1 && (
        <div>
          <label style={labelStyle}>신청 동기 <span style={{ color: '#ef4444' }}>*</span></label>
          <textarea
            value={form.reason}
            onChange={e => set('reason', e.target.value)}
            placeholder="이 프로그램에 참여하고 싶은 이유를 자유롭게 작성해주세요. (100자 이상)"
            style={{ ...inputStyle, height: 160, padding: '12px 14px', resize: 'vertical', lineHeight: 1.6 }}
          />
          <p style={{ fontSize: 12, color: 'var(--ink-400)', marginTop: 6 }}>작성 글자 수: {form.reason.length}자</p>
        </div>
      )}

      {/* Step 2 */}
      {step === 2 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div style={{ background: '#fafbfc', border: '1px solid var(--line)', borderRadius: 12, padding: '20px 24px', fontSize: 13, color: 'var(--ink-700)', lineHeight: 1.7 }}>
            <div style={{ fontWeight: 700, marginBottom: 12, color: 'var(--ink-900)' }}>신청 내용 확인</div>
            <div>이름: <strong>{form.name || '—'}</strong></div>
            <div>생년월일: <strong>{form.birth || '—'}</strong></div>
            <div>연락처: <strong>{form.phone || '—'}</strong></div>
            <div style={{ marginTop: 8 }}>신청 동기: <span style={{ color: form.reason ? 'var(--ink-900)' : 'var(--ink-400)' }}>{form.reason ? `${form.reason.slice(0, 60)}…` : '미입력'}</span></div>
          </div>
          <label style={{ display: 'flex', alignItems: 'flex-start', gap: 10, fontSize: 13, color: 'var(--ink-700)', cursor: 'pointer' }}>
            <input type="checkbox" checked={form.agree} onChange={e => set('agree', e.target.checked)} style={{ marginTop: 2, accentColor: 'var(--brand-500)' }} />
            <span>개인정보 수집·이용에 동의합니다. 수집된 정보는 프로그램 운영 목적으로만 활용됩니다.</span>
          </label>
        </div>
      )}

      {/* Navigation */}
      <div style={{ display: 'flex', gap: 10, marginTop: 36 }}>
        {step > 0 && (
          <button onClick={() => setStep(s => s - 1)} style={{
            flex: 1, height: 48, border: '1px solid var(--line)', background: '#fff',
            borderRadius: 8, fontWeight: 600, fontSize: 14, color: 'var(--ink-700)',
          }}>이전</button>
        )}
        {step < STEPS.length - 1 ? (
          <button onClick={() => setStep(s => s + 1)} style={{
            flex: 2, height: 48, background: 'var(--ink-900)', color: '#fff',
            border: 'none', borderRadius: 8, fontWeight: 700, fontSize: 14,
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 6,
          }}>
            다음 <Icon.ChevronR width={14} height={14} />
          </button>
        ) : (
          <button
            disabled={!form.agree}
            onClick={() => alert('신청이 완료되었습니다!')}
            style={{
              flex: 2, height: 48,
              background: form.agree ? 'var(--brand-500)' : 'var(--ink-300)',
              color: '#fff', border: 'none', borderRadius: 8, fontWeight: 700, fontSize: 14,
            }}
          >
            신청 완료
          </button>
        )}
      </div>
    </main>
  );
}
