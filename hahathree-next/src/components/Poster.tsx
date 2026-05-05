import type { Program } from '@/types';

interface PosterProps {
  program: Program;
  width?: number;
  height?: number;
}

export default function Poster({ program, width = 360, height = 200 }: PosterProps) {
  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      xmlns="http://www.w3.org/2000/svg"
      style={{ display: 'block', borderRadius: 12 }}
    >
      <rect width={width} height={height} fill={program.bg} rx="12" />
      {/* Decorative blobs */}
      <circle cx={width - 40} cy={height / 2} r={height * 0.55} fill="rgba(255,255,255,0.18)" />
      <circle cx={width - 80} cy={height * 0.2} r={height * 0.22} fill="rgba(255,255,255,0.22)" />
      {/* Tag */}
      <rect x="16" y="16" width="100" height="22" rx="11" fill="rgba(255,255,255,0.7)" />
      <text x="66" y="31" textAnchor="middle" fontSize="11" fontWeight="600" fill="#111319">
        {program.tag}
      </text>
      {/* Title */}
      <text x="16" y={height - 40} fontSize="18" fontWeight="800" fill="#111319" letterSpacing="-0.4">
        {program.title.split('\n')[0]}
      </text>
      {program.title.includes('\n') && (
        <text x="16" y={height - 18} fontSize="18" fontWeight="800" fill="#111319" letterSpacing="-0.4">
          {program.title.split('\n')[1]}
        </text>
      )}
    </svg>
  );
}
