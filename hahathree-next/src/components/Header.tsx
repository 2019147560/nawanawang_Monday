'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Icon } from '@/components/ui/Icon';

const iconBtn: React.CSSProperties = {
  position: 'relative',
  width: 36, height: 36, border: 'none', background: 'transparent',
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  color: 'var(--ink-700)', borderRadius: 8,
};

function NavItem({ href, label }: { href: string; label: string }) {
  const pathname = usePathname();
  const active = pathname === href;
  return (
    <Link href={href} style={{
      position: 'relative', padding: '24px 0',
      fontWeight: active ? 700 : 500,
      fontSize: 15,
      color: active ? 'var(--brand-500)' : 'var(--ink-700)',
    }}>
      {label}
      {active && (
        <span style={{
          position: 'absolute', left: 0, right: 0, bottom: -1,
          height: 3, background: 'var(--brand-500)', borderRadius: 2,
        }} />
      )}
    </Link>
  );
}

export default function Header() {
  return (
    <>
      {/* Utility bar */}
      <div style={{
        borderBottom: '1px solid var(--line-2)',
        background: '#fafbfc',
        fontSize: 12,
        color: 'var(--ink-600)',
      }}>
        <div style={{
          maxWidth: 1240, margin: '0 auto', padding: '0 32px',
          height: 36, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{
              background: '#fff8d4', color: '#7a5b00',
              padding: '3px 8px', borderRadius: 4, fontWeight: 600, fontSize: 11,
            }}>고립·은둔청년 통합 정보 플랫폼</span>
            <span style={{ color: 'var(--ink-500)' }}>운영시간 평일 10:00–18:00</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 18, color: 'var(--ink-500)' }}>
            <Link href="#">도움말</Link>
            <span style={{ color: 'var(--line)' }}>|</span>
            <Link href="#">1:1 문의</Link>
            <span style={{ color: 'var(--line)' }}>|</span>
            <Link href="#">로그인</Link>
            <span style={{ color: 'var(--line)' }}>|</span>
            <Link href="#">회원가입</Link>
          </div>
        </div>
      </div>

      {/* Main nav */}
      <header style={{
        borderBottom: '1px solid var(--line)',
        background: '#fff',
        position: 'sticky', top: 0, zIndex: 10,
      }}>
        <div style={{
          maxWidth: 1240, margin: '0 auto', padding: '0 32px',
          height: 72, display: 'flex', alignItems: 'center', gap: 36,
        }}>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              display: 'flex', alignItems: 'baseline', gap: 0,
              fontWeight: 800, fontSize: 22, letterSpacing: '-0.03em', color: 'var(--brand-700)',
            }}>
              <span>나와</span>
              <span style={{ color: 'var(--brand-500)' }}>나망</span>
            </div>
            <div style={{
              paddingLeft: 12, marginLeft: 4, borderLeft: '1px solid var(--line)',
              fontSize: 11, color: 'var(--ink-500)', lineHeight: 1.35, maxWidth: 130,
            }}>
              고립·은둔청년<br />통합 정보 플랫폼
            </div>
          </Link>

          <nav style={{ display: 'flex', alignItems: 'center', gap: 28, marginLeft: 16 }}>
            <NavItem href="/" label="지원사업 검색" />
            <NavItem href="/support" label="제도 안내" />
            <NavItem href="/my" label="마이페이지" />
          </nav>

          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 18 }}>
            <button style={iconBtn} aria-label="검색">
              <Icon.Search width={20} height={20} />
            </button>
            <button style={iconBtn} aria-label="알림">
              <Icon.Bell width={20} height={20} />
              <span style={{
                position: 'absolute', top: 6, right: 6, width: 7, height: 7,
                borderRadius: '50%', background: '#ef4444', border: '1.5px solid #fff',
              }} />
            </button>
            <button style={{
              width: 36, height: 36, borderRadius: '50%',
              background: '#e7f0ff', color: 'var(--brand-500)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontWeight: 700, fontSize: 14, border: 'none',
            }}>지</button>
          </div>
        </div>
      </header>
    </>
  );
}
