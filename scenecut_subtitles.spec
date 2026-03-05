# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec — Scene Cut Subtitles
# Génère un .app (macOS) ou .exe (Windows) autonome, sans terminal.
#
# Build macOS : pyinstaller scenecut_subtitles.spec --clean
# Build Windows : pyinstaller scenecut_subtitles.spec --clean  (sur Windows)

import sys

APP_NAME    = "Scene Cut Subtitles"
SCRIPT      = "scenecut_subtitles.py"
BUNDLE_ID   = "com.jondi-film.scenecut-subtitles"

block_cipher = None

a = Analysis(
    [SCRIPT],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        "aiohttp",
        "websockets",
        "websockets.legacy",
        "websockets.legacy.server",
        "tkinter",
        "asyncio",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["numpy", "pandas", "matplotlib", "PIL", "scipy"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # Pas de terminal — fenêtre graphique uniquement
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS uniquement : créer un .app bundle
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name=f"{APP_NAME}.app",
        bundle_identifier=BUNDLE_ID,
        info_plist={
            "CFBundleName":              APP_NAME,
            "CFBundleDisplayName":       APP_NAME,
            "CFBundleVersion":           "1.0.0",
            "CFBundleShortVersionString": "1.0",
            "NSHighResolutionCapable":   True,
            "LSUIElement":               False,   # Apparaît dans le Dock
            "NSHumanReadableCopyright":  "Jondi Film",
        },
    )
