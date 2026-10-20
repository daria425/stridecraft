import './chevron-button.css'

/** Round previous/next button with a drawn chevron, same stroke as the stat glyphs. */
export function ChevronButton({
  direction,
  label,
  onClick,
  disabled,
}: {
  direction: 'left' | 'right'
  label: string
  onClick: () => void
  disabled?: boolean
}) {
  return (
    <button
      type="button"
      className="chevron-button"
      aria-label={label}
      onClick={onClick}
      disabled={disabled}
    >
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d={direction === 'left' ? 'M15 5 L8 12 L15 19' : 'M9 5 L16 12 L9 19'} />
      </svg>
    </button>
  )
}
