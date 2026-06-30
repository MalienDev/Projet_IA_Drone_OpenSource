import { useState } from 'react'
import { PlayIcon, XIcon } from './Icons'

interface VideoReplayProps {
  clipPath?: string
  alertLabel?: string
  onClose: () => void
}

function VideoReplay({ clipPath, alertLabel = 'Replay alerte', onClose }: VideoReplayProps) {
  const [error, setError] = useState<string | null>(null)

  if (!clipPath) {
    return null
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4">
      <div className="w-full max-w-5xl overflow-hidden rounded-lg border border-neutral-700 bg-neutral-950 shadow-2xl">
        <div className="flex items-center justify-between border-b border-neutral-800 px-4 py-3">
          <div className="flex min-w-0 items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-md border border-emerald-500/35 bg-emerald-500/10 text-emerald-200">
              <PlayIcon className="h-4 w-4" />
            </span>
            <div className="min-w-0">
              <h3 className="truncate text-sm font-semibold text-neutral-100">{alertLabel}</h3>
              <p className="truncate text-xs text-neutral-500">{clipPath}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="icon-button"
            title="Fermer le replay"
            aria-label="Fermer le replay"
          >
            <XIcon className="h-4 w-4" />
          </button>
        </div>

        <div className="relative aspect-video bg-black">
          {error ? (
            <div className="video-empty-state">
              <p className="text-sm font-medium text-red-200">{error}</p>
            </div>
          ) : (
            <video
              src={clipPath}
              controls
              autoPlay
              className="h-full w-full object-contain"
              onError={() => setError('Impossible de charger le clip vidéo.')}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default VideoReplay
