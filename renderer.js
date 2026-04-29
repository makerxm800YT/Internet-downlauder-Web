let savePath = '';

async function chooseFolder() {
  const path = await window.electronAPI.chooseFolder();
  if (path) {
    savePath = path;
    document.getElementById('savePath').textContent = path;
  }
}

async function startDownload() {
  const url = document.getElementById('url').value.trim();
  if (!url) {
    alert("Please paste a URL");
    return;
  }

  const mode = document.getElementById('mode').value;
  const quality = document.getElementById('quality').value;
  const format = document.getElementById('format').value;

  const data = { url, mode, quality, format, savePath };

  const result = await window.electronAPI.startDownload(data);
  addLog(result.message, result.success ? 'success' : 'error');
}

function addLog(msg, type = 'info') {
  const logEl = document.getElementById('log');
  const color = type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#aaa';
  logEl.innerHTML += `<span style="color:${color}">${msg}</span><br>`;
  logEl.scrollTop = logEl.scrollHeight;
}

// Optional: listen for status updates from main process
window.electronAPI.onStatusUpdate((event, msg) => {
  document.getElementById('status').textContent = msg;
});
