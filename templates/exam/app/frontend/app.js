const $ = (id) => document.getElementById(id);
let canWrite = false;
let selectedJob = null;
async function api(path, body) {
  const response = await fetch(`/api${path}`, {
    method: body === undefined ? 'GET' : 'POST', credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'Harness' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) {
    if (response.status === 401) { canWrite = false; $('workflow').hidden = true; }
    throw new Error(JSON.stringify(data.error, null, 2));
  }
  return data;
}
async function action(work) {
  $('message').textContent = '';
  try { await work(); } catch (error) { $('message').textContent = error.message; }
}
async function files() {
  const result = {};
  for (const file of $('files').files) {
    if (Object.hasOwn(result, file.name)) throw new Error('파일명이 중복됩니다.');
    const bytes = await file.arrayBuffer();
    result[file.name] = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  }
  return { files: result };
}
async function refresh() {
  const data = await api('/datasets');
  $('datasets').textContent = JSON.stringify(data, null, 2);
  $('jobs').replaceChildren();
  for (const job of (await api('/jobs')).jobs) {
    const item = document.createElement('li');
    const text = document.createElement('span');
    text.textContent = `${job.id} · ${job.status}${job.recalculation_required ? ' · 재계산 필요' : ''} `;
    item.append(text);
    if (job.status === 'completed' && !job.recalculation_required) {
      const button = document.createElement('button');
      button.textContent = '결과 보기';
      button.onclick = () => action(async () => {
        const result = await api(`/jobs/${job.id}/export`);
        $('export').value = JSON.stringify(result, null, 2);
        selectedJob = job.id;
        $('save').disabled = !canWrite;
      });
      item.append(button);
    }
    $('jobs').append(item);
  }
  selectedJob = null;
  $('export').value = '';
  $('save').disabled = true;
}
async function boot() {
  const health = await api('/health');
  $('health').textContent = health.database === 'ready' ? 'DB 연결 정상' : 'DB 확인 필요';
  const config = await api('/config');
  canWrite = false;
  selectedJob = null;
  $('export').value = '';
  $('save').disabled = true;
  $('logout').hidden = true;
  $('workflow').hidden = true;
  $('login').hidden = false;
  $('auth').hidden = !config.auth_enabled;
  $('empty').hidden = config.workflow_enabled;
  let user;
  try { user = await api('/auth/me'); } catch (error) {
    if (config.auth_enabled) { $('identity').textContent = '로그인이 필요합니다.'; return; }
    throw error;
  }
  canWrite = user.can_write;
  $('login').hidden = config.auth_enabled;
  $('identity').textContent = user.username ? `${user.username} · ${user.role}` : '';
  $('logout').hidden = !config.auth_enabled;
  $('workflow').hidden = !config.workflow_enabled;
  for (const id of ['validate', 'apply', 'generate']) $(id).disabled = !canWrite;
  if (config.workflow_enabled) await refresh();
}
$('login').onsubmit = (event) => { event.preventDefault(); action(async () => {
  const form = new FormData(event.target);
  await api('/auth/login', Object.fromEntries(form));
  event.target.reset();
  await boot();
}); };
$('logout').onclick = () => action(async () => { await api('/auth/logout', {}); await boot(); });
$('validate').onclick = () => action(async () => {
  $('message').textContent = JSON.stringify(await api('/datasets/validate', await files()), null, 2);
});
$('apply').onclick = () => action(async () => { await api('/datasets/apply', await files()); await refresh(); });
$('generate').onclick = () => action(async () => {
  $('generate').disabled = true;
  try { await api('/jobs', JSON.parse($('options').value)); }
  finally { $('generate').disabled = !canWrite; await refresh(); }
});
$('refresh').onclick = () => action(refresh);
$('copy').onclick = () => action(async () => {
  try { await navigator.clipboard.writeText($('export').value); $('message').textContent = '복사했습니다.'; }
  catch { $('export').focus(); $('export').select(); $('message').textContent = '선택한 내용을 직접 복사하세요.'; }
});
$('save').onclick = () => action(async () => {
  if (!selectedJob) return;
  $('message').textContent = (await api(`/jobs/${selectedJob}/export`, {})).path;
});
action(boot);
