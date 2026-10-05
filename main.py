"""
通用文件 → Markdown / JSON 转换器
桌面应用主程序
"""
import os
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# 拖拽支持
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    DND_FILES = None

from core.extractor import DocumentExtractor
from core.to_markdown import to_markdown
from core.to_json import to_json


# ============ 配色 ============
COLORS = {
    "bg": "#0f172a",
    "card": "#1e293b",
    "card_hover": "#243049",
    "border": "#334155",
    "text": "#f1f5f9",
    "text_muted": "#94a3b8",
    "md": "#10b981",          # 绿色 - Markdown
    "md_dark": "#059669",
    "json": "#f59e0b",        # 橙色 - JSON
    "json_dark": "#d97706",
    "primary": "#6366f1",
}


class ConverterApp:
    def __init__(self):
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()

        self.root.title("通用文件转换器 → MD / JSON")
        self.root.geometry("900x600")
        self.root.minsize(800, 550)
        self.root.configure(bg=COLORS["bg"])

        self._set_icon()
        self._build_ui()

    def _set_icon(self):
        """设置窗口图标（可选）"""
        try:
            if os.path.exists("assets/icon.ico"):
                self.root.iconbitmap("assets/icon.ico")
        except Exception:
            pass

    # ==================== UI 构建 ====================

    def _build_ui(self):
        # 顶部标题
        header = tk.Frame(self.root, bg=COLORS["bg"], height=80)
        header.pack(fill="x", padx=30, pady=(20, 0))

        title = tk.Label(
            header,
            text="🔄 通用文件转换器",
            font=("Microsoft YaHei UI", 20, "bold"),
            bg=COLORS["bg"], fg=COLORS["text"]
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="拖拽任意文件到左侧转换为 Markdown，或到右侧转换为 JSON",
            font=("Microsoft YaHei UI", 10),
            bg=COLORS["bg"], fg=COLORS["text_muted"]
        )
        subtitle.pack(anchor="w", pady=(4, 0))

        # 主区域：左右两个投放区
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=30, pady=20)
        main.columnconfigure(0, weight=1, uniform="col")
        main.columnconfigure(1, weight=1, uniform="col")
        main.rowconfigure(0, weight=1)

        # 左侧：Markdown
        self.md_drop = self._create_drop_zone(
            parent=main,
            title="Markdown",
            icon="📝",
            hint="拖拽文件到此处\n转换为 .md",
            color=COLORS["md"],
            color_dark=COLORS["md_dark"],
            on_drop=lambda files: self._handle_drop(files, "md"),
        )
        self.md_drop["frame"].grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # 右侧：JSON
        self.json_drop = self._create_drop_zone(
            parent=main,
            title="JSON",
            icon="{ }",
            hint="拖拽文件到此处\n转换为 .json",
            color=COLORS["json"],
            color_dark=COLORS["json_dark"],
            on_drop=lambda files: self._handle_drop(files, "json"),
        )
        self.json_drop["frame"].grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # 底部状态栏
        self.status_var = tk.StringVar(value=self._get_status_text())
        status = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Microsoft YaHei UI", 9),
            bg=COLORS["bg"], fg=COLORS["text_muted"],
            anchor="w"
        )
        status.pack(fill="x", padx=30, pady=(0, 15))

    def _create_drop_zone(self, parent, title, icon, hint,
                          color, color_dark, on_drop):
        """创建一个拖拽区域"""
        frame = tk.Frame(
            parent, bg=COLORS["card"],
            highlightthickness=2, highlightbackground=COLORS["border"],
            highlightcolor=color,
        )

        inner = tk.Frame(frame, bg=COLORS["card"])
        inner.pack(expand=True, fill="both", padx=20, pady=20)

        # 图标
        icon_lbl = tk.Label(
            inner, text=icon,
            font=("Microsoft YaHei UI", 48, "bold"),
            bg=COLORS["card"], fg=color
        )
        icon_lbl.pack(pady=(30, 10))

        # 标题
        title_lbl = tk.Label(
            inner, text=title,
            font=("Microsoft YaHei UI", 18, "bold"),
            bg=COLORS["card"], fg=COLORS["text"]
        )
        title_lbl.pack()

        # 提示
        hint_lbl = tk.Label(
            inner, text=hint,
            font=("Microsoft YaHei UI", 11),
            bg=COLORS["card"], fg=COLORS["text_muted"],
            justify="center"
        )
        hint_lbl.pack(pady=(10, 20))

        # 点击选择按钮
        btn = tk.Button(
            inner, text="点击选择文件",
            font=("Microsoft YaHei UI", 10, "bold"),
            bg=color, fg="white",
            activebackground=color_dark, activeforeground="white",
            relief="flat", bd=0, padx=20, pady=8,
            cursor="hand2",
            command=lambda: self._select_file(on_drop)
        )
        btn.pack()

        # 支持的格式说明
        formats_lbl = tk.Label(
            inner,
            text="支持: pdf · docx · txt · md · html · csv · json · rtf · xlsx 等",
            font=("Microsoft YaHei UI", 8),
            bg=COLORS["card"], fg=COLORS["text_muted"],
            wraplength=320, justify="center"
        )
        formats_lbl.pack(side="bottom", pady=(15, 0))

        # 绑定拖拽事件（仅当 tkinterdnd2 可用）
        if DND_AVAILABLE:
            for widget in [frame, inner, icon_lbl, title_lbl, hint_lbl, formats_lbl]:
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind(
                    "<<Drop>>",
                    lambda e, cb=on_drop: self._on_drop_event(e, cb, frame, color)
                )
                # 拖入高亮
                widget.dnd_bind(
                    "<<DragEnter>>",
                    lambda e, f=frame, c=color: f.configure(highlightbackground=c)
                )
                widget.dnd_bind(
                    "<<DragLeave>>",
                    lambda e, f=frame: f.configure(highlightbackground=COLORS["border"])
                )

        # hover 效果
        def on_enter(_):
            frame.configure(bg=COLORS["card_hover"])
            inner.configure(bg=COLORS["card_hover"])
            for w in [icon_lbl, title_lbl, hint_lbl, formats_lbl]:
                w.configure(bg=COLORS["card_hover"])

        def on_leave(_):
            frame.configure(bg=COLORS["card"])
            inner.configure(bg=COLORS["card"])
            for w in [icon_lbl, title_lbl, hint_lbl, formats_lbl]:
                w.configure(bg=COLORS["card"])

        for w in [frame, inner, icon_lbl, title_lbl, hint_lbl, formats_lbl]:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", lambda e: self._select_file(on_drop))

        return {
            "frame": frame,
            "inner": inner,
            "icon": icon_lbl,
            "title": title_lbl,
            "hint": hint_lbl,
            "color": color,
        }

    def _on_drop_event(self, event, on_drop, frame, color):
        """处理拖拽释放"""
        frame.configure(highlightbackground=COLORS["border"])
        files = self.root.tk.splitlist(event.data)
        on_drop(files)

    # ==================== 交互逻辑 ====================

    def _select_file(self, on_drop):
        """文件选择对话框"""
        filetypes = [
            ("所有支持的文件",
             "*.pdf *.docx *.doc *.txt *.md *.markdown *.rtf "
             "*.html *.htm *.csv *.json *.xlsx *.xls *.log"),
            ("PDF 文件", "*.pdf"),
            ("Word 文档", "*.docx *.doc"),
            ("文本文件", "*.txt *.md *.log"),
            ("HTML 文件", "*.html *.htm"),
            ("数据文件", "*.csv *.json *.xlsx *.xls"),
            ("RTF 文件", "*.rtf"),
            ("所有文件", "*.*"),
        ]
        paths = filedialog.askopenfilenames(
            title="选择要转换的文件",
            filetypes=filetypes
        )
        if paths:
            on_drop(list(paths))

    def _handle_drop(self, files, target: str):
        """处理拖入的文件，target = 'md' | 'json'"""
        files = [f for f in files if os.path.isfile(f)]
        if not files:
            return

        # 验证
        valid = []
        invalid = []
        for f in files:
            if DocumentExtractor.is_supported(f):
                valid.append(f)
            else:
                invalid.append(os.path.basename(f))

        if invalid and not valid:
            messagebox.showwarning(
                "不支持的格式",
                f"以下文件暂不支持:\n{chr(10).join(invalid)}"
            )
            return

        if invalid:
            messagebox.showinfo(
                "部分跳过",
                f"以下文件不支持，将跳过:\n{chr(10).join(invalid)}"
            )

        # 选择输出目录
        output_dir = filedialog.askdirectory(
            title="选择输出文件夹"
        )
        if not output_dir:
            return

        # 后台执行转换
        self._set_busy(True, f"正在转换 {len(valid)} 个文件...")
        threading.Thread(
            target=self._run_conversion,
            args=(valid, output_dir, target),
            daemon=True
        ).start()

    def _run_conversion(self, files, output_dir, target):
        """后台转换线程"""
        success = 0
        failed = []

        for fp in files:
            try:
                doc = DocumentExtractor.extract(fp)

                if target == "md":
                    content = to_markdown(doc)
                    ext = ".md"
                else:
                    content = to_json(doc)
                    ext = ".json"

                # 输出文件名
                base = Path(fp).stem
                out_path = Path(output_dir) / f"{base}{ext}"

                # 避免覆盖
                counter = 1
                while out_path.exists():
                    out_path = Path(output_dir) / f"{base}_{counter}{ext}"
                    counter += 1

                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(content)

                success += 1
            except Exception as e:
                failed.append((os.path.basename(fp), str(e)))

        # 回到主线程更新 UI
        self.root.after(0, lambda: self._on_conversion_done(
            success, failed, output_dir, target
        ))

    def _on_conversion_done(self, success, failed, output_dir, target):
        """转换完成回调"""
        self._set_busy(False)

        target_name = "Markdown" if target == "md" else "JSON"

        if failed and success == 0:
            msg = "所有文件转换失败:\n\n" + "\n".join(
                f"• {name}: {err}" for name, err in failed[:5]
            )
            messagebox.showerror("转换失败", msg)
            self.status_var.set("❌ 转换失败")
            return

        if failed:
            msg = (
                f"✅ 成功转换 {success} 个文件\n"
                f"❌ 失败 {len(failed)} 个\n\n"
                f"输出目录: {output_dir}\n\n"
                f"是否打开输出文件夹？"
            )
        else:
            msg = (
                f"✅ 成功转换 {success} 个文件为 {target_name}\n\n"
                f"输出目录: {output_dir}\n\n"
                f"是否打开输出文件夹？"
            )

        if messagebox.askyesno("转换完成", msg):
            self._open_folder(output_dir)

        self.status_var.set(
            f"✅ 已转换 {success} 个文件 → {target_name}  |  输出: {output_dir}"
        )

    def _open_folder(self, path):
        """打开系统文件夹"""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", path])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showwarning("无法打开", f"请手动打开:\n{path}")

    def _set_busy(self, busy: bool, text: str = ""):
        """设置忙碌状态"""
        if busy:
            self.status_var.set(f"⏳ {text}")
            self.root.config(cursor="watch")
        else:
            self.root.config(cursor="")

    def _get_status_text(self):
        if DND_AVAILABLE:
            return "💡 拖拽文件到左侧（Markdown）或右侧（JSON），或点击选择文件"
        else:
            return "⚠️ 未安装 tkinterdnd2，仅支持点击选择文件（pip install tkinterdnd2）"

    def run(self):
        self.root.mainloop()


def main():
    app = ConverterApp()
    app.run()


if __name__ == "__main__":
    main()