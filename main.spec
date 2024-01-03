# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('main.ui', '.'), ('iconTrading.ico', '.'), ('modules/test/TestChejan0.ui', './modules/test'), ('modules/test/TestChejan1.ui', './modules/test'), ('modules/test/TestCode.ui', './modules/test'), ('modules/setting/ModalInformation.ui', './modules/setting'), ('modules/setting/ModalSettings.ui', './modules/setting'), ('extends/QGroupBoxMyAccount.ui', './extends'), ('extends/QGroupBoxMyAccount.py', './extends'), ('extends/QTableWidgetItemExtend.py', './extends'), ('extends/QTableWidgetMyStocks.py', './extends'), ('resources/iconEraser.png', './resources'), ('resources/iconReload.png', './resources'), ('resources/iconTrading.png', './resources'), ('resources/iconWarning.png', './resources')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
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
    icon=['iconTrading.ico'],
)
