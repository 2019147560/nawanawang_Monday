import Link from 'next/link';

export default function Footer() {
  return (
    <footer style={{
      borderTop: '1px solid var(--line)', marginTop: 80,
      background: '#fafbfc',
    }}>
      <div style={{
        maxWidth: 1240, margin: '0 auto', padding: '36px 32px 48px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
        gap: 32, flexWrap: 'wrap',
      }}>
        <div style={{ fontSize: 12, color: 'var(--ink-500)', lineHeight: 1.7, maxWidth: 540 }}>
          <div style={{ fontWeight: 800, fontSize: 15, color: 'var(--ink-900)', marginBottom: 10 }}>
            나와나망
          </div>
          <div>고립·은둔청년 통합 정보 플랫폼</div>
          <div>
            <strong style={{ color: 'var(--ink-700)' }}>대표 전화</strong> 02-000-0000{'  '}
            <strong style={{ color: 'var(--ink-700)' }}>운영시간</strong> 평일 10:00–18:00
          </div>
          <div style={{ marginTop: 10, color: 'var(--ink-400)' }}>
            본 화면은 디자인 목업으로 실제 사업과 무관합니다
          </div>
        </div>
        <div style={{
          display: 'flex', gap: 22,
          fontSize: 13, color: 'var(--ink-600)', fontWeight: 500,
        }}>
          <Link href="#">이용약관</Link>
          <Link href="#" style={{ color: 'var(--ink-900)', fontWeight: 700 }}>개인정보처리방침</Link>
          <Link href="#">오시는 길</Link>
          <Link href="#">문의하기</Link>
        </div>
      </div>
    </footer>
  );
}
