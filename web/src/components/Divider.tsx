/** Ornamental rule: a hairline with a diamond and two crescents at the centre. */
export function Divider() {
  return (
    <svg
      viewBox="0 0 320 16"
      width="100%"
      height="16"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
      focusable="false"
    >
      <g stroke="var(--color-gold-dim)" strokeWidth="1" fill="none">
        <path d="M0 8 H130" />
        <path d="M190 8 H320" />
        <path d="M144 3 a6 6 0 0 0 0 10" />
        <path d="M176 3 a6 6 0 0 1 0 10" />
      </g>
      <path d="M160 1 L167 8 L160 15 L153 8 Z" fill="var(--color-gold)" />
    </svg>
  )
}
