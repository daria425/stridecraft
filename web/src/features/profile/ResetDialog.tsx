import { useRef } from 'react'

/** The dangerous button and the question it asks first. Nothing is sent until "Confirm". */
export function ResetDialog({
  onConfirm,
  busy,
  error,
}: {
  onConfirm: () => void
  busy: boolean
  error: string | null
}) {
  const dialog = useRef<HTMLDialogElement>(null)
  return (
    <>
      <button type="button" className="profile__danger" onClick={() => dialog.current?.showModal()}>
        Reset profile
      </button>
      {error && (
        <p className="profile__error" role="alert">
          {error}
        </p>
      )}
      <dialog ref={dialog} className="profile__dialog" aria-labelledby="reset-question">
        <p id="reset-question">
          This resets all voyage progress. Are you sure you want to continue?
        </p>
        <div className="profile__dialog-actions">
          <button type="button" autoFocus onClick={() => dialog.current?.close()}>
            Cancel
          </button>
          <button
            type="button"
            className="profile__danger"
            disabled={busy}
            onClick={() => {
              dialog.current?.close()
              onConfirm()
            }}
          >
            Confirm
          </button>
        </div>
      </dialog>
    </>
  )
}
