const loginPanel = document.getElementById("login-panel");
const adminApp = document.getElementById("admin-app");
const loginForm = document.getElementById("login-form");
const loginMessage = document.getElementById("admin-login-message");
const logoutBtn = document.getElementById("logout");

const serviceForm = document.getElementById("service-form");
const masterForm = document.getElementById("master-form");
const timeForm = document.getElementById("time-form");
const applicationForm = document.getElementById("application-form");
const refreshApplicationsBtn = document.getElementById("refresh-applications");
const applicationsList = document.getElementById("applications-list");

const serviceMessage = document.getElementById("service-message");
const masterMessage = document.getElementById("master-message");
const applicationMessage = document.getElementById("application-message");

const today = new Date().toISOString().slice(0, 10);
document.getElementById("time-day").value = today;
document.getElementById("application-date").value = today;

function showMessage(node, text, isError = false) {
  node.textContent = text;
  node.classList.toggle("error", isError);
  node.classList.add("show");
}

function clearMessage(node) {
  node.textContent = "";
  node.className = "message";
}

function headers() {
  return {
    "Content-Type": "application/json",
  };
}

function showAdminApp() {
  loginPanel.classList.add("hidden");
  adminApp.classList.remove("hidden");
}

function showLogin() {
  adminApp.classList.add("hidden");
  loginPanel.classList.remove("hidden");
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      ...headers(),
      ...(options.headers || {}),
    },
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || "Запрос не выполнен");
  }
  return payload;
}

async function refreshApplications() {
  const payload = await api("/api/v1/admin/applications/actual", { method: "GET" });
  const items = payload.data || [];

  applicationsList.innerHTML = items.length
    ? items
        .map(
          (item) => `
            <article class="table-item">
              <strong>${item.customer_name}</strong>
              <div class="small muted">${item.service_name} · ${item.appointment_date} · ${item.time_slot}</div>
              <div class="small">Статус: ${item.status}</div>
              <div style="margin-top: 10px; display: flex; gap: 10px; flex-wrap: wrap">
                <button type="button" class="ghost" data-status="completed" data-id="${item.id}">Завершить</button>
                <button type="button" class="ghost" data-status="canceled" data-id="${item.id}">Отменить</button>
              </div>
            </article>
          `,
        )
        .join("")
    : '<div class="muted">Активных заявок нет.</div>';
}

async function loadServicesForAdmin() {
  const payload = await fetch("/api/v1/public/services").then((response) => response.json());
  const services = payload.data || [];
  const options = services.map((service) => `<option value="${service.id}">${service.name} (${service.price} ₽)</option>`);
  document.getElementById("application-service-id").innerHTML = options.join("");
}

async function loadMastersForAdmin(day = today) {
  const payload = await fetch(`/api/v1/public/masters?day=${encodeURIComponent(day)}`).then((response) => response.json());
  const masters = payload.data || [];
  const options = masters.map((master) => `<option value="${master.id}">${master.name}</option>`);
  document.getElementById("time-master-id").innerHTML = options.join("");
  document.getElementById("application-master-id").innerHTML = options.join("");
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage(loginMessage);

  const login = document.getElementById("login").value.trim();
  const password = document.getElementById("password").value.trim();

  if (login !== "admin" || password !== "admin") {
    showMessage(loginMessage, "Неверный логин или пароль", true);
    return;
  }

  showAdminApp();
  await Promise.all([loadServicesForAdmin(), loadMastersForAdmin()]);
  await refreshApplications();
});

logoutBtn.addEventListener("click", () => {
  showLogin();
});

serviceForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage(serviceMessage);

  try {
    await api("/api/v1/admin/services", {
      method: "POST",
      body: JSON.stringify({
        name: document.getElementById("service-name").value.trim(),
        description: document.getElementById("service-description").value.trim() || null,
        price: Number(document.getElementById("service-price").value),
        photo_url: document.getElementById("service-photo").value.trim() || null,
      }),
    });
    showMessage(serviceMessage, "Услуга создана");
    serviceForm.reset();
    await loadServicesForAdmin();
  } catch (error) {
    showMessage(serviceMessage, error.message, true);
  }
});

masterForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage(masterMessage);

  try {
    const result = await api("/api/v1/admin/masters", {
      method: "POST",
      body: JSON.stringify({ name: document.getElementById("master-name").value.trim() }),
    });
    showMessage(masterMessage, `Мастер создан: ID ${result.data.id}`);
    masterForm.reset();
    await loadMastersForAdmin(document.getElementById("time-day").value || today);
    document.getElementById("time-master-id").value = String(result.data.id);
    document.getElementById("application-master-id").value = String(result.data.id);
  } catch (error) {
    showMessage(masterMessage, error.message, true);
  }
});

timeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage(masterMessage);

  try {
    await api(`/api/v1/admin/masters/${document.getElementById("time-master-id").value}/times`, {
      method: "POST",
      body: JSON.stringify({
        day: document.getElementById("time-day").value,
        time_slot: document.getElementById("time-slot").value,
      }),
    });
    showMessage(masterMessage, "Слот добавлен");
    timeForm.reset();
    document.getElementById("time-day").value = today;
    await loadMastersForAdmin(today);
  } catch (error) {
    showMessage(masterMessage, error.message, true);
  }
});

applicationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage(applicationMessage);

  try {
    const result = await api("/api/v1/admin/applications", {
      method: "POST",
      body: JSON.stringify({
        service_id: Number(document.getElementById("application-service-id").value),
        master_id: Number(document.getElementById("application-master-id").value),
        name: document.getElementById("application-name").value.trim(),
        telephone_number: document.getElementById("application-phone").value.trim(),
        appointment_date: document.getElementById("application-date").value,
        time_slot: document.getElementById("application-time").value,
        comment: document.getElementById("application-comment").value.trim() || null,
      }),
    });
    showMessage(applicationMessage, `Заявка создана: ID ${result.data.id}`);
    await refreshApplications();
  } catch (error) {
    showMessage(applicationMessage, error.message, true);
  }
});

refreshApplicationsBtn.addEventListener("click", () => refreshApplications().catch((error) => showMessage(applicationMessage, error.message, true)));

applicationsList.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-id][data-status]");
  if (!button) {
    return;
  }

  try {
    await api(`/api/v1/admin/applications/${button.dataset.id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status: button.dataset.status }),
    });
    await refreshApplications();
  } catch (error) {
    showMessage(applicationMessage, error.message, true);
  }
});

showLogin();
