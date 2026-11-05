export type User = { id: number; name: string; email: string }
export type Status = 'todo' | 'in_progress' | 'done'
export type Project = 'Harness' | '제품 디자인' | '개발 환경'
export type Priority = 'high' | 'medium' | 'low'
export type Task = { id: number; title: string; project: Project; status: Status; priority: Priority; created_at: string }
export type Workspace = { tasks: Task[]; events: { id: number; message: string; created_at: string }[] }
export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) { super(message); this.status = status }
}
export async function api<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    method, credentials: 'same-origin', signal: AbortSignal.timeout(15000),
    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'Harness' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new ApiError(typeof error.detail === 'string' ? error.detail : '입력 내용을 확인하고 다시 시도하세요.', response.status)
  }
  return response.status === 204 ? undefined as T : response.json()
}
export function errorMessage(error: unknown) {
  return error instanceof ApiError ? error.message : '연결을 확인하고 다시 시도해 주세요.'
}
