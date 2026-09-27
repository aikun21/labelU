// Electron shell: starts the Python (LabelU) backend and shows its UI in a native window.
const { app, BrowserWindow, dialog, shell } = require('electron');
const { spawn } = require('child_process');
const fs = require('fs');
const http = require('http');
const net = require('net');
const path = require('path');

const HOST = '127.0.0.1';
const STARTUP_TIMEOUT_MS = 60_000;

let backend = null;
let mainWindow = null;
let quitting = false;

function getFreePort() {
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.unref();
    srv.on('error', reject);
    srv.listen(0, HOST, () => {
      const { port } = srv.address();
      srv.close(() => resolve(port));
    });
  });
}

function getDataDir() {
  // Dev: <repo>/data (same as running labelu directly). Packaged: %APPDATA%/<app>/data.
  if (!app.isPackaged) return path.resolve(__dirname, '..', 'data');
  return path.join(app.getPath('userData'), 'data');
}

function startBackend(port, dataDir) {
  let command;
  let args;
  let cwd;
  if (app.isPackaged) {
    const backendDir = path.join(process.resourcesPath, 'backend');
    command = path.join(backendDir, 'labelu-server.exe');
    args = [];
    cwd = dataDir;
  } else {
    const root = path.resolve(__dirname, '..');
    command = path.join(root, '.venv', 'Scripts', 'python.exe');
    args = ['-m', 'labelu.desktop'];
    cwd = root;
  }
  args.push('--host', HOST, '--port', String(port), '--data-dir', dataDir, '--parent-pid', String(process.pid));

  const logDir = path.join(dataDir, 'logs');
  fs.mkdirSync(logDir, { recursive: true });
  const log = fs.createWriteStream(path.join(logDir, 'backend.log'), { flags: 'w' });

  const child = spawn(command, args, {
    cwd,
    windowsHide: true,
    env: { ...process.env, PYTHONUNBUFFERED: '1', PYTHONIOENCODING: 'utf-8' },
  });
  child.stdout.pipe(log);
  child.stderr.pipe(log);
  child.on('exit', (code) => {
    backend = null;
    if (!quitting) {
      dialog.showErrorBox('后端服务已退出', `后端进程意外退出 (code ${code})。\n日志: ${path.join(logDir, 'backend.log')}`);
      app.quit();
    }
  });
  return child;
}

function waitForBackend(url, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  return new Promise((resolve, reject) => {
    const attempt = () => {
      const req = http.get(url, (res) => {
        res.resume();
        resolve();
      });
      req.on('error', () => {
        if (!backend) return reject(new Error('后端进程启动失败'));
        if (Date.now() > deadline) return reject(new Error('等待后端启动超时'));
        setTimeout(attempt, 300);
      });
      req.setTimeout(2000, () => req.destroy());
    };
    attempt();
  });
}

function stopBackend() {
  if (!backend) return;
  const pid = backend.pid;
  backend = null;
  // Kill the whole process tree (PyInstaller onedir exe / python may spawn children).
  if (process.platform === 'win32') {
    spawn('taskkill', ['/pid', String(pid), '/T', '/F'], { windowsHide: true });
  } else {
    try { process.kill(pid); } catch (_) { /* already gone */ }
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 640,
    title: 'Video Annotator',
    icon: path.join(__dirname, 'assets', 'icon.png'),
    autoHideMenuBar: true,
    show: false,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  mainWindow.once('ready-to-show', () => mainWindow.show());
  // Keep the app name in the title bar instead of the web page's <title>.
  mainWindow.on('page-title-updated', (e) => e.preventDefault());
  mainWindow.loadFile(path.join(__dirname, 'loading.html'));

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    const origin = new URL(mainWindow.webContents.getURL()).origin;
    if (url.startsWith(origin)) return { action: 'allow' };
    shell.openExternal(url);
    return { action: 'deny' };
  });
  mainWindow.on('closed', () => { mainWindow = null; });
}

async function boot() {
  createWindow();
  const dataDir = getDataDir();
  fs.mkdirSync(dataDir, { recursive: true });
  const port = await getFreePort();
  const baseUrl = `http://${HOST}:${port}`;
  backend = startBackend(port, dataDir);
  try {
    await waitForBackend(baseUrl, STARTUP_TIMEOUT_MS);
  } catch (err) {
    dialog.showErrorBox('启动失败', `${err.message}\n日志: ${path.join(dataDir, 'logs', 'backend.log')}`);
    app.quit();
    return;
  }
  if (mainWindow) mainWindow.loadURL(baseUrl);
}

if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.on('second-instance', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
  app.whenReady().then(boot);
  app.on('before-quit', () => { quitting = true; stopBackend(); });
  app.on('window-all-closed', () => app.quit());
}
