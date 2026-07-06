// app/ui.js
let currentView = "identity"; // Track what is currently active

let identityState = { headers: [], rows: [] };
let providerState = { headers: [], rows: [] };

// Helper to get state references dynamically based on the active view
function getActiveState() {
  return currentView === "provider" ? providerState : identityState;
}

window.esc = function (str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
};

window.initApp = async function () {
  window.Navigation.renderSidebar();
  await window.switchView("identity");
};

// Routing Logic supporting both Identity and Provider views
window.switchView = async function (viewId) {
  const container = document.getElementById("content-container");
  const viewTitle = document.getElementById("view-title");
  if (!container) return;

  currentView = viewId; // Update global routing location

  if (viewId === "identity") {
    if (viewTitle) viewTitle.innerText = "Identity Management";

    if (identityState.headers.length === 0) {
      const data = await window.DataService.fetchSalesforceAssets();
      identityState.headers = data.headers;
      identityState.rows = data.rows;
    }
    renderTableView(container);
  } else if (viewId === "provider") {
    if (viewTitle) viewTitle.innerText = "Provider Management";

    if (providerState.headers.length === 0) {
      const data = await window.ProviderDataService.fetchProviders();
      providerState.headers = data.headers;
      providerState.rows = data.rows;
    }
    renderTableView(container);
  }
};

// Unified dynamic renderer
function renderTableView(container) {
  container.innerHTML = `
        <div class="flex flex-col flex-1 min-h-0 w-full">
            <div class="flex justify-start mb-4">
                <button type="button"
                        onclick="event.preventDefault(); window.addTableRow();"
                        class="px-4 py-2 text-sm font-medium rounded-lg text-white bg-appPrimary hover:opacity-90 transition-all shadow-sm">
                    + Add Row
                </button>
            </div>

            <div class="border border-appBorder bg-appCard rounded-xl overflow-hidden flex flex-col flex-1 shadow-sm transition-colors duration-200">
                <div class="overflow-x-auto flex-1">
                    <table class="w-full text-left border-collapse text-sm">
                        <thead class="sticky top-0 z-10 bg-appCard" id="fd-thead"></thead>
                        <tbody class="divide-y divide-appBorder text-appFg/90" id="fd-tbody"></tbody>
                    </table>
                </div>
            </div>

            <div class="pt-4 mt-4 border-t border-appBorder flex justify-end">
                <button type="button"
                        onclick="event.preventDefault(); window.exportCSV();"
                        class="px-5 py-2 text-sm font-medium rounded-lg text-white bg-appPrimary hover:opacity-90 transition-all shadow-sm">
                    Save
                </button>
            </div>
        </div>
    `;
  updateTableDOM();
}

function updateTableDOM() {
  const thead = document.getElementById("fd-thead");
  const tbody = document.getElementById("fd-tbody");
  if (!thead || !tbody) return;

  const state = getActiveState();

  // 1. Header: Use standard style definitions matching your theme variables
  thead.innerHTML = `
    <tr style="background-color: var(--app-hover, rgba(255,255,255,0.04)); color: var(--app-fg); font-weight: 500;">
        ${state.headers.map((h) => `<th class="px-4 py-3 text-left text-xs uppercase tracking-wider" style="border-b: 1px solid var(--app-border); font-weight: 500;">${esc(h)}</th>`).join("")}
        <th class="px-4 py-3 text-right text-xs uppercase tracking-wider w-16" style="border-b: 1px solid var(--app-border); font-weight: 500;">Actions</th>
    </tr>`;

  if (state.rows.length === 0) {
    tbody.innerHTML = `
        <tr>
            <td colspan="${state.headers.length + 1}" class="p-8 text-center" style="color: var(--app-fg); opacity: 0.5;">
                No data found. Click '+ Add Row' to start.
            </td>
        </tr>`;
    return;
  }

  // 2. Body Cells: Clean 1px lines using your theme's explicit border variable
  tbody.innerHTML = state.rows
    .map((row, rowIndex) => {
      return `<tr class="fd-data-row" id="fd-row-${rowIndex}">
            ${state.headers
              .map(
                (headerName, colIndex) => `
                <td class="px-3 py-2" style="border-b: 1px solid var(--app-border);">
                    <input type="text"
                           name="${headerName}_row_${rowIndex}"
                           value="${esc(row[colIndex] || "")}"
                           oninput="window.updateStateValue(${rowIndex}, ${colIndex}, this.value)"
                           style="width: 100%; background: transparent; border: 1px solid var(--app-border); color: var(--app-fg); border-radius: 6px; padding: 6px 10px; font-size: 14px; outline: none;">
                </td>`,
              )
              .join("")}
            <td class="px-3 py-2 text-right" style="border-b: 1px solid var(--app-border);">
                <button onclick="window.deleteTableRow(${rowIndex})" class="p-1" style="color: #ef4444; background: none; border: none; cursor: pointer; font-weight: 500;">✕</button>
            </td>
        </tr>`;
    })
    .join("");
}

// Live update targets whichever view is active
window.updateStateValue = function (row, col, value) {
  const state = getActiveState();
  if (state.rows[row]) {
    state.rows[row][col] = value;
  }
};

window.addTableRow = function () {
  const state = getActiveState();

  if (!state.headers || state.headers.length === 0) {
    state.headers =
      currentView === "provider"
        ? [
            "name",
            "function",
            "active",
            "domain",
            "api",
            "kms",
            "terms",
            "description",
          ]
        : ["original_name", "function", "active", "description"];
  }

  const newIndex = state.rows.length;
  state.rows.push(new Array(state.headers.length).fill(""));

  updateTableDOM();

  const newTr = document.getElementById(`fd-row-${newIndex}`);
  if (newTr) {
    newTr.style.backgroundColor = "var(--hover-bg)";
    newTr.classList.add("data-new-row");
  }
};

window.deleteTableRow = function (index) {
  const state = getActiveState();
  state.rows.splice(index, 1);
  updateTableDOM();
};

window.exportCSV = function () {
  const state = getActiveState();

  // Choose the appropriate data layer service to send payloads back to
  const service =
    currentView === "provider"
      ? window.ProviderDataService
      : window.DataService;
  const saveMethod =
    currentView === "provider" ? "saveProviders" : "saveSalesforceAssets";

  const csvContent = service.serializeCSV(state.headers, state.rows);

  const saveBtn = document.querySelector("button[onclick*='window.exportCSV']");
  const originalText = saveBtn ? saveBtn.innerText : "Save";
  if (saveBtn) {
    saveBtn.innerText = "Saving...";
    saveBtn.disabled = true;
  }

  service[saveMethod](csvContent).then((success) => {
    if (saveBtn) {
      saveBtn.innerText = originalText;
      saveBtn.disabled = false;
    }

    if (success) {
      document.querySelectorAll(".data-new-row").forEach((tr) => {
        tr.style.backgroundColor = "";
        tr.classList.remove("data-new-row");
      });
    }
  });
};
