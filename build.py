"""
PyInstaller 打包脚本
运行: python build.py
"""
import os
import sys
import shutil
import subprocess


APP_NAME = "UniversalConverter"


def clean():
    for d in ["build", "dist", f"{APP_NAME}.spec"]:
        if os.path.exists(d):
            if os.path.isdir(d):
                shutil.rmtree(d)
            else:
                os.remove(d)


def build():
    print("🧹 清理旧文件...")
    clean()

    print("📦 开始打包（可能需要 1-3 分钟）...")

    sep = ";" if sys.platform == "win32" else ":"

    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",                # 不显示控制台
        "--name", APP_NAME,
        # 收集所有需要的依赖
        "--collect-all", "tkinterdnd2",
        "--collect-all", "pypdf",
        "--collect-all", "pdfplumber",
        "--collect-all", "docx",
        "--collect-all", "bs4",
        "--collect-all", "openpyxl",
        "--hidden-import", "reportlab",
        "--hidden-import", "striprtf",
        "--hidden-import", "markdownify",
        # 打包数据文件
        "--add-data", f"assets{sep}assets" if os.path.exists("assets") else ".",
        "main.py",
    ]

    subprocess.run(args, check=True)

    print("\n" + "=" * 50)
    print(f"✅ 打包完成！")
    print(f"📂 可执行文件位置: dist/{APP_NAME}.exe（Windows）")
    print(f"📂 或: dist/{APP_NAME}（macOS / Linux）")
    print("=" * 50)


if __name__ == "__main__":
    build()