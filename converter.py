"""
PDF 和 TXT 文件互转核心模块
"""
import os
from pathlib import Path
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PDFTXTConverter:
    """PDF 和 TXT 文件互转工具类"""

    def __init__(self, font_path: str = None):
        """
        初始化转换器

        Args:
            font_path: 中文字体路径（可选）。如果不指定，将尝试使用系统字体。
        """
        self.font_name = "Helvetica"
        self.font_path = font_path

        # 尝试注册中文字体
        self._register_chinese_font()

    def _register_chinese_font(self):
        """注册中文字体，用于生成中文 PDF"""
        # 常见的中文字体路径
        possible_fonts = [
            self.font_path,
            # Windows
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            # macOS
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            # Linux
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

        for font_path in possible_fonts:
            if font_path and os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
                    self.font_name = "ChineseFont"
                    return
                except Exception:
                    continue

    def pdf_to_txt(self, pdf_path: str, txt_path: str) -> bool:
        """
        将 PDF 文件转换为 TXT 文件

        Args:
            pdf_path: 输入的 PDF 文件路径
            txt_path: 输出的 TXT 文件路径

        Returns:
            bool: 转换是否成功
        """
        try:
            reader = PdfReader(pdf_path)
            text_content = []

            for i, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text:
                    text_content.append(f"=== 第 {i} 页 ===\n{text}\n")

            # 写入 TXT 文件
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write("\n".join(text_content))

            return True

        except Exception as e:
            print(f"❌ PDF 转 TXT 失败: {e}")
            return False

    def txt_to_pdf(self, txt_path: str, pdf_path: str,
                   font_size: int = 12, line_height: int = 18) -> bool:
        """
        将 TXT 文件转换为 PDF 文件

        Args:
            txt_path: 输入的 TXT 文件路径
            pdf_path: 输出的 PDF 文件路径
            font_size: 字号
            line_height: 行高

        Returns:
            bool: 转换是否成功
        """
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4
            margin = 50
            y = height - margin

            for line in lines:
                # 处理长行自动换行
                line = line.rstrip("\n")
                wrapped_lines = self._wrap_text(line, width - 2 * margin, font_size)

                for wrapped in wrapped_lines:
                    if y < margin + line_height:
                        c.showPage()
                        y = height - margin

                    c.setFont(self.font_name, font_size)
                    c.drawString(margin, y, wrapped)
                    y -= line_height

            c.save()
            return True

        except Exception as e:
            print(f"❌ TXT 转 PDF 失败: {e}")
            return False

    def _wrap_text(self, text: str, max_width: float, font_size: int) -> list:
        """
        长文本自动换行

        Args:
            text: 原文本
            max_width: 最大宽度
            font_size: 字号

        Returns:
            list: 换行后的文本列表
        """
        if not text:
            return [""]

        # 按字符宽度估算
        char_width = font_size * 0.6
        max_chars = max(1, int(max_width / char_width))

        result = []
        for i in range(0, len(text), max_chars):
            result.append(text[i:i + max_chars])

        return result

    def batch_convert(self, input_dir: str, output_dir: str,
                      direction: str = "pdf2txt") -> dict:
        """
        批量转换

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            direction: 转换方向，"pdf2txt" 或 "txt2pdf"

        Returns:
            dict: 转换结果统计
        """
        os.makedirs(output_dir, exist_ok=True)
        stats = {"success": 0, "failed": 0, "files": []}

        if direction == "pdf2txt":
            ext_in, ext_out = ".pdf", ".txt"
            convert_func = self.pdf_to_txt
        else:
            ext_in, ext_out = ".txt", ".pdf"
            convert_func = self.txt_to_pdf

        for file in Path(input_dir).glob(f"*{ext_in}"):
            output_file = Path(output_dir) / (file.stem + ext_out)
            if convert_func(str(file), str(output_file)):
                stats["success"] += 1
                stats["files"].append(str(output_file))
            else:
                stats["failed"] += 1

        return stats