# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules
from glob import glob

asset_patterns = (
    'bang_py/assets/*.png',
    'bang_py/assets/*.svg',
    'bang_py/assets/icons/*.svg',
    'bang_py/assets/characters/*.webp',
    'bang_py/assets/audio/*.wav',
    'bang_py/assets/*.md',
)

asset_paths = [
    (path, 'bang_py/assets')
    for pattern in asset_patterns
    for path in glob(pattern)
]

a = Analysis(
    ['pyinstaller_entry.py'],
    pathex=[],
    binaries=collect_dynamic_libs('PySide6'),
    datas=asset_paths,
    hiddenimports=collect_submodules('PySide6') + collect_submodules('websockets'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='bang',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
