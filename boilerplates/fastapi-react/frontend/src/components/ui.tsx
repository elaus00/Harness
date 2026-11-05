import type { ButtonHTMLAttributes, InputHTMLAttributes } from 'react'
import { Layers3 } from 'lucide-react'
import type { Status } from '../lib/api'

export function Brand() { return <span className="brand"><span className="brand-mark"><Layers3 size={21} strokeWidth={2.5} /></span>harness<span className="brand-edition">workspace</span></span> }
export function Button({ variant = 'default', className = '', ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'default' | 'primary' | 'subtle' }) {
  return <button className={`button button-${variant} ${className}`} {...props} />
}
export function TextField({ label, id, ...props }: InputHTMLAttributes<HTMLInputElement> & { label: string; id: string }) {
  return <label className="field" htmlFor={id}><span>{label}</span><input id={id} {...props} /></label>
}
export function Avatar({ name, small = false }: { name: string; small?: boolean }) {
  return <span className={`avatar ${small ? 'avatar-small' : ''}`} aria-label={name}>{name.slice(0, 1).toUpperCase()}</span>
}
export function StatusBadge({ status }: { status: Status }) {
  const names = { todo: '해야 할 일', in_progress: '진행 중', done: '완료' }
  return <span className={`badge badge-${status}`}><span />{names[status]}</span>
}
