"""
从各种文件格式中提取结构化文本内容
统一输出: List[Paragraph]，每个 Paragraph 包含 text 和 type
"""
import os
import csv
import json
from pathlib import Path
from typing import List, Dict, Any


class Paragraph:
    """统一的段落结构"""

    def __init__(self, text: str, style: str = "normal", level: int = 0):
        self.text = text.strip()
        self.style = style      # normal | heading | list | table | code | quote
        self.level = level      # 标题级别、列表缩进等

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "style": self.style,
            "level": self.level,
        }


class DocumentExtractor:
    """从各种格式提取内容"""

    SUPPORTED_EXTS = {
        ".txt", ".md", ".markdown",
        ".pdf",
        ".docx", ".doc",
        ".rtf",
        ".html", ".htm",
        ".csv",
        ".json",
        ".xlsx", ".xls",
        ".log",
        ".py", ".js", ".java", ".c", ".cpp", ".go", ".rs",
        ".xml", ".yaml", ".yml",
    }

    @classmethod
    def is_supported(cls, filepath: str) -> bool:
        return Path(filepath).suffix.lower() in cls.SUPPORTED_EXTS

    @classmethod
    def extract(cls, filepath: str) -> Dict[str, Any]:
        """
        提取文件内容
        返回: {
            "filename": ...,
            "filetype": ...,
            "paragraphs": [Paragraph, ...],
            "metadata": {...}
        }
        """
        path = Path(filepath)
        ext = path.suffix.lower()

        result = {
            "filename": path.name,
            "filetype": ext.lstrip("."),
            "filepath": str(path.absolute()),
            "size": path.stat().st_size if path.exists() else 0,
            "paragraphs": [],
            "metadata": {},
        }

        try:
            if ext in (".txt", ".log", ".md", ".markdown",
                       ".py", ".js", ".java", ".c", ".cpp",
                       ".go", ".rs", ".xml", ".yaml", ".yml"):
                result["paragraphs"] = cls._extract_text(filepath)
            elif ext == ".pdf":
                result["paragraphs"] = cls._extract_pdf(filepath)
            elif ext == ".docx":
                result["paragraphs"] = cls._extract_docx(filepath)
            elif ext == ".doc":
                result["paragraphs"] = cls._extract_doc(filepath)
            elif ext == ".rtf":
                result["paragraphs"] = cls._extract_rtf(filepath)
            elif ext in (".html", ".htm"):
                result["paragraphs"] = cls._extract_html(filepath)
            elif ext == ".csv":
                result["paragraphs"] = cls._extract_csv(filepath)
            elif ext == ".json":
                result["paragraphs"] = cls._extract_json(filepath)
            elif ext in (".xlsx", ".xls"):
                result["paragraphs"] = cls._extract_excel(filepath)
            else:
                # 兜底：当纯文本处理
                result["paragraphs"] = cls._extract_text(filepath)
        except Exception as e:
            raise RuntimeError(f"解析 {path.name} 失败: {e}")

        return result

    # ============ 各格式解析 ============

    @staticmethod
    def _extract_text(filepath: str) -> List[Paragraph]:
        """纯文本 → 段落（按空行分段）"""
        paragraphs = []
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # 按空行分段
        blocks = [b.strip() for b in content.split("\n\n") if b.strip()]
        if not blocks:
            blocks = [content.strip()] if content.strip() else []

        for block in blocks:
            # 识别 Markdown 标题
            lines = block.split("\n")
            first = lines[0]
            if first.startswith("#"):
                level = len(first) - len(first.lstrip("#"))
                paragraphs.append(Paragraph(
                    first.lstrip("# ").strip(), "heading", level
                ))
                # 剩余行作为普通段落
                rest = "\n".join(lines[1:]).strip()
                if rest:
                    paragraphs.append(Paragraph(rest, "normal"))
            else:
                paragraphs.append(Paragraph(block, "normal"))

        return paragraphs

    @staticmethod
    def _extract_pdf(filepath: str) -> List[Paragraph]:
        """PDF → 段落"""
        paragraphs = []
        try:
            import pdfplumber
            with pdfplumber.open(filepath) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    # 尝试提取表格
                    tables = page.extract_tables()
                    for block in text.split("\n\n"):
                        block = block.strip()
                        if block:
                            paragraphs.append(Paragraph(block, "normal"))

                    for table in tables:
                        rows = []
                        for row in table:
                            rows.append([str(c or "").strip() for c in row])
                        if rows:
                            paragraphs.append(Paragraph(
                                json.dumps(rows, ensure_ascii=False),
                                "table"
                            ))
        except ImportError:
            # 降级到 pypdf
            from pypdf import PdfReader
            reader = PdfReader(filepath)
            for page in reader.pages:
                text = page.extract_text() or ""
                for block in text.split("\n\n"):
                    block = block.strip()
                    if block:
                        paragraphs.append(Paragraph(block, "normal"))

        return paragraphs

    @staticmethod
    def _extract_docx(filepath: str) -> List[Paragraph]:
        """DOCX → 段落"""
        from docx import Document

        doc = Document(filepath)
        paragraphs = []

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            style = "normal"
            level = 0
            if para.style.name.startswith("Heading"):
                style = "heading"
                try:
                    level = int(para.style.name.split()[-1])
                except ValueError:
                    level = 1
            elif para.style.name.startswith("List"):
                style = "list"
            paragraphs.append(Paragraph(text, style, level))

        # 提取表格
        for table in doc.tables:
            rows = []
            for row in table.rows:
                rows.append([cell.text.strip() for cell in row.cells])
            if rows:
                paragraphs.append(Paragraph(
                    json.dumps(rows, ensure_ascii=False), "table"
                ))

        return paragraphs

    @staticmethod
    def _extract_doc(filepath: str) -> List[Paragraph]:
        """老版 .doc（仅 Linux/Mac 可通过 antiword 支持）"""
        import subprocess
        try:
            result = subprocess.run(
                ["antiword", filepath],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                paragraphs = []
                for block in result.stdout.split("\n\n"):
                    if block.strip():
                        paragraphs.append(Paragraph(block.strip(), "normal"))
                return paragraphs
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        raise RuntimeError(
            ".doc 格式需要安装 antiword，建议先另存为 .docx"
        )

    @staticmethod
    def _extract_rtf(filepath: str) -> List[Paragraph]:
        """RTF → 段落"""
        from striprtf.striprtf import rtf_to_text

        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        text = rtf_to_text(content)
        paragraphs = []
        for block in text.split("\n\n"):
            if block.strip():
                paragraphs.append(Paragraph(block.strip(), "normal"))
        return paragraphs

    @staticmethod
    def _extract_html(filepath: str) -> List[Paragraph]:
        """HTML → 段落"""
        from bs4 import BeautifulSoup

        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        paragraphs = []

        for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6",
                                       "p", "li", "blockquote", "pre"]):
            text = element.get_text(strip=True)
            if not text:
                continue

            tag = element.name
            if tag.startswith("h"):
                paragraphs.append(Paragraph(text, "heading", int(tag[1])))
            elif tag == "li":
                paragraphs.append(Paragraph(text, "list"))
            elif tag == "blockquote":
                paragraphs.append(Paragraph(text, "quote"))
            elif tag == "pre":
                paragraphs.append(Paragraph(text, "code"))
            else:
                paragraphs.append(Paragraph(text, "normal"))

        # 处理表格
        for table in soup.find_all("table"):
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(cells)
            if rows:
                paragraphs.append(Paragraph(
                    json.dumps(rows, ensure_ascii=False), "table"
                ))

        return paragraphs

    @staticmethod
    def _extract_csv(filepath: str) -> List[Paragraph]:
        """CSV → 表格段落"""
        paragraphs = []
        with open(filepath, "r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.reader(f)
            rows = [row for row in reader if any(cell.strip() for cell in row)]

        if rows:
            paragraphs.append(Paragraph(
                json.dumps(rows, ensure_ascii=False), "table"
            ))
        return paragraphs

    @staticmethod
    def _extract_json(filepath: str) -> List[Paragraph]:
        """JSON → 段落"""
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)

        text = json.dumps(data, ensure_ascii=False, indent=2)
        return [Paragraph(text, "code")]

    @staticmethod
    def _extract_excel(filepath: str) -> List[Paragraph]:
        """Excel → 表格段落"""
        from openpyxl import load_workbook

        wb = load_workbook(filepath, data_only=True)
        paragraphs = []

        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            rows = []
            for row in sheet.iter_rows(values_only=True):
                cells = ["" if c is None else str(c) for c in row]
                if any(c.strip() for c in cells):
                    rows.append(cells)

            if rows:
                # 加一个标题行表示工作表
                paragraphs.append(Paragraph(f"工作表: {sheet_name}", "heading", 2))
                paragraphs.append(Paragraph(
                    json.dumps(rows, ensure_ascii=False), "table"
                ))

        return paragraphs