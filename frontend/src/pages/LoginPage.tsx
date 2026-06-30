import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { ActivityIcon, LockIcon, ShieldIcon, UserIcon } from '../components/Icons'

function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(username, password)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentification refusée.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100">
      <main className="mx-auto grid min-h-screen max-w-6xl items-center gap-8 px-4 py-8 lg:grid-cols-[1fr_420px]">
        <section className="hidden lg:block">
          <div className="ops-panel overflow-hidden">
            <div className="border-b border-neutral-800 px-5 py-4">
              <div className="flex items-center gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-md border border-emerald-500/35 bg-emerald-500/10 text-emerald-200">
                  <ShieldIcon className="h-5 w-5" />
                </span>
                <div>
                  <h1 className="text-base font-semibold text-neutral-50">GCS Surveillance IA</h1>
                  <p className="text-xs text-neutral-500">Poste local de supervision drone</p>
                </div>
              </div>
            </div>

            <div className="grid gap-4 p-5">
              <div className="mission-radar">
                <div className="mission-radar__grid" />
                <div className="mission-radar__track mission-radar__track--one" />
                <div className="mission-radar__track mission-radar__track--two" />
                <div className="mission-radar__center" />
              </div>

              <div className="grid grid-cols-3 gap-3">
                {[
                  ['LOS', 'RTSP/RTMP'],
                  ['BLOS', 'SRT/RTMP'],
                  ['IA', 'Local'],
                ].map(([label, value]) => (
                  <div key={label} className="rounded-md border border-neutral-800 bg-neutral-900/70 p-3">
                    <p className="text-xs text-neutral-500">{label}</p>
                    <p className="mt-1 truncate text-sm font-semibold text-neutral-100">{value}</p>
                  </div>
                ))}
              </div>

              <div className="rounded-md border border-amber-500/25 bg-amber-500/10 p-3 text-xs leading-5 text-amber-100">
                Les alertes critiques restent à confirmer par l’opérateur. Le système assiste la décision, il ne l’exécute pas.
              </div>
            </div>
          </div>
        </section>

        <section className="ops-panel w-full overflow-hidden">
          <div className="border-b border-neutral-800 px-5 py-5">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-md border border-neutral-700 bg-neutral-900 text-neutral-300">
                <LockIcon className="h-5 w-5" />
              </span>
              <div>
                <h2 className="text-base font-semibold text-neutral-50">Accès opérateur</h2>
                <p className="text-xs text-neutral-500">Authentification locale JWT</p>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 p-5">
            <label className="form-field">
              <span>Identifiant</span>
              <div className="form-input-shell">
                <UserIcon className="h-4 w-4 text-neutral-500" />
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  autoComplete="username"
                  required
                />
              </div>
            </label>

            <label className="form-field">
              <span>Mot de passe</span>
              <div className="form-input-shell">
                <LockIcon className="h-4 w-4 text-neutral-500" />
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete="current-password"
                  required
                />
              </div>
            </label>

            {error && (
              <div className="rounded-md border border-red-500/30 bg-red-950/25 px-3 py-2 text-sm text-red-200">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="primary-button w-full"
            >
              {loading ? (
                <>
                  <ActivityIcon className="h-4 w-4 animate-pulse" />
                  Vérification...
                </>
              ) : (
                <>
                  <ShieldIcon className="h-4 w-4" />
                  Entrer dans la console
                </>
              )}
            </button>
          </form>
        </section>
      </main>
    </div>
  )
}

export default LoginPage
