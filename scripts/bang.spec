# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for building ``bang`` in a directory layout."""

from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules
from glob import glob

asset_patterns = (
    '../bang_py/assets/*.png',
    '../bang_py/assets/*.svg',
    '../bang_py/assets/icons/*.svg',
    '../bang_py/assets/characters/*.webp',
    '../bang_py/assets/audio/*.mp3',
    '../bang_py/assets/audio/*.wav',
    '../bang_py/assets/*.md',
)

asset_paths = [
    (path, 'bang_py/assets')
    for pattern in asset_patterns
    for path in glob(pattern)
]

qml_patterns = ('../bang_py/ui/qml/*.qml',)
qml_paths = [
    (path, 'bang_py/ui/qml')
    for pattern in qml_patterns
    for path in glob(pattern)
]

a = Analysis(
    ['../pyinstaller_entry.py'],
    pathex=[],
    binaries=collect_dynamic_libs('PySide6'),
    datas=asset_paths + qml_paths,
    hiddenimports=
        collect_submodules('PySide6')
        + collect_submodules('websockets')
        + ['bang_py.card_handlers.dispatch', 'bang_py.card_handlers.bang_handlers'],
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
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='bang',
)
