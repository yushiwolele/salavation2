# -*- mode:python  ;  coding:utf-8 -*-

import os

# 从环境变量中获取自定义参数
project = os.environ.get('PROJECT_PATH', 'None')
print(project)
self_config = os.environ.get('SELF_CONFIG_PATH', 'None')

block_cipher = None

PROJECT_PATH = project #基线包路径
SELF_CONFIG_PATH = self_config
PYTHON_SITEPACK_PATH = 'F:\\Salvation\\venv\\Lib\\site-packages\\' #python路径。因为只有此功能使用，如放在配置文件需读取+设置环境变量，故不放在公共配置文件中


a = Analysis(['RunEnvFree.py'],
             pathex=[],
             binaries=[],
             datas=[
             (PROJECT_PATH+'Programs','AutoTest\\Programs'),
             (PROJECT_PATH+'Files','AutoTest\\Files'),
             (PROJECT_PATH+'Logs','AutoTest\\Logs'),
             (PROJECT_PATH+'Conf','AutoTest\\Conf'),
             (PROJECT_PATH+'Path','AutoTest\\Path'),
             (PYTHON_SITEPACK_PATH+'autoit\\lib','autoit\\lib'),
             (PYTHON_SITEPACK_PATH+'robot\\htmldata','robot\\htmldata'),
             (SELF_CONFIG_PATH+'readme.txt','.'),
             (SELF_CONFIG_PATH+'self_config.txt','.')
             ],
             hiddenimports=['robot.libraries.BuiltIn',
                            'robot.libraries.Reserved',
                            'robot.libraries.Easter',
                            'robot.libraries.String',
                            'Selenium2Library',
                            'CustomLibrary',
                            'robot.libraries.OperatingSystem',
                            'robot.libraries.Dialogs',
                            'robot.libraries.Collections',
                            'robot.libraries.Screenshot',
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='RunEnvFree',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='RunEnvFree')