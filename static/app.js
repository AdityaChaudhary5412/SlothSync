document.addEventListener("DOMContentLoaded", () => {
  const engineName = document.getElementById("engineName");
  const btnScan = document.getElementById("btnScan");
  const btnSync = document.getElementById("btnSync");
  const btnRollback = document.getElementById("btnRollback");
  const sourceInput = document.getElementById("sourceInput");
  const backupInput = document.getElementById("backupInput");
  const filesTableBody = document.getElementById("filesTableBody");
  const fileCountBadge = document.getElementById("fileCountBadge");
  const statTimeSaved = document.getElementById("statTimeSaved");
  const statDuplicates = document.getElementById("statDuplicates");
  const statFiles = document.getElementById("statFiles");
  const aiSummaryCard = document.getElementById("aiSummaryCard");
  const aiSummaryText = document.getElementById("aiSummaryText");
  const aiModelTag = document.getElementById("aiModelTag");
  const logsContainer = document.getElementById("logsContainer");

  // Fetch initial system status
  fetch("/api/status")
    .then(r => r.json())
    .then(data => {
      engineName.textContent = data.ai_engine || "Offline Engine";
      if (data.use_gemma) {
        engineName.style.color = "#4ade80";
      }
    })
    .catch(() => {
      engineName.textContent = "Offline Heuristics";
    });

  // Fetch recent logs
  function refreshLogs() {
    fetch("/api/logs")
      .then(r => r.json())
      .then(data => {
        if (data.logs && data.logs.length > 0) {
          logsContainer.innerHTML = data.logs.map(log => `
            <div style="margin-bottom: 12px; border-bottom: 1px dashed #2e443b; padding-bottom: 8px;">
              <strong style="color: #f59e0b;">${log.name}</strong>
              <pre style="white-space: pre-wrap; margin-top: 4px; color: #a7f3d0;">${log.content}</pre>
            </div>
          `).join("");
        }
      });
  }
  refreshLogs();

  // Handle Scan (Dry run)
  btnScan.addEventListener("click", () => {
    btnScan.disabled = true;
    btnScan.textContent = "Analyzing Clutter...";

    fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: sourceInput.value, backup: backupInput.value })
    })
    .then(r => r.json())
    .then(data => {
      renderResults(data);
    })
    .catch(err => {
      alert("Error scanning folder: " + err);
    })
    .finally(() => {
      btnScan.disabled = false;
      btnScan.textContent = "🔍 Scan & Analyze (Dry Run)";
    });
  });

  // Handle Sync Execution
  btnSync.addEventListener("click", () => {
    btnSync.disabled = true;
    btnSync.textContent = "Sloth is organizing...";

    fetch("/api/sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: sourceInput.value, backup: backupInput.value, organize: true })
    })
    .then(r => r.json())
    .then(data => {
      if (data.status === "success") {
        alert("✨ SlothSync successfully organized and backed up files!\n\nManifest saved to: " + data.manifest);
        refreshLogs();
        btnScan.click();
      } else {
        alert("Sync error: " + JSON.stringify(data));
      }
    })
    .catch(err => {
      alert("Sync failed: " + err);
    })
    .finally(() => {
      btnSync.disabled = false;
      btnSync.textContent = "🦥 Sloth Sync & Organize";
    });
  });

  // Handle Rollback
  btnRollback.addEventListener("click", () => {
    if (!confirm("Are you sure you want to rollback the last sync session?")) return;
    btnRollback.disabled = true;

    fetch("/api/rollback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: sourceInput.value, backup: backupInput.value })
    })
    .then(r => r.json())
    .then(data => {
      alert(data.message || "Rollback completed.");
      refreshLogs();
      btnScan.click();
    })
    .catch(err => alert("Rollback failed: " + err))
    .finally(() => {
      btnRollback.disabled = false;
    });
  });

  function renderResults(data) {
    if (data.error) {
      alert(data.error);
      return;
    }

    statFiles.textContent = data.file_count;
    statDuplicates.textContent = data.duplicates_count;
    statTimeSaved.textContent = (data.lazy_payoff ? data.lazy_payoff.minutes_saved : 0) + " min";
    fileCountBadge.textContent = `${data.file_count} items`;

    if (data.summary) {
      aiSummaryCard.style.display = "block";
      aiSummaryText.textContent = data.summary;
      aiModelTag.textContent = data.ai_engine;
    }

    if (!data.files || data.files.length === 0) {
      filesTableBody.innerHTML = `<tr><td colspan="5" class="empty-row">No files found in source folder.</td></tr>`;
      return;
    }

    filesTableBody.innerHTML = data.files.map(f => {
      const dupBadge = f.is_duplicate 
        ? `<span class="badge" style="background:#ef4444; color:#fff;">Duplicate</span>`
        : `<span class="badge" style="background:#059669; color:#fff;">Unique</span>`;

      return `
        <tr>
          <td><strong>${f.name}</strong><br><small style="color:#8ea89d;">${(f.size / 1024).toFixed(1)} KB</small></td>
          <td><span class="badge">${f.category}</span></td>
          <td><code>${f.suggested_name}</code></td>
          <td>${(f.tags || []).map(t => `<span class="badge" style="margin-right:4px;">#${t}</span>`).join("")}</td>
          <td>${dupBadge}</td>
        </tr>
      `;
    }).join("");
  }
});
