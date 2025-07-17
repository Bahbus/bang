import os
import subprocess
import sys
from pathlib import Path


def test_bang_executable_exits(tmp_path):
    subprocess.run(["make", "build-exe"], check=True)
    exe = Path("dist/bang.exe" if sys.platform.startswith("win") else "dist/bang")
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["BANG_AUTO_CLOSE"] = "1"
    proc = subprocess.run([str(exe)], env=env, timeout=10)
    assert proc.returncode == 0
