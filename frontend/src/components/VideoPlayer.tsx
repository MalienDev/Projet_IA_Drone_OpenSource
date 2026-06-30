import { useEffect, useRef, useState } from 'react'
import Hls from 'hls.js'

function VideoPlayer() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    // HLS connection to MediaMTX (more reliable than WebRTC for testing)
    // MediaMTX HLS endpoint: http://localhost:8888/stream_name/index.m3u8
    // Use relative URL to work through nginx proxy
    const streamUrl = 'http://localhost:8888/drone-01-los/index.m3u8'
    
    if (videoRef.current) {
      // Check if HLS is supported
      if (Hls.isSupported()) {
        const hls = new Hls({
          enableWorker: true,
          lowLatencyMode: true,
        })
        
        hls.loadSource(streamUrl)
        hls.attachMedia(videoRef.current)
        
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          setConnected(true)
          setError(null)
          videoRef.current?.play().catch(console.error)
        })
        
        hls.on(Hls.Events.ERROR, (_event: any, data: any) => {
          if (data.fatal) {
            setError('Video stream not available. Start the simulator to publish a stream.')
            setConnected(false)
          }
        })
        
        return () => {
          hls.destroy()
        }
      } else if (videoRef.current.canPlayType('application/vnd.apple.mpegurl')) {
        // Native HLS support (Safari)
        videoRef.current.src = streamUrl
        
        videoRef.current.onloadedmetadata = () => {
          setConnected(true)
          setError(null)
          videoRef.current?.play().catch(console.error)
        }
        
        videoRef.current.onerror = () => {
          setError('Video stream not available. Start the simulator to publish a stream.')
          setConnected(false)
        }
      } else {
        setError('HLS is not supported in this browser.')
      }

      // Timeout pour détecter si le stream ne répond pas
      const timeout = setTimeout(() => {
        if (!connected) {
          setError('Video stream not available. Start the simulator to publish a stream.')
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
