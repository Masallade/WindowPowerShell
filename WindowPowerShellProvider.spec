# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs

# Collect all cv2 dependencies
datas = []
binaries = []
hiddenimports = ['cv2', 'numpy', 'PIL', '_cv2']

# Collect cv2 data files and binaries - this should capture all DLLs
cv2_data, cv2_binaries, cv2_hidden = collect_all('cv2')
datas += cv2_data
binaries += cv2_binaries
hiddenimports += cv2_hidden

# Also explicitly collect dynamic libraries from cv2 package
try:
    cv2_dynamic = collect_dynamic_libs('cv2')
    binaries += cv2_dynamic
except:
    pass  # If this fails, continue with what we have

# Collect numpy dependencies (cv2 depends on numpy)
numpy_data, numpy_binaries, numpy_hidden = collect_all('numpy')
datas += numpy_data
binaries += numpy_binaries
hiddenimports += numpy_hidden

a = Analysis(
    ['WindowPowerShellProvider.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='WindowPowerShellProvider',
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
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WindowPowerShellProvider',
)
