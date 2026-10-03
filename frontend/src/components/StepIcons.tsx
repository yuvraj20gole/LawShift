/** Four plain line icons for the pipeline steps: one stroke weight, no fills. */

type P = { className?: string };

function Svg({ className, children }: P & { children: React.ReactNode }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      width="22"
      height="22"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      {children}
    </svg>
  );
}

/** Find the date. */
export function CalendarIcon(p: P) {
  return (
    <Svg {...p}>
      <rect x="3.5" y="5" width="17" height="15" rx="2" />
      <path d="M3.5 10h17M8 3v4M16 3v4" />
    </Svg>
  );
}

/** Pick the code: one path in, two ways out. */
export function ForkIcon(p: P) {
  return (
    <Svg {...p}>
      <path d="M12 20v-7M12 13c0-3-6-3-6-8M12 13c0-3 6-3 6-8" />
      <path d="M4 7l2-2 2 2M16 7l2-2 2 2" />
    </Svg>
  );
}

/** Find the section. */
export function SearchIcon(p: P) {
  return (
    <Svg {...p}>
      <circle cx="10.5" cy="10.5" r="6" />
      <path d="M15 15l5.5 5.5" />
    </Svg>
  );
}

/** Write it up and check it. */
export function CheckPageIcon(p: P) {
  return (
    <Svg {...p}>
      <path d="M6 3.5h8.5L19 8v12.5H6z" />
      <path d="M14 3.5V8h5M9.5 14.5l2 2 4-4.5" />
    </Svg>
  );
}

export function SwapIcon(p: P) {
  return (
    <Svg {...p}>
      <path d="M4 8h14M14.5 4.5L18 8l-3.5 3.5M20 16H6M9.5 12.5L6 16l3.5 3.5" />
    </Svg>
  );
}
