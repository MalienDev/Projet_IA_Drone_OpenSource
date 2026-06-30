import { useEffect, useMemo, useRef, useState } from 'react'
import Hls from 'hls.js'
import { ActivityIcon, VideoIcon } from './Icons'

interface VideoPlayerProps {
  streamName?: string
  title?: string
  linkType?: string
}

function joinUrl(baseUrl: string, streamName: string) {
  const base = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl
  return `${base}/${streamName}/index.m3u8`
}

function VideoPlayer({
  streamName = 'drone-01-los',
  title = 'Caméra principale',
  linkType = 'LOS',
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [connected, setConnected] = useState(false)

  const streamUrl = useMemo(() => {
    const baseUrl = ((import.meta as any).env?.VITE_HLS_BASE_URL as string | undefined)
      || '/mediamtx'
    return joinUrl(baseUrl, streamName)
  }, [streamName])

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    setConnected(false)
    setError(null)

    let timeoutId = window.setTimeout(() => {
      setError('Flux vidéo indisponible. Vérifier MediaMTX et le simulateur.')
      setConnected(false)
    }, 6000)

    const markReady = () => {
      window.clearTimeout(timeoutId)
      setConnected(true)
      setError(null)
      video.play().catch(() => undefined)
    }

    if (Hls.isSupported()) {
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: true,
        backBufferLength: 30,
      })

      hls.loadSource(streamUrl)
      hls.attachMedia(video)
      hls.on(Hls.Events.MANIFEST_PARSED, markReady)
      hls.on(Hls.Events.ERROR, (_event: string, data: any) => {
        if (data.fatal) {
          window.clearTimeout(timeoutId)
          setError('Flux HLS interrompu ou non publié.')
          setConnected(false)
        }
      })

      return () => {
        window.clearTimeout(timeoutId)
        hls.destroy()
      }
    }

    if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = streamUrl
      video.onloadedmetadata = markReady
      video.onerror = () => {
        window.clearTimeout(timeoutId)
        setError('Flux HLS indisponible dans ce navigateur.')
        setConnected(false)
      }

      return () => {
        window.clearTimeout(timeoutId)
        video.removeAttribute('src')
      }
    }

    window.clearTimeout(timeoutId)
    setError('HLS n’est pas supporté par ce navigateur.')
  }, [streamUrl])

  const handleFullscreen = () => {
    videoRef.current?.requestFullscreen?.()
  }

  return (
    <div className="video-shell">
      <div className="video-toolbar">
        <div className="flex min-w-0 items-center gap-3">
          <span className={`status-dot ${connected ? 'status-dot--ok' : 'status-dot--warn'}`} />
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-neutral-100">{title}</p>
            <p className="truncate text-xs text-neutral-400">{streamName} · {linkType}</p>
          </div>
        </div>
        <button
          type="button"
          onClick={handleFullscreen}
          className="icon-button"
          title="Plein écran"
          aria-label="Plein écran"
        >
          <VideoIcon className="h-4 w-4" />
        </button>
      </div>

      <div className="relative aspect-video overflow-hidden bg-black">
        {error ? (
          <div className="video-empty-state">
            <VideoIcon className="h-10 w-10 text-neutral-500" />
            <p className="mt-3 text-sm font-medium text-neutral-200">{error}</p>
            <p className="mt-1 max-w-md text-center text-xs text-neutral-500">
              Aucun flux ne quitte le poste local dans ce mode ; le lecteur attend la republication HLS de MediaMTX.
            </p>
          </div>
        ) : (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="h-full w-full object-contain"
            />
            {!connected && (
              <div className="video-empty-state bg-black/65">
                <ActivityIcon className="h-9 w-9 animate-pulse text-emerald-300" />
                <p className="mt-3 text-sm text-neutral-200">Connexion au flux...</p>
              </div>
            )}
            <div className="absolute left-3 top-3 flex items-center gap-2 rounded-md border border-neutral-700/80 bg-neutral-950/80 px-2.5 py-1.5 text-xs text-neutral-200">
              <span className={`status-dot ${connected ? 'status-dot--ok' : 'status-dot--warn'}`} />
              {connected ? 'LIVE' : 'SYNC'}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default VideoPlayer
