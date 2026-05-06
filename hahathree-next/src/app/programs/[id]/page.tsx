import Link from 'next/link';
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import Crumb from '@/components/Crumb';
import { Icon } from '@/components/ui/Icon';
import { PROGRAMS, getDetailData } from '@/lib/data';

interface Props {
  params: { id: string };
}

export function generateStaticParams() {
  return PROGRAMS.map(p => ({ id: String(p.id) }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const p = PROGRAMS.find(p => p.id === Number(params.id));
  if (!p) return {};
  return { title: `${p.title.replace('\n', ' ')} — 나와나망` };
}

const tableTh: React.CSSProperties = {
  background: '#fafbfc', fontWeight: 600, fontSize: 12,
  color: 'var(--ink-500)', textAlign: 'left',
  padding: '14px 18px', borderBottom: '1px solid var(--line)',
  borderRight: '1px solid var(--line)', width: '15%',
};
const tableTd: React.CSSProperties = {
  padding: '14px 18px', borderBottom: '1px solid var(--line)',
  borderRight: '1px solid var(--line)', color: 'var(--ink-900)',
  fontSize: 13, fontWeight: 500, width: '35%',
};

function DetailSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 28 }}>
      <h2 style={{
        margin: '0 0 12px', fontSize: 16, fontWeight: 700,
        color: 'var(--ink-900)', display: 'flex', alignItems: 'center', gap: 8,
        paddingBottom: 10, borderBottom: '1px solid var(--line)',
      }}>
        <span style={{ width: 3, height: 16, background: 'var(--brand-500)', borderRadius: 2 }} />
        {title}
      </h2>
      <div>{children}</div>
    </div>
  );
}

function SidebarRow({ label, value, last }: { label: string; value: string; last?: boolean }) {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '10px 0', borderBottom: last ? 'none' : '1px solid var(--line-2)',
    }}>
      <dt style={{ color: 'var(--ink-500)', fontSize: 12, fontWeight: 500 }}>{label}</dt>
      <dd style={{ margin: 0, color: 'var(--ink-900)', fontSize: 13, fontWeight: 700 }}>{value}</dd>
    </div>
  );
}

