/* ═══════════════════════════════════════════════════
   Admin JS — ZayavkaScript
   All API logic preserved, tab system + toasts added
   ═══════════════════════════════════════════════════ */

/* ── DOM refs ── */
const loginScreen  = document.getElementById('login-screen');
const adminApp     = document.getElementById('admin-app');
const loginForm    = document.getElementById('login-form');
const loginBtn     = document.getElementById('login-btn');
const logoutBtn    = document.getElementById('logout');

const serviceForm    = document.getElementById('service-form');
const masterForm     = document.getElementById('master-form');
const timeForm       = document.getElementById('time-form');
const applicationForm = document.getElementById('application-form');
const refreshBtn     = document.getElementById('refresh-applications');
const applicationsList = document.getElementById('applications-list');

const today = new Date().toISOString().slice(0, 10);
document.getElementById('time-day').value = today;
document.getElementById('application-date').value = today;

/* ── Toast system ── */
function showToast(title, message = '', type = 'info') {
  const container = document.getElementById('toast-container');
  const icons = { success: 'fa-circle-check', error: 'fa-circle-xmark', info: 'fa-circle-info' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <i class="toast-icon fa-solid ${icons[type] || icons.info}"></i>
    <div class="toast-body">
      <div class="toast-title">${title}</div>
      ${message ? `<div class="toast-msg">${message}</div>` : ''}
    </div>
  `;
  container.appendChild(toast);
  setTimeout(() => { toast.classList.add('fade-out'); setTimeout(() => toast.remove(), 300); }, 4000);
}

/* ── Tab switching ── */
const tabMeta = {
  'tab-applications':    { title: 'Заявки',        subtitle: 'Управление активными заявками' },
  'tab-services':        { title: 'Услуги',         subtitle: 'Создание и управление услугами' },
  'tab-masters':         { title: 'Мастера',        subtitle: 'Добавление новых мастеров' },
  'tab-slots':           { title: 'Слоты времени',  subtitle: 'Расписание работы мастеров' },
  'tab-new-application': { title: 'Новая заявка',   subtitle: 'Ручное создание заявки администратором' },
};

function switchTab(tabId) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-link[data-tab]').forEach(b => b.classList.remove('active'));

  const panel = document.getElementById(tabId);
  const navBtn = document.querySelector(`.nav-link[data-tab="${tabId}"]`);
  if (panel) panel.classList.add('active');
  if (navBtn) navBtn.classList.add('active');

  const meta = tabMeta[tabId] || {};
  document.getElementById('current-tab-title').textContent    = meta.title    || '';
  document.getElementById('current-tab-subtitle').textContent = meta.subtitle || '';

  /* Show/hide refresh button only on applications tab */
  refreshBtn.style.display = tabId === 'tab-applications' ? '' : 'none';
}

document.querySelectorAll('.nav-link[data-tab]').forEach(btn => {
  btn.addEventListener('click', () => switchTab(btn.dataset.tab));
});

/* ── API helper ── */
async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || 'Запрос не выполнен');
  return payload;
}

/* ── Status badge ── */
const statusLabels = { new: 'Новая', in_progress: 'В работе', completed: 'Завершена', canceled: 'Отменена' };

/* ── Render applications ── */
async function refreshApplications() {
  applicationsList.innerHTML = `<div class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><p>Загрузка заявок...</p></div>`;
  const payload = await api('/api/v1/admin/applications/actual', { method: 'GET' });
  const items = payload.data || [];

  if (!items.length) {
    applicationsList.innerHTML = `<div class="empty-state"><i class="fa-solid fa-inbox"></i><p>Активных заявок нет</p></div>`;
    return;
  }

  applicationsList.innerHTML = items.map(item => `
    <div class="app-row">
      <div class="app-row-info">
        <div class="app-row-name">
          <i class="fa-solid fa-user text-muted" style="margin-right:6px;font-size:12px"></i>${item.customer_name}
          <span class="badge badge-${item.status}" style="margin-left:8px">${statusLabels[item.status] || item.status}</span>
        </div>
        <div class="app-row-meta">
          <span><i class="fa-solid fa-tag"></i> ${item.service_name}</span>
          <span><i class="fa-solid fa-calendar"></i> ${item.appointment_date}</span>
          <span><i class="fa-solid fa-clock"></i> ${item.time_slot}</span>
          ${item.master_name ? `<span><i class="fa-solid fa-user-tie"></i> ${item.master_name}</span>` : ''}
          ${item.comment ? `<span><i class="fa-solid fa-comment"></i> ${item.comment}</span>` : ''}
        </div>
      </div>
      <div class="app-row-actions">
        <button class="btn btn-success btn-sm" data-status="completed" data-id="${item.id}">
          <i class="fa-solid fa-check"></i> Завершить
        </button>
        <button class="btn btn-danger btn-sm" data-status="canceled" data-id="${item.id}">
          <i class="fa-solid fa-xmark"></i> Отменить
        </button>
      </div>
    </div>
  `).join('');
}

/* ── Load services for admin ── */
async function loadServicesForAdmin() {
  const payload = await fetch('/api/v1/public/services').then(r => r.json());
  const services = payload.data || [];
  const options = services.map(s => `<option value="${s.id}">${s.name} (${s.price} ₽)</option>`);
  document.getElementById('application-service-id').innerHTML = options.join('');

  /* Also render in services tab */
  const list = document.getElementById('services-admin-list');
  if (!services.length) {
    list.innerHTML = `<div class="empty-state"><i class="fa-solid fa-box-open"></i><p>Услуг нет</p></div>`;
    return;
  }
  list.innerHTML = services.map(s => `
    <div class="service-card" style="cursor:default">
      <div class="service-icon"><i class="fa-solid fa-sparkles"></i></div>
      <div class="service-info">
        <div class="service-name">${s.name}</div>
        <div class="service-desc">${s.description || '—'}</div>
        <div class="service-price">${s.price} ₽</div>
      </div>
    </div>
  `).join('');
}

/* ── Load masters for admin ── */
async function loadMastersForAdmin(day = today) {
  const payload = await fetch(`/api/v1/public/masters?day=${encodeURIComponent(day)}`).then(r => r.json());
  const masters = payload.data || [];
  const options = masters.map(m => `<option value="${m.id}">${m.name}</option>`);
  document.getElementById('time-master-id').innerHTML = options.join('');
  document.getElementById('application-master-id').innerHTML = options.join('');
}

/* ── Login ── */
loginForm.addEventListener('submit', async event => {
  event.preventDefault();
  loginBtn.classList.add('btn-loading');
  loginBtn.disabled = true;

  const login    = document.getElementById('login').value.trim();
  const password = document.getElementById('password').value.trim();

  await new Promise(r => setTimeout(r, 400)); /* tiny UX delay */

  if (login !== 'admin' || password !== 'admin') {
    loginBtn.classList.remove('btn-loading');
    loginBtn.disabled = false;
    showToast('Ошибка входа', 'Неверный логин или пароль', 'error');
    return;
  }

  loginScreen.classList.add('hidden');
  adminApp.classList.remove('hidden');
  switchTab('tab-applications');

  await Promise.all([loadServicesForAdmin(), loadMastersForAdmin()]);
  await refreshApplications();

  showToast('Добро пожаловать!', 'Вы вошли как администратор', 'success');
  loginBtn.classList.remove('btn-loading');
  loginBtn.disabled = false;
});

/* ── Logout ── */
logoutBtn.addEventListener('click', () => {
  adminApp.classList.add('hidden');
  loginScreen.classList.remove('hidden');
  loginForm.reset();
  document.getElementById('login').value = 'admin';
  document.getElementById('password').value = 'admin';
});

/* ── Create service ── */
serviceForm.addEventListener('submit', async event => {
  event.preventDefault();
  const btn = serviceForm.querySelector('button[type=submit]');
  btn.classList.add('btn-loading'); btn.disabled = true;
  try {
    await api('/api/v1/admin/services', {
      method: 'POST',
      body: JSON.stringify({
        name:        document.getElementById('service-name').value.trim(),
        description: document.getElementById('service-description').value.trim() || null,
        price:       Number(document.getElementById('service-price').value),
        photo_url:   document.getElementById('service-photo').value.trim() || null,
      }),
    });
    showToast('Услуга создана', '', 'success');
    serviceForm.reset();
    await loadServicesForAdmin();
  } catch (e) {
    showToast('Ошибка', e.message, 'error');
  } finally {
    btn.classList.remove('btn-loading'); btn.disabled = false;
  }
});

/* ── Create master ── */
masterForm.addEventListener('submit', async event => {
  event.preventDefault();
  const btn = masterForm.querySelector('button[type=submit]');
  btn.classList.add('btn-loading'); btn.disabled = true;
  try {
    const result = await api('/api/v1/admin/masters', {
      method: 'POST',
      body: JSON.stringify({ name: document.getElementById('master-name').value.trim() }),
    });
    showToast('Мастер создан', `ID: ${result.data.id}`, 'success');
    masterForm.reset();
    await loadMastersForAdmin(document.getElementById('time-day').value || today);
    document.getElementById('time-master-id').value = String(result.data.id);
    document.getElementById('application-master-id').value = String(result.data.id);
  } catch (e) {
    showToast('Ошибка', e.message, 'error');
  } finally {
    btn.classList.remove('btn-loading'); btn.disabled = false;
  }
});

/* ── Add time slot ── */
timeForm.addEventListener('submit', async event => {
  event.preventDefault();
  const btn = timeForm.querySelector('button[type=submit]');
  btn.classList.add('btn-loading'); btn.disabled = true;
  try {
    await api(`/api/v1/admin/masters/${document.getElementById('time-master-id').value}/times`, {
      method: 'POST',
      body: JSON.stringify({
        day:       document.getElementById('time-day').value,
        time_slot: document.getElementById('time-slot').value,
      }),
    });
    showToast('Слот добавлен', '', 'success');
    timeForm.reset();
    document.getElementById('time-day').value = today;
    await loadMastersForAdmin(today);
  } catch (e) {
    showToast('Ошибка', e.message, 'error');
  } finally {
    btn.classList.remove('btn-loading'); btn.disabled = false;
  }
});

/* ── Create application (admin) ── */
applicationForm.addEventListener('submit', async event => {
  event.preventDefault();
  const btn = applicationForm.querySelector('button[type=submit]');
  btn.classList.add('btn-loading'); btn.disabled = true;
  try {
    const result = await api('/api/v1/admin/applications', {
      method: 'POST',
      body: JSON.stringify({
        service_id:       Number(document.getElementById('application-service-id').value),
        master_id:        Number(document.getElementById('application-master-id').value),
        name:             document.getElementById('application-name').value.trim(),
        telephone_number: document.getElementById('application-phone').value.trim(),
        appointment_date: document.getElementById('application-date').value,
        time_slot:        document.getElementById('application-time').value,
        comment:          document.getElementById('application-comment').value.trim() || null,
      }),
    });
    showToast('Заявка создана', `ID: ${result.data.id}`, 'success');
    applicationForm.reset();
    document.getElementById('application-date').value = today;
    await refreshApplications();
    switchTab('tab-applications');
  } catch (e) {
    showToast('Ошибка', e.message, 'error');
  } finally {
    btn.classList.remove('btn-loading'); btn.disabled = false;
  }
});

/* ── Refresh button ── */
refreshBtn.addEventListener('click', () =>
  refreshApplications().catch(e => showToast('Ошибка', e.message, 'error'))
);

/* ── Change status (complete/cancel) ── */
applicationsList.addEventListener('click', async event => {
  const button = event.target.closest('button[data-id][data-status]');
  if (!button) return;
  button.classList.add('btn-loading'); button.disabled = true;
  try {
    await api(`/api/v1/admin/applications/${button.dataset.id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status: button.dataset.status }),
    });
    const labels = { completed: 'Заявка завершена', canceled: 'Заявка отменена' };
    showToast(labels[button.dataset.status] || 'Статус обновлён', '', 'success');
    await refreshApplications();
  } catch (e) {
    showToast('Ошибка', e.message, 'error');
    button.classList.remove('btn-loading'); button.disabled = false;
  }
});

/* ── Boot ── */
switchTab('tab-applications');
