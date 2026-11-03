import { useState } from 'react'
import './App.css'

type Connection = 'idle' | 'loading' | 'success' | 'error'

export default function App() {
  const [connection, setConnection] = useState<Connection>('idle')
  const [message, setMessage] = useState('버튼을 눌러 API 연결을 확인하세요.')

  async function checkConnection() {
    setConnection('loading')
    setMessage('API에 연결하고 있습니다…')
    try {
      const response = await fetch('/api/v1/health', {
        signal: AbortSignal.timeout(5000),
        headers: { Accept: 'application/json' },
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const data: unknown = await response.json()
      if (!data || typeof data !== 'object' || !('status' in data) || data.status !== 'ok') {
        throw new Error('Unexpected response')
      }
      setConnection('success')
      setMessage('연결되었습니다. 새 프로젝트를 시작할 준비가 됐습니다.')
    } catch {
      setConnection('error')
      setMessage('API에 연결하지 못했습니다. 백엔드 실행 상태를 확인하고 다시 시도하세요.')
    }
  }

  return (
    <main>
      <p className="eyebrow">HARNESS / STARTER</p>
      <h1>작은 시작,<br />단단한 기반.</h1>
      <p className="intro">FastAPI + React + Vite</p>
      <section aria-labelledby="connection-heading">
        <h2 id="connection-heading">개발 환경 확인</h2>
        <p role="status" data-state={connection}>{message}</p>
        <button onClick={checkConnection} disabled={connection === 'loading'}>
          {connection === 'loading' ? '연결 확인 중…' : 'API 연결 확인'}
        </button>
      </section>
    </main>
  )
}
