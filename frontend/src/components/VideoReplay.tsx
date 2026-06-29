import { useState } from 'react'

interface VideoReplayProps {
  clipPath?: string
  onClose: () => void
}

function VideoReplay({ clipPath, onClose }: VideoReplayProps) {
  const [error, setError] = useState<string | null>(null)

  if (!clipPath) {
    return null
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-4 max-w-4xl w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold text-white">Alert Replay</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            &times;
          </button>
        </div>

        <div className="relative bg-black rounded-lg overflow-hidden aspect-video">
          {error ? (
            <div className="flex items-center justify-center h-full text-red-500">
              <p>{error}</p>
            </div>
          ) : (
            <video
              src={clipPath}
              controls
              autoPlay
              className="w-full h-full object-contain"
              onError={() => setError('Failed to load video clip')}
            />
          )}
        </div>

        <div className="mt-4 flex justify-end">
          <button
            onClick={onClose}
            className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

export default VideoReplay