export default function ProgramDetailPage({ params }: Props) {
  const p = PROGRAMS.find(p => p.id === Number(params.id));
  if (!p) notFound();

  // id에 따라 상세 데이터 가져오기
  const DETAIL_DATA = getDetailData(Number(params.id));

  return (
    <main style={{ maxWidth: 1240, margin: '0 auto', padding: '0 32px 32px' }}>
      <Crumb items={[
        { label: '고립·은둔 예방' },
        { label: '지원사업 검색', href: '/' },
        { label: p.title.replace('\n', ', ') },
      ]} />

      <Link href="/" style={{
        display: 'inline-flex', alignItems: 'center', gap: 4,
        color: 'var(--ink-500)', fontSize: 12, padding: '6px 0',
      }}>
        <Icon.ChevronL width={14} height={14} />
        사업 목록으로
      </Link>

      <div style={{ height: 1, background: 'var(--line-2)', margin: '12px 0 28px' }} />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 32 }}>
        {/* Left */}
        <div>
          <div style={{ display: 'flex', gap: 6, marginBottom: 16 }}>
            {p.chips.map((c, i) => (
              <span key={i} style={{
                background: i === 0 ? '#e6f4ec' : '#f3f4f7',
                color: i === 0 ? '#1f7a4d' : 'var(--ink-700)',
                padding: '5px 10px', borderRadius: 6, fontSize: 12, fontWeight: 600,
              }}>{c}</span>
            ))}
            <span style={{ background: '#f3f4f7', color: 'var(--ink-700)', padding: '5px 10px', borderRadius: 6, fontSize: 12, fontWeight: 600 }}>회복 프로그램</span>
          </div>

          <h1 style={{ margin: 0, fontSize: 32, fontWeight: 800, color: 'var(--ink-900)', letterSpacing: '-0.03em', lineHeight: 1.3 }}>
            {p.title.replace('\n', ', ')}
          </h1>
          <p style={{ marginTop: 12, marginBottom: 28, fontSize: 14, color: 'var(--ink-600)', lineHeight: 1.6 }}>
            {DETAIL_DATA.intro}
          </p>

          <table style={{ width: '100%', borderCollapse: 'collapse', border: '1px solid var(--line)', borderRadius: 8, overflow: 'hidden', fontSize: 13, marginBottom: 32 }}>
            <tbody>
              <tr>
                <th style={tableTh}>주관 기관</th><td style={tableTd}>{DETAIL_DATA.org.name}</td>
                <th style={tableTh}>진행 지역</th><td style={tableTd}>{DETAIL_DATA.org.region}</td>
              </tr>
              <tr>
                <th style={tableTh}>진행 형태</th><td style={tableTd}>온·오프라인</td>
                <th style={tableTh}>참여 기간</th><td style={tableTd}>{p.weeks}</td>
              </tr>
              <tr>
                <th style={tableTh}>신청 마감</th><td style={tableTd}>{p.deadline.replace('마감 ', '')}</td>
                <th style={tableTh}>모집 인원</th><td style={tableTd}>12명</td>
              </tr>
            </tbody>
          </table>

          <DetailSection title="프로그램 소개">
            <p style={{ margin: 0, fontSize: 14, color: 'var(--ink-700)', lineHeight: 1.75 }}>{DETAIL_DATA.description}</p>
          </DetailSection>

          <DetailSection title="신청자격">
            <p style={{ margin: 0, fontSize: 14, color: 'var(--ink-700)', lineHeight: 1.75 }}>{DETAIL_DATA.qualification}</p>
          </DetailSection>

          <DetailSection title="사업 커리큘럼">
            <div style={{ position: 'relative', paddingLeft: 20 }}>
              <div style={{ position: 'absolute', left: 4, top: 8, bottom: 8, width: 1, background: 'var(--line)' }} />
              {DETAIL_DATA.curriculum.map((c, i) => (
                <div key={i} style={{ position: 'relative', marginBottom: i === DETAIL_DATA.curriculum.length - 1 ? 0 : 12 }}>
                  <div style={{ position: 'absolute', left: -20, top: 18, width: 9, height: 9, borderRadius: '50%', background: 'var(--brand-500)', border: '2px solid #fff', boxShadow: '0 0 0 1px var(--line)' }} />
                  <div style={{ border: '1px solid var(--line)', borderRadius: 10, padding: '14px 18px', background: '#fff' }}>
                    <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--brand-500)', marginBottom: 4 }}>{c.weeks}</div>
                    <div style={{ fontSize: 13, color: 'var(--ink-700)', lineHeight: 1.55 }}>{c.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </DetailSection>

          <div style={{ background: '#fafbfc', border: '1px solid var(--line)', borderRadius: 12, padding: '22px 26px', marginTop: 16 }}>
            <h3 style={{ margin: '0 0 16px', fontSize: 15, fontWeight: 700, color: 'var(--ink-900)', paddingBottom: 14, borderBottom: '1px solid var(--line)' }}>기관 및 문의 정보</h3>
            <div style={{ fontSize: 12, color: 'var(--ink-500)', marginBottom: 4 }}>주최·주관 기관</div>
            <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--ink-900)', marginBottom: 16 }}>{DETAIL_DATA.org.name}</div>
            <div style={{ fontSize: 12, color: 'var(--ink-500)', marginBottom: 8 }}>문의 창구</div>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, fontSize: 13, display: 'flex', flexDirection: 'column', gap: 8, color: 'var(--ink-700)' }}>
              <li>📞 {DETAIL_DATA.org.phone}</li>
              <li>💬 카카오톡: {DETAIL_DATA.org.kakao}</li>
              <li>🔗 오픈채팅: {DETAIL_DATA.org.homepage}</li>
              <li>✉ {DETAIL_DATA.org.email}</li>
            </ul>
          </div>
        </div>

        {/* Right: sticky sidebar */}
        <aside>
          <div style={{ position: 'sticky', top: 96, border: '1px solid var(--line)', borderRadius: 12, padding: 22, background: '#fff' }}>
            <dl style={{ margin: 0, fontSize: 13 }}>
              <SidebarRow label="기간" value={p.weeks} />
              <SidebarRow label="진행 형태" value="온·오프라인" />
              <SidebarRow label="지역" value="경기" />
              <SidebarRow label="신청 마감" value={p.deadline.replace('마감 ', '')} last />
            </dl>

            <Link href={`/programs/${p.id}/apply`}>
              <button style={{
                width: '100%', height: 48, marginTop: 16,
                background: 'var(--brand-500)', color: '#fff', border: 'none',
                borderRadius: 8, fontWeight: 700, fontSize: 14,
                display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: 6,
              }}>
                신청페이지로 바로가기 <Icon.ChevronR width={14} height={14} />
              </button>
            </Link>

            <div style={{
              marginTop: 12, padding: '14px 16px',
              background: 'var(--brand-50)', borderRadius: 8,
              fontSize: 12, color: 'var(--ink-700)', lineHeight: 1.55,
              display: 'flex', gap: 8,
            }}>
              <span style={{ flexShrink: 0 }}>💡</span>
              <span>신청 전 반드시 신청 자격을 확인하세요. 문의는 기관으로 직접 연락하시면 됩니다.</span>
            </div>
          </div>
        </aside>
      </div>
    </main>
  );
}
