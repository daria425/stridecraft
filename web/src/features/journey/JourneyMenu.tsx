import { NavLink } from 'react-router'

/** Moves between the strider's home and the voyage map. */
export function JourneyMenu() {
  return (
    <nav className="journey-menu" aria-label="Views">
      <NavLink to="/" end>
        Strider
      </NavLink>
      <NavLink to="/voyage">Voyage</NavLink>
    </nav>
  )
}
