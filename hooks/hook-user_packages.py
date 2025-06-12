# PyInstaller hook to include necessary modules
from PyInstaller.utils.hooks import collect_all

# Ensure all specified packages are included

# Include PyQt5 and all its dependencies
try:
    datas, binaries, hiddenimports = collect_all("PyQt5")
    __all__ = ["datas", "binaries", "hiddenimports"]
except Exception:
    pass
