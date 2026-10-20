import { Divider } from './Divider'
import { GiltFrame } from './GiltFrame'
import './banner.css'

/** The name plate at the top of a scene. `level` is the heading rank, since each page has one h1. */
export function Banner({
  title,
  subtitle,
  level,
  id,
}: {
  title: string
  subtitle: string
  level: 1 | 2
  id?: string
}) {
  const Heading = level === 1 ? 'h1' : 'h2'
  return (
    <GiltFrame className="banner">
      <Heading id={id}>{title}</Heading>
      <Divider />
      <p>{subtitle}</p>
    </GiltFrame>
  )
}
