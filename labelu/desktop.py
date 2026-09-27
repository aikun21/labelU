"""Backend entry point used by the Electron desktop shell (and the PyInstaller build).

Electron picks a free port and a data directory, starts this process, waits for
the HTTP server to answer and then loads the UI from it.
"""
import argparse
import os
import secrets
import sys
import threading


def _watch_parent(pid: int) -> None:
    """Exit when the Electron process goes away so the backend is never orphaned."""
    if sys.platform == "win32":
        import ctypes

        SYNCHRONIZE = 0x00100000
        INFINITE = 0xFFFFFFFF
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
        if not handle:
            os._exit(0)
        kernel32.WaitForSingleObject(handle, INFINITE)
        os._exit(0)
    else:
        import time

        while True:
            try:
                os.kill(pid, 0)
            except OSError:
                os._exit(0)
            time.sleep(2)


def _load_secret_key(data_dir: str) -> str:
    """Keep the JWT key stable across restarts so users stay logged in."""
    key_file = os.path.join(data_dir, "secret.key")
    if os.path.exists(key_file):
        with open(key_file, "r", encoding="utf-8") as f:
            key = f.read().strip()
        if key:
            return key
    key = secrets.token_hex(32)
    with open(key_file, "w", encoding="utf-8") as f:
        f.write(key)
    return key


def main() -> None:
    parser = argparse.ArgumentParser(description="LabelU desktop backend")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--parent-pid", type=int, default=None)
    args = parser.parse_args()

    # Windowless PyInstaller builds have no stdout/stderr; loguru needs a sink.
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

    # Must be set before labelu is imported: settings are computed at import time.
    if args.data_dir:
        data_dir = os.path.abspath(args.data_dir)
        os.makedirs(data_dir, exist_ok=True)
        os.environ["LABELU_DATA_DIR"] = data_dir
        os.environ.setdefault("PASSWORD_SECRET_KEY", _load_secret_key(data_dir))

    if args.parent_pid:
        threading.Thread(target=_watch_parent, args=(args.parent_pid,), daemon=True).start()

    import uvicorn

    from labelu.main import app
    from labelu.internal.common.config import settings

    settings.HOST = args.host
    settings.PORT = str(args.port)
    settings.MEDIA_HOST = f"http://{args.host}:{args.port}"

    uvicorn.run(app=app, host=args.host, port=args.port, ws="websockets", log_config=None)


if __name__ == "__main__":
    main()
