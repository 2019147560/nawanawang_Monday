import type { SVGProps } from 'react';

type IconProps = SVGProps<SVGSVGElement>;

const base: IconProps = {
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
};

export const Icon = {
  Search: (p: IconProps) => (
    <svg {...base} {...p}>
      <circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" />
    </svg>
  ),
  Bell: (p: IconProps) => (
    <svg {...base} {...p}>
      <path d="M6 8a6 6 0 1 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z" /><path d="M10 19a2 2 0 0 0 4 0" />
    </svg>
  ),
  Refresh: (p: IconProps) => (
    <svg {...base} {...p}>
      <path d="M3 12a9 9 0 0 1 15.5-6.3L21 8" /><path d="M21 3v5h-5" />
      <path d="M21 12a9 9 0 0 1-15.5 6.3L3 16" /><path d="M3 21v-5h5" />
    </svg>
  ),
  Chevron: (p: IconProps) => (
    <svg {...base} {...p}><path d="m6 9 6 6 6-6" /></svg>
  ),
  ChevronL: (p: IconProps) => (
    <svg {...base} {...p}><path d="m15 6-6 6 6 6" /></svg>
  ),
  ChevronR: (p: IconProps) => (
    <svg {...base} {...p}><path d="m9 6 6 6-6 6" /></svg>
  ),
  Grid: (p: IconProps) => (
    <svg {...base} {...p}>
      <rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" />
    </svg>
  ),
  List: (p: IconProps) => (
    <svg {...base} {...p}>
      <path d="M8 6h13" /><path d="M8 12h13" /><path d="M8 18h13" />
      <circle cx="4" cy="6" r="1" /><circle cx="4" cy="12" r="1" /><circle cx="4" cy="18" r="1" />
    </svg>
  ),
  ArrowUpRight: (p: IconProps) => (
    <svg {...base} {...p}>
      <path d="M7 17 17 7" /><path d="M8 7h9v9" />
    </svg>
  ),
};
