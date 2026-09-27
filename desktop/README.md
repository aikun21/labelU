# Video Annotator 桌面版

基于 LabelU 的桌面视频标注工具：Electron 提供原生窗口，内嵌 LabelU 前端；Python 后端（FastAPI + SQLite）由 Electron 作为子进程启动/关闭。

```
VideoAnnotator.exe (Electron)
 ├─ 选一个空闲端口，启动 resources/backend/labelu-server.exe（PyInstaller 打包的 labelu/desktop.py）
 ├─ 等后端就绪后在窗口中加载 http://127.0.0.1:<port>
 └─ 退出时结束后端进程（后端也会监视 Electron 进程，Electron 崩溃时自行退出）
```

## 数据位置

| 模式 | SQLite 数据库 / 媒体文件 |
| --- | --- |
| 开发 (`npm start`) | `<仓库>/data/` |
| 打包后 | `%APPDATA%\VideoAnnotator\data\` |

后端日志：`<数据目录>/logs/backend.log`。

## 开发运行

```powershell
# 仓库根目录，首次需要
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
powershell -File scripts\fetch_frontend.ps1

cd desktop
npm install
npm start          # 使用 .venv 中的 Python 源码运行后端
```

## 打包 exe

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_desktop.ps1
```

产物位于 `desktop/release/`：

- `VideoAnnotator-Setup-<ver>.exe`：安装包（推荐分发）
- `VideoAnnotator-<ver>-win-x64.zip`：免安装版，解压后运行 `VideoAnnotator.exe`
- `win-unpacked/VideoAnnotator.exe`：可直接运行的目录

未使用 electron-builder 的 `portable` 单文件目标：它每次启动都要把约 2000 个后端文件解压到临时目录，启动需要约 2 分钟。

## 其它

- 图标：`build/make_icon.py` 生成 `build/icon.{png,ico}` 与 `assets/icon.png`。
- PyInstaller 配置：`backend/labelu-server.spec`。alembic 迁移脚本运行时从磁盘加载，它们引用的模块需在 `hiddenimports` 中声明。
