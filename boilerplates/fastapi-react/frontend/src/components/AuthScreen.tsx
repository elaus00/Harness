import { useState } from 'react'
import type { FormEvent } from 'react'
import { ArrowRight, Check, Layers3, ShieldCheck } from 'lucide-react'
import { api, errorMessage } from '../lib/api'
import type { User } from '../lib/api'
import { Brand, Button, TextField } from './ui'

export default function AuthScreen({ onAuthenticated }: { onAuthenticated: (user: User) => void }) {
  const [register, setRegister] = useState(false)
  const [pending, setPending] = useState(false)
  const [error, setError] = useState('')
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    setPending(true); setError('')
    try {
      const user = await api<User>(register ? '/auth/register' : '/auth/login', 'POST', {
        email: data.get('email'), password: data.get('password'), ...(register ? { name: data.get('name') } : {}),
      })
      onAuthenticated(user)
    } catch (error) { setError(errorMessage(error)) }
    finally { setPending(false) }
  }
  return <div className="auth-page">
    <header className="auth-header"><Brand /><span>나만의 작업 공간</span></header>
    <main className="auth-main">
      <section className="auth-story">
        <span className="eyebrow">LESS FRICTION. MORE FOCUS.</span>
        <h1>좋은 작업의 시작,<br /><span>정돈된 워크스페이스.</span></h1>
        <p>흩어진 업무를 한곳에 모으고,<br />지금 중요한 일에 집중하세요.</p>
        <div className="story-board" aria-hidden="true">
          <div className="story-board-title"><Layers3 size={18} /> 프로젝트의 다음 단계 <span>3개의 업무</span></div>
          <div><i className="story-check"><Check size={12} /></i><span>작업의 기준을 세우고</span><b className="tiny-badge">완료</b></div>
          <div><i className="story-dot" /><span>하나씩 만들어가고</span><b className="tiny-badge blue">진행 중</b></div>
          <div><i className="story-empty" /><span>배운 것을 다음 작업으로</span><b className="tiny-badge neutral">예정</b></div>
        </div>
        <p className="story-note"><ShieldCheck size={16} /> 개인 작업은 내 계정 안에서 안전하게.</p>
      </section>
      <section className="auth-card" aria-labelledby="auth-title">
        <div className="small-brand"><Layers3 size={24} /></div>
        <h2 id="auth-title">{register ? '워크스페이스 시작하기' : '다시 만나서 반가워요'}</h2>
        <p>{register ? '계정을 만들고 나만의 업무를 정리하세요.' : '로그인하고 작업을 이어가세요.'}</p>
        <form onSubmit={submit}>
          {register && <TextField id="name" name="name" label="이름" autoComplete="name" placeholder="어떻게 불러드릴까요?" required maxLength={60} />}
          <TextField id="email" name="email" label="이메일" type="email" autoComplete="email" placeholder="name@example.com" required />
          <TextField id="password" name="password" label="비밀번호" type="password" autoComplete={register ? 'new-password' : 'current-password'} placeholder={register ? '12자 이상 입력하세요' : '비밀번호를 입력하세요'} required minLength={register ? 12 : 1} maxLength={128} />
          {error && <div className="error-message" role="alert">{error}</div>}
          <Button variant="primary" className="auth-submit" disabled={pending}>{pending ? '잠시만 기다려 주세요…' : register ? '계정 만들기' : '로그인'}{!pending && <ArrowRight size={16} />}</Button>
        </form>
        <div className="auth-switch">{register ? '이미 계정이 있나요?' : '처음 방문하셨나요?'} <button disabled={pending} onClick={() => { setRegister(!register); setError('') }}>{register ? '로그인' : '계정 만들기'}</button></div>
      </section>
    </main>
    <footer className="auth-footer">HARNESS WORKSPACE <span>집중할 수 있는 환경을 만듭니다.</span></footer>
  </div>
}
