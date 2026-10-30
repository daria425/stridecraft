import { Link } from 'react-router'
import { useBreeds, useJourney, useMe, useProfile, useResetProfile } from '../../api/queries'
import { CreatureSlot } from '../../components/CreatureSlot'
import { GiltFrame } from '../../components/GiltFrame'
import { SceneMessage } from '../../components/SceneMessage'
import { StatList } from '../../components/StatList'
import '../../components/scene.css'
import { ResetDialog } from './ResetDialog'
import './profile.css'

export function ProfilePage() {
  const me = useMe().data
  const breeds = useBreeds().data
  const profile = useProfile().data
  const journey = useJourney().data
  const reset = useResetProfile()
  const strider = me?.strider
  if (!me || !strider) return null
  if (!profile || !journey) return <SceneMessage>Loading...</SceneMessage>

  const breed = breeds?.find((b) => b.id === strider.breed)
  const lastEncounter = journey.crossed[0]
  const rows: [string, string][] = [
    ['Runs counted', String(profile.runs)],
    ['Training runs', String(profile.training_runs)],
    ['Voyage distance', `${profile.total_km.toFixed(1)} km`],
    ['Elevation gained', `${Math.round(profile.elevation_gain_m)} m`],
    ['Adopted', new Date(strider.adopted_at).toLocaleDateString()],
  ]

  return (
    <main className="scene profile">
      <header className="profile__bar">
        <Link to="/">Back</Link>
        <span>{me.username ?? me.firstname}</span>
      </header>

      <section className="profile__card" aria-labelledby="profile-strider">
        <GiltFrame className="profile__portrait">
          {breed?.icon_url ? (
            <img src={breed.icon_url} alt={`${strider.name}, a ${breed.name}`} />
          ) : (
            <CreatureSlot
              modelUrl={breed?.model_url ?? null}
              label={strider.name}
              breedId={strider.breed}
            />
          )}
        </GiltFrame>
        <h1 id="profile-strider">{strider.name}</h1>
        <p>{breed?.name ?? strider.breed}</p>
        <GiltFrame className="profile__stats">
          <StatList stats={strider.stats} />
        </GiltFrame>
      </section>

      <section className="profile__details">
        <GiltFrame className="profile__panel">
          <h2>User Stats</h2>
          <table className="profile__table">
            <tbody>
              {rows.map(([label, value]) => (
                <tr key={label}>
                  <th scope="row">{label}</th>
                  <td>{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </GiltFrame>

        <GiltFrame className="profile__panel">
          <h2>Voyage</h2>
          <p>
            {journey.leg_name}, next stop {journey.leg_waypoint} of {journey.leg_length} ·{' '}
            {journey.km_to_go.toFixed(1)} km to go
          </p>
          {lastEncounter ? (
            <>
              <p>
                <strong>Last encounter: {lastEncounter.title}</strong>
              </p>
              <p>{lastEncounter.text}</p>
            </>
          ) : (
            <p>Nothing met on the road yet.</p>
          )}
        </GiltFrame>

        <ResetDialog
          onConfirm={() => reset.mutate()}
          busy={reset.isPending}
          error={reset.error?.message ?? null}
        />
      </section>
    </main>
  )
}
