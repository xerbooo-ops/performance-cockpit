# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

backend_dir = Path(SPECPATH)
frontend_dist = backend_dir.parent / "frontend" / "dist"

analysis = Analysis(
    ["src/performance_cockpit/standalone.py"],
    pathex=[str(backend_dir / "src")],
    binaries=[],
    datas=[
        (str(frontend_dist), "frontend"),
        (str(backend_dir / "migrations"), "migrations"),
    ],
    hiddenimports=["uvicorn.logging", "uvicorn.loops.auto", "uvicorn.protocols.http.auto"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["psycopg"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(analysis.pure)
exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="PerformanceCockpit",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
