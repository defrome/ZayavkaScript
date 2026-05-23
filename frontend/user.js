const serviceSelect = document.getElementById("service-select");
const servicesList = document.getElementById("services-list");
const mastersList = document.getElementById("masters-list");
const servicesStatus = document.getElementById("services-status");
const messageBox = document.getElementById("user-message");
const form = document.getElementById("application-form");
const dateInput = document.getElementById("appointment-date");
const reloadMastersBtn = document.getElementById("reload-masters");
const masterSelect = document.getElementById("master-select");

const today = new Date().toISOString().slice(0, 10);
dateInput.value = today;

function showMessage(text, isError = false) {
  messageBox.textContent = text;
  messageBox.classList.toggle("error", isError);
  messageBox.classList.add("show");
}

function clearMessage() {
  messageBox.textContent = "";
  messageBox.className = "message";
}

function serviceLabel(service) {
  return `${service.name} · ${service.price} ₽`;
}

async function loadServices() {
  servicesStatus.textContent = "загрузка услуг";
  const response = await fetch("/api/v1/public/services");
  const payload = await response.json();
  const services = payload.data || [];

  serviceSelect.innerHTML = services.map((service) => `<option value="${service.id}">${serviceLabel(service)}</option>`).join("");
  servicesList.innerHTML = services
    .map(
      (service) => `
        <article class="card">
          <strong>${service.name}</strong>
          <div class="muted small">${service.description || "Описание не указано"}</div>
          <div style="margin-top: 8px" class="pill">${service.price} ₽</div>
        </article>
      `,
    )
    .join("");

  servicesStatus.textContent = services.length ? "услуги загружены" : "услуг нет";
}

async function loadMasters() {
  const day = dateInput.value;
  mastersList.innerHTML = '<div class="muted">Загрузка...</div>';
  const response = await fetch(`/api/v1/public/masters?day=${encodeURIComponent(day)}`);
  const payload = await response.json();
  const masters = payload.data || [];

  mastersList.innerHTML = masters.length
    ? masters
        .map(
          (master) => `
            <article class="card">
              <strong>${master.name}</strong>
              <div class="muted small">Свободные слоты на ${day}</div>
              <div class="small" style="margin-top: 8px">
                ${master.times.length ? master.times.map((slot) => slot.time_slot).join(", ") : "Нет свободных слотов"}
              </div>
            </article>
          `,
        )
        .join("")
    : '<div class="muted">Нет доступных мастеров на выбранную дату.</div>';

  const masterOptions = ['<option value="">Любой мастер</option>'];
  masters.forEach((master) => {
    masterOptions.push(`<option value="${master.id}">${master.name}</option>`);
  });
  masterSelect.innerHTML = masterOptions.join("");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearMessage();

  const payload = {
    service_id: Number(serviceSelect.value),
    master_id: masterSelect.value ? Number(masterSelect.value) : null,
    name: document.getElementById("name").value.trim(),
    telephone_number: document.getElementById("phone").value.trim(),
    appointment_date: dateInput.value,
    time_slot: document.getElementById("time-slot").value,
    comment: document.getElementById("comment").value.trim() || null,
  };

  const response = await fetch("/api/v1/public/applications", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const result = await response.json();

  if (!response.ok) {
    showMessage(result.detail || "Ошибка отправки заявки", true);
    return;
  }

  showMessage(`Заявка отправлена. ID: ${result.data.id}`);
  form.reset();
  dateInput.value = today;
  await loadMasters();
});

dateInput.addEventListener("change", loadMasters);
reloadMastersBtn.addEventListener("click", loadMasters);

loadServices()
  .then(loadMasters)
  .catch(() => showMessage("Не удалось загрузить данные", true));
