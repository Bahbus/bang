import os
import subprocess
import sys
from pathlib import Path
import shutil

import pytest


@pytest.mark.skipif(shutil.which("pyinstaller") is None,
                    reason="pyinstaller not installed")
def test_bang_executable_exits(tmp_path):
    try:
        subprocess.run(["make", "build-exe"], check=True)
        exe = Path(
            "dist/bang.exe" if sys.platform.startswith("win") else "dist/bang"
        )
        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"
        env["BANG_AUTO_CLOSE"] = "1"
        proc = subprocess.run([str(exe)], env=env, timeout=10)
        assert proc.returncode == 0
    finally:
        shutil.rmtree("build", ignore_errors=True)
        shutil.rmtree("dist", ignore_errors=True)
