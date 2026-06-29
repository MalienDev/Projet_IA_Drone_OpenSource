import { useAuth } from '../hooks/useAuth'
import MapView from '../components/MapView'
import VideoPlayer from '../components/VideoPlayer'
import AlertPanel from '../components/AlertPanel'

function DashboardPage() {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white">Drone Surveillance Dashboard</h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-300">{user?.username}</span>
            <button
              onClick={logout}
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Map View */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h2 className="text-xl font-semibold text-white mb-4">Map</h2>
            <MapView />
          </div>

          {/* Video Player */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h2 className="text-xl font-semibold text-white mb-4">Live Video</h2>
            <VideoPlayer />
          </div>

          {/* Alert Panel */}
          <div className="lg:col-span-2 bg-gray-800 rounded-lg p-4">
            <h2 className="text-xl font-semibold text-white mb-4">Alerts</h2>
            <AlertPanel />
          </div>
        </div>
      </main>
    </div>
  )
}

export default DashboardPage
