'use client';

import { useState, useEffect } from 'react';
import type { Review } from '@/types';

interface ReviewStripProps {
  reviews: Review[];
}

export default function ReviewStrip({ reviews }: ReviewStripProps) {
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setIdx((i) => (i + 1) % reviews.length);
    }, 3500);
    return () => clearInterval(timer);
  }, [reviews.length]);

  const r = reviews[idx];

  return (
    <div style={{
      background: 'var(--brand-50)',
      border: '1px solid var(--brand-100)',
      borderRadius: 12, padding: '18px 24px',
      marginTop: 32,
      display: 'flex', alignItems: 'flex-start', gap: 14,
    }}>
      <span style={{ fontSize: 22, flexShrink: 0 }}>💬</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13, color: 'var(--ink-600)', lineHeight: 1.6 }}>
          {r.body}
        </div>
        <div style={{ marginTop: 8, fontSize: 11, color: 'var(--ink-400)', fontWeight: 600 }}>
          {r.name} · {r.program}
        </div>
      </div>
      <div style={{ display: 'flex', gap: 4, flexShrink: 0, alignSelf: 'center' }}>
        {reviews.map((_, i) => (
          <button
            key={i}
            onClick={() => setIdx(i)}
            aria-label={`후기 ${i + 1}`}
            style={{
              width: i === idx ? 16 : 6, height: 6,
              borderRadius: 999, border: 'none',
              background: i === idx ? 'var(--brand-500)' : 'var(--brand-100)',
              transition: 'width .25s ease',
              padding: 0,
            }}
          />
        ))}
      </div>
    </div>
  );
}
