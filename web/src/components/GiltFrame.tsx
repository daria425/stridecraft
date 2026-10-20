import type { HTMLAttributes } from 'react'
import './gilt-frame.css'

function Corner({ position }: { position: 'tl' | 'tr' | 'bl' | 'br' }) {
  return (
    <svg
      className={`gilt-frame__corner gilt-frame__corner--${position}`}
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path d="M1 23 V6 L6 1 H23" fill="none" stroke="var(--color-gold)" strokeWidth="1.4" />
      <path d="M7 9 L9 7 L11 9 L9 11 Z" fill="var(--color-gold)" />
    </svg>
  )
}

/** Hairline gilt frame with notched corners on a quiet indigo plate. Extra props (aria-label,
 * tabIndex, role) go to the outer div. */
export function GiltFrame({ children, className = '', ...rest }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`gilt-frame ${className}`} {...rest}>
      <Corner position="tl" />
      <Corner position="tr" />
      <Corner position="bl" />
      <Corner position="br" />
      {children}
    </div>
  )
}
