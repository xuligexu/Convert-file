"""
图形界面
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from converter import PDFTXTConverter


class ConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF ↔ TXT 转换工具")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        self.converter = PDFTXTConverter()
        self._build_ui()

    def _build_ui(self):
        # 标题
        title = ttk.Label(
            self.root,
            text="PDF ↔ TXT 文件转换工具",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=15)

        # Notebook 选项卡
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Tab 1: PDF → TXT
        pdf_frame = ttk.Frame(notebook)
        notebook.add(pdf_frame, text="PDF → TXT")
        self._build_pdf_to_txt(pdf_frame)

        # Tab 2: TXT → PDF
        txt_frame = ttk.Frame(notebook)
        notebook.add(txt_frame, text="TXT → PDF")
        self._build_txt_to_pdf(txt_frame)

        # 状态栏
        self.status = ttk.Label(self.root, text="就绪", relief="sunken", anchor="w")
        self.status.pack(fill="x", side="bottom")

    def _build_pdf_to_txt(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill="both", expand=True)

        # 输入文件
        ttk.Label(frame, text="PDF 文件:").grid(row=0, column=0, sticky="w", pady=5)
        self.pdf_input = tk.StringVar()
        ttk.Entry(frame, textvariable=self.pdf_input, width=50).grid(
            row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="浏览...",
                   command=lambda: self._browse(self.pdf_input, [("PDF", "*.pdf")])
                   ).grid(row=0, column=2, pady=5)

        # 输出文件
        ttk.Label(frame, text="输出 TXT:").grid(row=1, column=0, sticky="w", pady=5)
        self.txt_output = tk.StringVar()
        ttk.Entry(frame, textvariable=self.txt_output, width=50).grid(
            row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="浏览...",
                   command=lambda: self._save_as(self.txt_output, [("TXT", "*.txt")])
                   ).grid(row=1, column=2, pady=5)

        # 转换按钮
        ttk.Button(frame, text="开始转换",
                   command=self._convert_pdf2txt
                   ).grid(row=2, column=1, pady=20)

    def _build_txt_to_pdf(self, parent):
        frame = ttk.Frame(parent, padding=20)
        frame.pack(fill="both", expand=True)

        # 输入文件
        ttk.Label(frame, text="TXT 文件:").grid(row=0, column=0, sticky="w", pady=5)
        self.txt_input = tk.StringVar()
        ttk.Entry(frame, textvariable=self.txt_input, width=50).grid(
            row=0, column=1, padx=5, pady=5)
        ttk.Button(frame, text="浏览...",
                   command=lambda: self._browse(self.txt_input, [("TXT", "*.txt")])
                   ).grid(row=0, column=2, pady=5)

        # 输出文件
        ttk.Label(frame, text="输出 PDF:").grid(row=1, column=0, sticky="w", pady=5)
        self.pdf_output = tk.StringVar()
        ttk.Entry(frame, textvariable=self.pdf_output, width=50).grid(
            row=1, column=1, padx=5, pady=5)
        ttk.Button(frame, text="浏览...",
                   command=lambda: self._save_as(self.pdf_output, [("PDF", "*.pdf")])
                   ).grid(row=1, column=2, pady=5)

        # 字号设置
        ttk.Label(frame, text="字号:").grid(row=2, column=0, sticky="w", pady=5)
        self.font_size = tk.IntVar(value=12)
        ttk.Spinbox(frame, from_=8, to=30, textvariable=self.font_size,
                    width=10).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # 转换按钮
        ttk.Button(frame, text="开始转换",
                   command=self._convert_txt2pdf
                   ).grid(row=3, column=1, pady=20)

    def _browse(self, var, filetypes):
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            var.set(filename)

    def _save_as(self, var, filetypes):
        filename = filedialog.asksaveasfilename(
            defaultextension=filetypes[0][1].replace("*", ""),
            filetypes=filetypes
        )
        if filename:
            var.set(filename)

    def _convert_pdf2txt(self):
        if not self.pdf_input.get() or not self.txt_output.get():
            messagebox.showwarning("提示", "请选择输入和输出文件")
            return

        self.status.config(text="转换中...")

        def run():
            success = self.converter.pdf_to_txt(
                self.pdf_input.get(), self.txt_output.get())
            if success:
                self.status.config(text="✅ 转换成功")
                messagebox.showinfo("成功", "PDF 转 TXT 完成！")
            else:
                self.status.config(text="❌ 转换失败")
                messagebox.showerror("错误", "转换失败，请检查文件")

        threading.Thread(target=run, daemon=True).start()

    def _convert_txt2pdf(self):
        if not self.txt_input.get() or not self.pdf_output.get():
            messagebox.showwarning("提示", "请选择输入和输出文件")
            return

        self.status.config(text="转换中...")

        def run():
            success = self.converter.txt_to_pdf(
                self.txt_input.get(),
                self.pdf_output.get(),
                font_size=self.font_size.get()
            )
            if success:
                self.status.config(text="✅ 转换成功")
                messagebox.showinfo("成功", "TXT 转 PDF 完成！")
            else:
                self.status.config(text="❌ 转换失败")
                messagebox.showerror("错误", "转换失败，请检查文件")

        threading.Thread(target=run, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()