import { useEffect, useRef, useState } from 'react'

function VideoPlayer() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    // WebRTC connection to MediaMTX
    // MediaMTX WebRTC endpoint: http://localhost:8189/stream_name
    const streamUrl = 'http://localhost:8189/drone-01-los'
    
    if (videoRef.current) {
      videoRef.current.src = streamUrl
      
      videoRef.current.onloadedmetadata = () => {
        setConnected(true)
        setError(null)
      }
      
      videoRef.current.onerror = () => {
        setError('Video stream not available. Make sure MediaMTX is running and the stream is active.')
        setConnected(false)
      }

      // Timeout pour détecter si le stream ne répond pas
      const timeout = setTimeout(() => {
        if (!connected) {
          setError('Video stream not available. Make sure MediaMTX is running and the stream is active.')
        }
      }, 5000)

      return () => clearTimeout(timeout)
    }
  }, [])

  return (
    <div className="relative bg-black rounded-lg overflow-hidden aspect-video">
      {error ? (
        <div className="flex items-center justify-center h-full text-red-500">
          <p>{error}</p>
        </div>
      ) : (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-contain"
          />
          {!connected && (
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
              <p className="text-white">Connecting to stream...</p>
            </div>
          )}
          {connected && (
            <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded text-sm">
              LIVE
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default VideoPlayer
