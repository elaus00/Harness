import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { X } from 'lucide-react'
import { api, errorMessage } from '../lib/api'
import { Button, TextField } from './ui'

export default function CreateTask({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null)
  const [pending, setPending] = useState(false)
  const [error, setError] = useState('')
  useEffect(() => { const element = dialog.current; element?.showModal(); return () => element?.close() }, [])
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setPending(true); setError('')
    const data = Object.fromEntries(new FormData(event.currentTarget))
    try { await api('/tasks', 'POST', data); onCreated(); onClose() }
    catch (error) { setError(errorMessage(error)) }
    finally { setPending(false) }
  }
  return <dialog ref={dialog} className="task-dialog" onCancel={onClose} aria-labelledby="create-title">
    <div className="dialog-heading"><h2 id="create-title">새 업무 만들기</h2><Button variant="subtle" aria-label="닫기" onClick={onClose}><X size={20} /></Button></div>
    <p className="muted">다음에 할 일을 구체적으로 적어보세요.</p>
    <form onSubmit={submit}>
      <TextField id="task-title" label="업무 제목" name="title" placeholder="어떤 일을 해야 하나요?" required maxLength={200} autoFocus />
      <div className="form-row"><label className="field">프로젝트<select name="project"><option>Harness</option><option>제품 디자인</option><option>개발 환경</option></select></label>
        <label className="field">우선순위<select name="priority" defaultValue="medium"><option value="high">높음</option><option value="medium">보통</option><option value="low">낮음</option></select></label></div>
      {error && <p className="error-message" role="alert">{error}</p>}
      <div className="dialog-actions"><Button type="button" onClick={onClose}>취소</Button><Button variant="primary" disabled={pending}>{pending ? '만드는 중…' : '업무 만들기'}</Button></div>
    </form>
  </dialog>
}
