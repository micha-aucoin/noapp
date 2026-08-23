#!/usr/bin/env python3

import subprocess
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

WATCH_DIRS = [
    BASE_DIR / "noapp",
    BASE_DIR / "templates",
    BASE_DIR / "static",
]

WATCH_SUFFIXES = {
    ".py",
    ".html",
    ".css",
}

MAIN_FILE = BASE_DIR / "main.py"
DEV_SERVER_FILE = BASE_DIR / "dev" / "server.py"

def get_mtimes():
    mtimes = {}
    mtimes[MAIN_FILE] = MAIN_FILE.stat().st_mtime
    for directory in WATCH_DIRS:
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in WATCH_SUFFIXES:
                continue
            mtimes[path] = path.stat().st_mtime
    return mtimes

if __name__ == "__main__":
    process = subprocess.Popen([str(DEV_SERVER_FILE)])
    mtimes = get_mtimes()
    try:
        while True:
            time.sleep(1)
            new_mtimes = get_mtimes()
            if new_mtimes != mtimes:
                process.terminate()
                process.wait()
                process = subprocess.Popen([str(DEV_SERVER_FILE)])
                mtimes = new_mtimes
    finally:
        process.terminate()
        process.wait()
