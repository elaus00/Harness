import { useCallback, useEffect, useState } from 'react'
import { ArrowDown, ArrowUp, ArrowUpRight, Check, CheckCheck, ChevronRight, Circle, Clock3, FolderKanban, LayoutDashboard, ListTodo, LogOut, Menu, Plus, Search, SlidersHorizontal, Sparkles, X } from 'lucide-react'
import { api, ApiError, errorMessage } from '../lib/api'
import type { Project, Status, User, Workspace } from '../lib/api'
import { Avatar, Brand, Button, StatusBadge } from './ui'
import CreateTask from './CreateTask'

const projects: Project[] = ['Harness', '제품 디자인', '개발 환경']
const projectDescriptions = ['더 나은 작업 방식을 위한 기반', '일관되고 명확한 사용자 경험', '안정적인 개발과 빠른 실행']
const statusNames = { all: '전체', todo: '해야 할 일', in_progress: '진행 중', done: '완료' }

export default function Dashboard({ user, onExpired }: { user: User; onExpired: () => void }) {
  const [workspace, setWorkspace] = useState<Workspace>({ tasks: [], events: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<Status | 'all'>('all')
  const [project, setProject] = useState<Project | 'all'>('all')
  const [page, setPage] = useState<'overview' | 'tasks'>('overview')
  const [creating, setCreating] = useState(false)
  const [busy, setBusy] = useState(false)
  const [mobileMenu, setMobileMenu] = useState(false)
  const load = useCallback(async () => {
    try { setWorkspace(await api<Workspace>('/workspace')); setError('') }
    catch (error) { if (error instanceof ApiError && error.status === 401) onExpired(); else setError(errorMessage(error)) }
    finally { setLoading(false) }
  }, [onExpired])
  useEffect(() => { void Promise.resolve().then(load) }, [load])
  async function mutate(path: string, method = 'POST', data?: unknown) {
    setBusy(true); setError('')
    try { await api(path, method, data); await load() }
    catch (error) { if (error instanceof ApiError && error.status === 401) onExpired(); else setError(errorMessage(error)) }
    finally { setBusy(false) }
  }
  async function logout() {
    setBusy(true)
    try { await api('/auth/logout', 'POST'); onExpired() }
    catch (error) { setError(errorMessage(error)) }
    finally { setBusy(false) }
  }
  const tasks = workspace.tasks
  const counts = { all: tasks.length, todo: tasks.filter(t => t.status === 'todo').length, in_progress: tasks.filter(t => t.status === 'in_progress').length, done: tasks.filter(t => t.status === 'done').length }
  const filtered = tasks.filter(t => (status === 'all' || t.status === status) && (project === 'all' || t.project === project) && `${t.title} HRN-${t.id}`.toLowerCase().includes(search.toLowerCase()))
  function navigate(next: 'overview' | 'tasks', chosen: Project | 'all' = 'all') { setPage(next); setProject(chosen); setStatus('all'); setMobileMenu(false) }
  return <div className="app-shell">
    <header className="topbar"><Button variant="subtle" className="mobile-toggle" onClick={() => setMobileMenu(!mobileMenu)} aria-label="메뉴 열기" aria-expanded={mobileMenu}><Menu size={20} /></Button><Brand />
      <label className="global-search"><Search size={17} /><input aria-label="업무 검색" placeholder="업무 검색…" value={search} onChange={e => setSearch(e.target.value)} /><span>검색</span></label>
      <div className="topbar-right"><Button variant="primary" onClick={() => setCreating(true)}><Plus size={16} />만들기</Button><Avatar name={user.name} /></div>
    </header>
    {mobileMenu && <button className="sidebar-scrim" aria-label="메뉴 닫기" onClick={() => setMobileMenu(false)} />}
    <aside className={`sidebar ${mobileMenu ? 'sidebar-open' : ''}`}>
      <div className="workspace-switch"><span className="workspace-icon">H</span><div><strong>My workspace</strong><span>개인 워크스페이스</span></div></div>
      <nav aria-label="주 메뉴"><button className={page === 'overview' ? 'nav-item active' : 'nav-item'} onClick={() => navigate('overview')}><LayoutDashboard size={18} />대시보드</button>
        <button className={page === 'tasks' && project === 'all' ? 'nav-item active' : 'nav-item'} onClick={() => navigate('tasks')}><ListTodo size={18} />내 업무<span className="nav-count">{counts.todo + counts.in_progress}</span></button>
        <p className="nav-heading">프로젝트 <span>{projects.length}</span></p>
        {projects.map((name, i) => <button key={name} className={project === name ? 'nav-item active' : 'nav-item'} onClick={() => navigate('tasks', name)}><span className={`project-dot project-${i}`} />{name}</button>)}
      </nav>
      <div className="sidebar-bottom"><div className="workspace-tip"><Sparkles size={17} /><strong>작은 진전도 기록하세요</strong><p>오늘의 작업이 내일의<br />더 나은 시작이 됩니다.</p></div>
        <div className="profile"><Avatar name={user.name} small /><div><strong>{user.name}</strong><span title={user.email}>{user.email}</span></div><Button variant="subtle" aria-label="로그아웃" onClick={logout} disabled={busy}><LogOut size={17} /></Button></div></div>
    </aside>
    <main className="dashboard-main">
      <div className="breadcrumb">워크스페이스 <ChevronRight size={13} /><span>{project !== 'all' ? project : page === 'overview' ? '대시보드' : '내 업무'}</span></div>
      <div className="page-heading"><div><h1>{page === 'overview' ? '대시보드' : project === 'all' ? '내 업무' : project}</h1><p>{page === 'overview' ? `${user.name}님, 오늘도 중요한 일부터 시작해 볼까요?` : '해야 할 일을 정리하고 진행 상황을 업데이트하세요.'}</p></div><span className="workspace-label"><span />개인 공간</span></div>
      {error && <div className="error-banner" role="alert">{error}<Button onClick={load}>다시 시도</Button></div>}
      {loading ? <div className="section-loading" role="status">업무를 불러오고 있습니다…</div> : <>
      {page === 'overview' && <>
        <div className="summary-strip">
          <div><span><ListTodo size={16} />전체 업무</span><strong>{counts.all}<small>개의 업무</small></strong></div>
          <div><span><Circle size={16} />해야 할 일</span><strong>{counts.todo}<small>다음 시작을 기다려요</small></strong></div>
          <div><span><Clock3 size={16} />진행 중</span><strong className="blue-text">{counts.in_progress}<small>차근차근 진행 중</small></strong></div>
          <div><span><CheckCheck size={16} />완료</span><strong className="green-text">{counts.done}<small>{counts.all ? `${Math.round(counts.done / counts.all * 100)}% 완료했어요` : '첫 완료를 만들어보세요'}</small></strong></div>
        </div>
        <section className="projects-section"><div className="section-title"><h2>프로젝트</h2><span className="muted">나의 작업을 한눈에</span></div><div className="project-grid">
          {projects.map((name, i) => { const items = tasks.filter(t => t.project === name); const completed = items.filter(t => t.status === 'done').length; return <button className="project-card" key={name} onClick={() => navigate('tasks', name)}>
            <div className="project-card-heading"><span className={`project-icon project-${i}`}><FolderKanban size={20} /></span><ArrowUpRight size={16} /></div><h3>{name}</h3><p>{projectDescriptions[i]}</p>
            <div className="project-progress-label"><span>{items.length}개 업무</span><span>{items.length ? Math.round(completed / items.length * 100) : 0}%</span></div>
            <div className="progress-track"><span className={`progress-${i}`} style={{ width: `${items.length ? completed / items.length * 100 : 0}%` }} /></div>
          </button> })}
        </div></section>
      </>}
      <div className={page === 'overview' ? 'work-grid' : 'work-grid full-width'}>
        <section className="task-panel"><div className="section-title"><h2>나의 업무 <span className="number-chip">{tasks.length}</span></h2><Button variant="subtle" onClick={() => setCreating(true)}><Plus size={16} />업무 추가</Button></div>
          <div className="task-toolbar"><div className="tabs" aria-label="업무 상태 필터">{(Object.keys(statusNames) as (Status | 'all')[]).map(key => <button key={key} aria-pressed={status === key} className={status === key ? 'tab selected' : 'tab'} onClick={() => setStatus(key)}>{statusNames[key]}<span>{counts[key]}</span></button>)}</div>
            <label className="project-filter"><SlidersHorizontal size={14} /><select aria-label="프로젝트 필터" value={project} onChange={e => setProject(e.target.value as Project | 'all')}><option value="all">모든 프로젝트</option>{projects.map(p => <option key={p}>{p}</option>)}</select></label></div>
          {search && <div className="search-note">“{search}” 검색 결과 <button onClick={() => setSearch('')} aria-label="검색 초기화"><X size={14} /></button></div>}
          {filtered.length ? <div className="table-scroll"><table><thead><tr><th>업무</th><th>상태</th><th>우선순위</th><th>담당자</th></tr></thead><tbody>{filtered.map(task => <tr key={task.id}>
            <td><div className="task-name"><span className={`task-type ${task.status === 'done' ? 'task-complete' : ''}`}><Check size={11} /></span><div><span className="task-id">HRN-{task.id} <i>·</i> {task.project}</span><strong>{task.title}</strong></div></div></td>
            <td><div className="status-control"><StatusBadge status={task.status} /><select aria-label={`${task.title} 상태`} value={task.status} disabled={busy} onChange={e => void mutate(`/tasks/${task.id}`, 'PATCH', { status: e.target.value })}><option value="todo">해야 할 일</option><option value="in_progress">진행 중</option><option value="done">완료</option></select></div></td>
            <td><span className={`priority priority-${task.priority}`}>{task.priority === 'high' ? <ArrowUp size={15} /> : task.priority === 'low' ? <ArrowDown size={15} /> : <span className="equal-mark">=</span>}{ { high: '높음', medium: '보통', low: '낮음' }[task.priority]}</span></td><td><Avatar name={user.name} small /></td>
          </tr>)}</tbody></table></div> : <div className="empty-state"><ListTodo size={30} /><h3>{tasks.length ? '조건에 맞는 업무가 없습니다' : '첫 업무로 시작해 보세요'}</h3><p>{tasks.length ? '검색어나 필터를 변경해 보세요.' : '직접 업무를 만들거나 샘플로 워크스페이스를 둘러보세요.'}</p>{!tasks.length && <Button onClick={() => void mutate('/tasks/sample')} disabled={busy}><Sparkles size={15} />샘플 업무 불러오기</Button>}</div>}
          <div className="table-footer">{filtered.length}개의 업무 <span>변경 사항은 자동으로 저장됩니다</span></div>
        </section>
        {page === 'overview' && <aside className="activity-panel"><div className="section-title"><h2>최근 활동</h2><Clock3 size={16} /></div>{workspace.events.length ? <ol className="activity-list">{workspace.events.map(event => <li key={event.id}><span className="activity-marker" /><div><p>{event.message}</p><time dateTime={event.created_at}>{new Date(event.created_at).toLocaleString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</time></div></li>)}</ol> : <div className="activity-empty">업무를 만들거나 상태를 바꾸면<br />여기에 기록됩니다.</div>}<div className="activity-bottom"><span className="status-dot" />지금, 차곡차곡 쌓이는 중</div></aside>}
      </div></>}
      <footer className="dashboard-footer"><span>작업을 정리하고, 가능성을 넓히세요.</span><span>HARNESS WORKSPACE</span></footer>
    </main>
    {creating && <CreateTask onClose={() => setCreating(false)} onCreated={() => void load()} />}
  </div>
}
