from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SUBFOLDER = PROJECT_ROOT / "Trần_Kiên_G12_T179_1598"
if str(SUBFOLDER) not in sys.path:
    sys.path.insert(0, str(SUBFOLDER))

if (SUBFOLDER / "main.py").exists():
    os.chdir(SUBFOLDER)
    runpy.run_path(str(SUBFOLDER / "main.py"), run_name="__main__")
else:
    raise FileNotFoundError("Không tìm thấy entrypoint trong thư mục con")
