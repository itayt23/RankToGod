import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the path of the directory containing this script
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__name__)))

# Specify the options for PyInstaller
a = Analysis(['RankToGod.py'],
             pathex=[str(SCRIPT_DIR)],
             binaries=[],
             datas=[('.env', '.')],  # Include the .env file in the distribution
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None,
             noarchive=False)

# Define the output directory and name of the executable
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='EncRankToGodV6',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          windowed=True)