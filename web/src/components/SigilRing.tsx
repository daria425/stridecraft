import './sigil-ring.css'

const HEXAGRAM = ['200,40 338.6,280 61.4,280', '200,360 61.4,120 338.6,120']
const NODES = [...HEXAGRAM[0].split(' '), ...HEXAGRAM[1].split(' ')]
const CARDINALS = [
  [200, 10],
  [390, 200],
  [200, 390],
  [10, 200],
]

/** Engraved summoning circle. Lies flat on the stage floor under the strider. Decoration only. */
export function SigilRing() {
  return (
    <div className="sigil-ring">
      <svg viewBox="0 0 400 400" aria-hidden="true" focusable="false">
        <g className="sigil-ring__inscribe" fill="none" stroke="var(--color-gold)">
          <circle cx="200" cy="200" r="190" strokeWidth="1.5" pathLength="1" />
          <circle cx="200" cy="200" r="181" strokeWidth="0.6" strokeOpacity="0.6" pathLength="1" />
          {HEXAGRAM.map((points) => (
            <polygon
              key={points}
              points={points}
              strokeWidth="0.8"
              strokeOpacity="0.55"
              strokeLinejoin="miter"
              pathLength="1"
            />
          ))}
          <circle cx="200" cy="200" r="124" strokeWidth="2" pathLength="1" />
          <circle cx="200" cy="200" r="130" strokeWidth="0.6" strokeOpacity="0.7" pathLength="1" />
        </g>
        <circle
          className="sigil-ring__ticks"
          cx="200"
          cy="200"
          r="172"
          fill="none"
          stroke="var(--color-gold-dim)"
          strokeWidth="7"
          strokeDasharray="1.2 10.8"
        />
        <g fill="var(--color-gold)">
          {NODES.map((node) => {
            const [x, y] = node.split(',')
            return <circle key={node} cx={x} cy={y} r="3.2" />
          })}
          {CARDINALS.map(([x, y]) => (
            <path
              key={`${x}-${y}`}
              d={`M${x} ${y - 9} L${x + 6} ${y} L${x} ${y + 9} L${x - 6} ${y} Z`}
            />
          ))}
        </g>
      </svg>
    </div>
  )
}
