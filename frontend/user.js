/* ── DOM refs ── */
const serviceSelect   = document.getElementById('service-select');
const servicesList    = document.getElementById('services-list');
const mastersList     = document.getElementById('masters-list');
const servicesStatus  = document.getElementById('services-status');
const form            = document.getElementById('application-form');
const dateInput       = document.getElementById('appointment-date');
const reloadMastersBtn = document.getElementById('reload-masters');
const masterSelect    = document.getElementById('master-select');
const submitBtn       = document.getElementById('submit-btn');

/* ── Init date ── */
const today = new Date().toISOString().slice(0, 10);
dateInput.value = today;

/* ── Toast system ── */
function showToast(title, message = '', type = 'info') {
  const container = document.getElementById('toast-container');
  const icons = { success: 'fa-circle-check', error: 'fa-circle-xmark', info: 'fa-circle-info' };
  const labels = { success: 'Успешно', error: 'Ошибка', info: 'Информация' };

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

  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

/* ── Status pill ── */
function setStatus(text, type = '') {
  servicesStatus.textContent = text;
  servicesStatus.className = 'status-pill' + (type ? ` ${type}` : '');
}

/* ── Initials avatar ── */
function initials(name) {
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase();
}

/* ── Load services ── */
async function loadServices() {
  setStatus('Загрузка...', 'loading');
  servicesList.innerHTML = `<div class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><p>Загрузка услуг...</p></div>`;

  const response = await fetch('/api/v1/public/services');
  const payload  = await response.json();
  const services = payload.data || [];

  /* Populate select */
  serviceSelect.innerHTML = services.map(s =>
    `<option value="${s.id}">${s.name} · ${s.price} ₽</option>`
  ).join('');

  /* Render cards */
  if (!services.length) {
    servicesList.innerHTML = `<div class="empty-state"><i class="fa-solid fa-box-open"></i><p>Услуг пока нет</p></div>`;
    setStatus('Нет услуг');
    return;
  }

  servicesList.innerHTML = services.map(s => `
    <div class="service-card" data-id="${s.id}" role="button" tabindex="0">
      <div class="service-icon"><i class="fa-solid fa-sparkles"></i></div>
      <div class="service-info">
        <div class="service-name">${s.name}</div>
        <div class="service-desc">${s.description || 'Описание не указано'}</div>
        <div class="service-price">${s.price} ₽</div>
      </div>
    </div>
  `).join('');

  /* Sync card click → select */
  servicesList.querySelectorAll('.service-card').forEach(card => {
    const activate = () => {
      servicesList.querySelectorAll('.service-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      serviceSelect.value = card.dataset.id;
    };
    card.addEventListener('click', activate);
    card.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') activate(); });
  });

  /* Pre-select first */
  servicesList.querySelector('.service-card')?.classList.add('selected');
  setStatus(`${services.length} услуг`, 'success');
}

/* ── Load masters ── */
async function loadMasters() {
  const day = dateInput.value;
  mastersList.innerHTML = `<div class="empty-state"><i class="fa-solid fa-spinner fa-spin"></i><p>Загрузка мастеров...</p></div>`;

  const response = await fetch(`/api/v1/public/masters?day=${encodeURIComponent(day)}`);
  const payload  = await response.json();
  const masters  = payload.data || [];

  if (!masters.length) {
    mastersList.innerHTML = `<div class="empty-state"><i class="fa-solid fa-user-slash"></i><p>Нет доступных мастеров на выбранную дату</p></div>`;
  } else {
    mastersList.innerHTML = masters.map(m => `
      <div class="master-card">
        <div class="master-avatar">${initials(m.name)}</div>
        <div class="master-info">
          <div class="master-name">${m.name}</div>
          <div class="slots-wrap">
            ${m.times.length
              ? m.times.map(slot => `<span class="slot-chip"><i class="fa-solid fa-clock"></i>${slot.time_slot}</span>`).join('')
              : `<span class="no-slots">Нет свободных слотов</span>`
            }
          </div>
        </div>
      </div>
    `).join('');
  }

  /* Populate master select */
  const opts = ['<option value="">Любой мастер</option>'];
  masters.forEach(m => opts.push(`<option value="${m.id}">${m.name}</option>`));
  masterSelect.innerHTML = opts.join('');
}

/* ── Form submit ── */
form.addEventListener('submit', async event => {
  event.preventDefault();
  submitBtn.classList.add('btn-loading');
  submitBtn.disabled = true;

  const payload = {
    service_id:       Number(serviceSelect.value),
    master_id:        masterSelect.value ? Number(masterSelect.value) : null,
    name:             document.getElementById('name').value.trim(),
    telephone_number: document.getElementById('phone').value.trim(),
    appointment_date: dateInput.value,
    time_slot:        document.getElementById('time-slot').value,
    comment:          document.getElementById('comment').value.trim() || null,
  };

  const response = await fetch('/api/v1/public/applications', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(payload),
  });

  const result = await response.json();
  submitBtn.classList.remove('btn-loading');
  submitBtn.disabled = false;

  if (!response.ok) {
    showToast('Ошибка отправки', result.detail || 'Попробуйте ещё раз', 'error');
    return;
  }

  showToast('Заявка отправлена!', `Номер заявки: #${result.data.id}`, 'success');
  form.reset();
  dateInput.value = today;
  await loadMasters();
});

/* ── Events ── */
dateInput.addEventListener('change', loadMasters);
reloadMastersBtn.addEventListener('click', loadMasters);

/* ── Boot ── */
loadServices()
  .then(loadMasters)
  .catch(() => showToast('Ошибка загрузки', 'Не удалось загрузить данные с сервера', 'error'));
