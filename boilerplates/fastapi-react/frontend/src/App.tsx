import { useCallback, useEffect, useState } from 'react'
import AuthScreen from './components/AuthScreen'
import Dashboard from './components/Dashboard'
import { Button } from './components/ui'
import { api, ApiError, errorMessage } from './lib/api'
import type { User } from './lib/api'
import './App.css'

export default function App() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const restore = useCallback(async () => {
    try { setUser(await api<User>('/auth/me')) }
    catch (error) { if (!(error instanceof ApiError && error.status === 401)) setError(errorMessage(error)) }
    finally { setLoading(false) }
  }, [])
  useEffect(() => { void Promise.resolve().then(restore) }, [restore])
  const onExpired = useCallback(() => setUser(null), [])
  if (loading) return <main className="loading-screen" role="status"><span className="loader" />워크스페이스를 준비하고 있습니다.</main>
  if (error) return <main className="loading-screen"><p role="alert">{error}</p><Button onClick={() => { setLoading(true); setError(''); void restore() }}>다시 연결</Button></main>
  return user ? <Dashboard user={user} onExpired={onExpired} /> : <AuthScreen onAuthenticated={setUser} />
}
