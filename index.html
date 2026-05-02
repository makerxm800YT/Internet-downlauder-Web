const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs-extra');
const ytdlp = require('yt-dlp-exec');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 860,
    height: 740,
    minWidth: 780,
    minHeight: 620,
    backgroundColor: '#0f0f0f',
    icon: path.join(__dirname, 'assets/icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.loadFile('index.html');
  // mainWindow.webContents.openDevTools(); // remove in production
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

// Handle download request from renderer
ipcMain.handle('start-download', async (event, data) => {
  const { url, mode, quality, format, savePath } = data;

  try {
    const options = {
      output: path.join(savePath, '%(title)s.%(ext)s'),
      quiet: false,
    };

    if (mode.includes('Audio')) {
      options.format = 'bestaudio/best';
      options.extractAudio = true;
      options.audioFormat = format === 'mp3' ? 'mp3' : 'm4a';
      options.audioQuality = 0; // best
    } else {
      const qMap = {
        'Best Quality': 'bestvideo+bestaudio/best',
        '1080p': 'bestvideo[height<=1080]+bestaudio/best',
        '720p': 'bestvideo[height<=720]+bestaudio/best',
        '480p': 'bestvideo[height<=480]+bestaudio/best',
      };
      options.format = qMap[quality] || 'bestvideo+bestaudio/best';
      options.mergeOutputFormat = format || 'mp4';
    }

    if (mode.includes('Playlist')) {
      options.noPlaylist = false;
    } else {
      options.noPlaylist = true;
    }

    mainWindow.webContents.send('status-update', 'Starting download...');

    await ytdlp(url, options);

    return { success: true, message: 'Download completed!' };
  } catch (error) {
    console.error(error);
    return { success: false, message: error.message || 'Download failed' };
  }
});

ipcMain.handle('choose-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  return result.canceled ? null : result.filePaths[0];
});
