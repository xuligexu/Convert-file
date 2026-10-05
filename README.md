# 🔄 Universal File Converter → MD / JSON

A **desktop application** that lets you drag any common file onto the left side of the window to convert it to **Markdown**, or onto the right side to convert it to **JSON**.

![preview](https://via.placeholder.com/900x600/0f172a/10b981?text=Universal+Converter)

---

## ✨ Features

- 🎯 **Dual Drop Zones** — Left zone converts to Markdown, right zone converts to JSON.
- 📂 **Multi-Format Support**
  - Documents: `pdf` `docx` `doc` `txt` `md` `rtf`
  - Web: `html` `htm`
  - Data: `csv` `json` `xlsx` `xls`
  - Code: `py` `js` `java` `c` `cpp` `go` `rs` `xml` `yaml`
  - Logs: `log`
- 🖱️ **Drag & Drop or Click** — Two ways to add files.
- 🔒 **Fully Local** — No data is ever uploaded.
- 📦 **One-Click EXE Build** — Run on Windows without Python installed.
- 🎨 **Dark Theme** — A modern, eye-friendly interface.

---

## 🚀 Quick Start

### Option 1: Download the EXE (Recommended for end users)

1. Go to [Releases](https://github.com/xuligexu/universal-converter/releases)
2. Download `UniversalConverter.exe`
3. Double-click to run ✅

### Option 2: Run from Source (For developers)

```bash
git clone https://github.com/xuligexu/universal-converter.git
cd universal-converter

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

### Option 3: Build Your Own EXE

```bash
python build.py
```

The executable will be generated in the `dist/` directory.

---

## 📖 How to Use

1. **Launch the app** — two drop zones will appear.
2. **Drag a file**:
   - Drop onto the **left green zone** → produces a `.md` file
   - Drop onto the **right orange zone** → produces a `.json` file
3. **Choose an output folder**
4. **View the result**

---

## 📄 Output Format Examples

### Markdown Output

```markdown
---
filename: example.docx
filetype: docx
size: 12345
---

# example

## Heading Level 1

This is a normal paragraph.

### Heading Level 2

- List item 1
- List item 2

| Name | Age |
| --- | --- |
| Alice | 25 |
| Bob | 30 |
```

### JSON Output

```json
{
  "metadata": {
    "filename": "example.docx",
    "filetype": "docx",
    "size_bytes": 12345,
    "paragraph_count": 7
  },
  "content": {
    "title": "example",
    "paragraphs": [
      { "type": "heading", "level": 1, "text": "Heading Level 1" },
      { "type": "normal", "text": "This is a normal paragraph." },
      { "type": "table", "text": "...", "rows": [["Name","Age"],["Alice","25"]] }
    ],
    "plain_text": "..."
  }
}
```

---

## 🛠️ Tech Stack

| Module | Technology |
|--------|------------|
| GUI | Tkinter + tkinterdnd2 |
| PDF | pdfplumber / pypdf |
| DOCX | python-docx |
| HTML | BeautifulSoup4 + lxml |
| RTF | striprtf |
| Excel | openpyxl |
| Packaging | PyInstaller |

---

## 📁 Project Structure

```
universal-converter/
├── main.py                # GUI entry point
├── core/
│   ├── extractor.py       # Per-format content extractors
│   ├── to_markdown.py     # Markdown generator
│   └── to_json.py         # JSON generator
├── build.py               # PyInstaller build script
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

---

## ❓ FAQ

**Q: `.doc` (legacy Word) files fail to convert?**

A: `.doc` is a binary legacy format. Recommendations:
- On Windows: install `antiword`
- Or open in Word and "Save As" `.docx`

**Q: Drag & drop doesn't work?**

A: Make sure `tkinterdnd2` is installed: `pip install tkinterdnd2`

**Q: The packaged EXE is quite large?**

A: PyInstaller bundles the Python interpreter and all dependencies. ~100 MB is normal.

**Q: macOS says "cannot verify developer"?**

A: Right-click the app → Open → Allow. Or run:
`xattr -d com.apple.quarantine UniversalConverter.app`

---

## 📜 License

MIT License

---

## 🌟 Star History

If this project helps you, please consider giving it a ⭐!