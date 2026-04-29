const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  startDownload: (data) => ipcRenderer.invoke('start-download', data),
  chooseFolder: () => ipcRenderer.invoke('choose-folder'),
  onStatusUpdate: (callback) => ipcRenderer.on('status-update', callback)
});
