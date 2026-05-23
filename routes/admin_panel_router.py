from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["admin-panel"])


@router.get("/admin", response_class=HTMLResponse)
def admin_panel() -> str:
    return """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Панель администратора заявок</title>
  <style>
    :root {
      --bg: #f4f7fb;
      --card: #ffffff;
      --ink: #1f2937;
      --accent: #0f766e;
      --muted: #6b7280;
      --line: #e5e7eb;
    }
    body { margin: 0; font-family: "Segoe UI", sans-serif; background: linear-gradient(135deg, #eef2ff, var(--bg)); color: var(--ink); }
    .wrap { max-width: 1100px; margin: 24px auto; padding: 0 16px; }
    h1 { margin-bottom: 10px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .card { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,.04); }
    label { display: block; margin: 10px 0 4px; font-size: 14px; color: var(--muted); }
    input, select, button, textarea { width: 100%; padding: 10px; border-radius: 8px; border: 1px solid var(--line); box-sizing: border-box; }
    button { background: var(--accent); color: #fff; border: 0; cursor: pointer; margin-top: 12px; }
    button:hover { opacity: .9; }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; }
    th, td { border-bottom: 1px solid var(--line); text-align: left; padding: 8px; font-size: 14px; }
    .full { grid-column: 1 / -1; }
    .hint { font-size: 13px; color: var(--muted); }
    @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
<div class="wrap">
  <h1>Админ-панель заявок</h1>
  <p class="hint">Укажите токен администратора и управляйте актуальными заявками.</p>

  <div class="card">
    <label>Admin token</label>
    <input id="token" placeholder="dev-admin-token" />
  </div>

  <div class="grid">
    <div class="card">
      <h3>Создать заявку клиента</h3>
      <label>Service ID</label><input id="service_id" type="number" />
      <label>Master ID</label><input id="master_id" type="number" />
      <label>Имя клиента</label><input id="name" />
      <label>Телефон</label><input id="phone" />
      <label>Дата</label><input id="day" type="date" />
      <label>Время (HH:MM)</label><input id="time_slot" placeholder="14:30" />
      <label>Комментарий</label><textarea id="comment"></textarea>
      <button onclick="createApplication()">Создать</button>
      <p id="create_result" class="hint"></p>
    </div>

    <div class="card">
      <h3>Обновить статус заявки</h3>
      <label>Application ID</label><input id="application_id" type="number" />
      <label>Новый статус</label>
      <select id="new_status">
        <option value="new">new</option>
        <option value="in_progress">in_progress</option>
        <option value="completed">completed</option>
        <option value="canceled">canceled</option>
      </select>
      <button onclick="updateStatus()">Обновить статус</button>
      <p id="status_result" class="hint"></p>
    </div>

    <div class="card full">
      <h3>Актуальные заявки</h3>
      <button onclick="loadActual()">Обновить список</button>
      <table>
        <thead>
          <tr>
            <th>ID</th><th>Клиент</th><th>Телефон</th><th>Услуга</th><th>Мастер</th><th>Дата</th><th>Время</th><th>Статус</th>
          </tr>
        </thead>
        <tbody id="actual_table"></tbody>
      </table>
    </div>
  </div>
</div>

<script>
function headers() {
  return {
    "Content-Type": "application/json",
    "x-admin-token": document.getElementById("token").value || ""
  };
}

async function createApplication() {
  const payload = {
    service_id: Number(document.getElementById("service_id").value),
    master_id: Number(document.getElementById("master_id").value),
    name: document.getElementById("name").value,
    telephone_number: document.getElementById("phone").value,
    appointment_date: document.getElementById("day").value,
    time_slot: document.getElementById("time_slot").value,
    comment: document.getElementById("comment").value || null,
  };

  const res = await fetch("/api/v1/admin/applications", {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(payload),
  });

  const data = await res.json();
  document.getElementById("create_result").textContent = res.ok
    ? `Создано: ID ${data.data.id}`
    : `Ошибка: ${data.detail || "не удалось создать"}`;
  if (res.ok) loadActual();
}

async function updateStatus() {
  const appId = Number(document.getElementById("application_id").value);
  const payload = { status: document.getElementById("new_status").value };

  const res = await fetch(`/api/v1/admin/applications/${appId}/status`, {
    method: "PATCH",
    headers: headers(),
    body: JSON.stringify(payload),
  });

  const data = await res.json();
  document.getElementById("status_result").textContent = res.ok
    ? `Обновлено: ${data.data.status}`
    : `Ошибка: ${data.detail || "не удалось обновить"}`;
  if (res.ok) loadActual();
}

async function loadActual() {
  const res = await fetch("/api/v1/admin/applications/actual", { headers: headers() });
  const data = await res.json();
  const table = document.getElementById("actual_table");
  table.innerHTML = "";

  if (!res.ok) {
    table.innerHTML = `<tr><td colspan="8">Ошибка: ${data.detail || "доступ запрещен"}</td></tr>`;
    return;
  }

  for (const app of data.data) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${app.id}</td>
      <td>${app.customer_name}</td>
      <td>${app.customer_phone}</td>
      <td>${app.service_name}</td>
      <td>${app.master_name || "-"}</td>
      <td>${app.appointment_date}</td>
      <td>${app.time_slot}</td>
      <td>${app.status}</td>
    `;
    table.appendChild(row);
  }
}

loadActual();
</script>
</body>
</html>
    """
