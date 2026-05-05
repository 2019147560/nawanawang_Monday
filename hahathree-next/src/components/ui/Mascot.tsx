export default function Mascot({ size = 80 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 80 80"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      {/* Simple friendly character */}
      <circle cx="40" cy="36" r="28" fill="#cfe6ff" />
      <circle cx="32" cy="32" r="4" fill="#1655c2" />
      <circle cx="48" cy="32" r="4" fill="#1655c2" />
      <path d="M32 46 Q40 54 48 46" stroke="#1655c2" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      {/* Body */}
      <ellipse cx="40" cy="68" rx="16" ry="8" fill="#e7f0ff" />
    </svg>
  );
}
