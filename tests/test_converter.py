"""
单元测试
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from converter import PDFTXTConverter


class TestConverter(unittest.TestCase):

    def setUp(self):
        self.converter = PDFTXTConverter()
        self.tmpdir = tempfile.mkdtemp()

    def test_txt_to_pdf(self):
        """测试 TXT 转 PDF"""
        txt_path = os.path.join(self.tmpdir, "test.txt")
        pdf_path = os.path.join(self.tmpdir, "test.pdf")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("Hello World\n测试中文\nLine 3")

        result = self.converter.txt_to_pdf(txt_path, pdf_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 0)

    def test_pdf_to_txt(self):
        """测试 PDF 转 TXT（先生成再读取）"""
        txt_path = os.path.join(self.tmpdir, "source.txt")
        pdf_path = os.path.join(self.tmpdir, "source.pdf")
        output_txt = os.path.join(self.tmpdir, "output.txt")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("Hello World\nSecond Line")

        # 先生成 PDF
        self.converter.txt_to_pdf(txt_path, pdf_path)
        self.assertTrue(os.path.exists(pdf_path))

        # 再转回 TXT
        result = self.converter.pdf_to_txt(pdf_path, output_txt)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_txt))

        with open(output_txt, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Hello World", content)

    def test_nonexistent_file(self):
        """测试不存在的文件"""
        result = self.converter.pdf_to_txt(
            "/nonexistent/file.pdf",
            os.path.join(self.tmpdir, "out.txt")
        )
        self.assertFalse(result)

    def test_wrap_text(self):
        """测试文本换行"""
        result = self.converter._wrap_text("abcdefghij", 60, 10)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_wrap_empty(self):
        """测试空文本换行"""
        result = self.converter._wrap_text("", 100, 12)
        self.assertEqual(result, [""])


if __name__ == "__main__":
    unittest.main()