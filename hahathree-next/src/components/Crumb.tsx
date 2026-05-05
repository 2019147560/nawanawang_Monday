import Link from 'next/link';

interface CrumbItem {
  label: string;
  href?: string;
}

interface CrumbProps {
  items: CrumbItem[];
}

export default function Crumb({ items }: CrumbProps) {
  return (
    <nav style={{
      padding: '20px 0 12px',
      fontSize: 12, color: 'var(--ink-500)',
      display: 'flex', alignItems: 'center', gap: 6,
    }} aria-label="breadcrumb">
      {items.map((item, i) => (
        <span key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {i > 0 && <span>›</span>}
          {item.href ? (
            <Link href={item.href} style={{ color: 'var(--ink-500)' }}>{item.label}</Link>
          ) : (
            <span style={{ color: 'var(--ink-900)', fontWeight: 600 }}>{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}
