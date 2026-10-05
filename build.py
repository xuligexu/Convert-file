import os
import sys
import shutil
import subprocess

# 强制 UTF-8，兼容 Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


APP_NAME = "UniversalConverter"


def clean():
    for d in ["build", "dist", f"{APP_NAME}.spec"]:
        if os.path.exists(d):
            if os.path.isdir(d):
                shutil.rmtree(d)
            else:
                os.remove(d)


def build():
    print("[*] Cleaning old files...")
    clean()

    print("[*] Building (this may take 1-3 minutes)...")

    sep = ";" if sys.platform == "win32" else ":"

    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", APP_NAME,
        "--collect-all", "tkinterdnd2",
        "--collect-all", "pypdf",
        "--collect-all", "pdfplumber",
        "--collect-all", "docx",
        "--collect-all", "bs4",
        "--collect-all", "openpyxl",
        "--hidden-import", "reportlab",
        "--hidden-import", "striprtf",
        "--hidden-import", "markdownify",
        "--add-data", f"assets{sep}assets" if os.path.exists("assets") else ".",
        "main.py",
    ]

    subprocess.run(args, check=True)

    print("\n" + "=" * 50)
    print("[OK] Build complete!")
    print(f"Executable: dist/{APP_NAME}.exe (Windows)")
    print(f"Or:         dist/{APP_NAME}    (macOS / Linux)")
    print("=" * 50)


if __name__ == "__main__":
    build()