# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the LabelU backend used by the Electron shell.
# Build: pyinstaller desktop/backend/labelu-server.spec --distpath desktop/backend/dist --workpath desktop/backend/build
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = []
# Frontend build + alembic migration scripts (alembic loads versions/*.py from disk).
datas += collect_data_files("labelu", include_py_files=True, excludes=["**/tests/**", "**/__pycache__/**"])

hiddenimports = []
hiddenimports += collect_submodules("labelu", filter=lambda name: ".tests" not in name)
hiddenimports += collect_submodules("uvicorn")
hiddenimports += collect_submodules("websockets")
hiddenimports += collect_submodules("alembic")
# Alembic migration scripts are loaded from disk at runtime, so PyInstaller can't
# see their imports; bundle everything they may reference.
hiddenimports += collect_submodules("sqlalchemy", filter=lambda name: ".testing" not in name)
hiddenimports += ["random", "json", "datetime"]
hiddenimports += ["email_validator", "multipart", "python_multipart", "aiofiles", "jose", "bcrypt"]

a = Analysis(
    ["server_entry.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "pytest", "MySQLdb"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="labelu-server",
    debug=False,
    strip=False,
    upx=False,
    # Console app so uvicorn has a real stdout; Electron spawns it with windowsHide.
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="labelu-server",
)
