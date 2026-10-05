"""
将提取的内容转换为 Markdown 格式
"""
from typing import Dict, Any, List
from .extractor import Paragraph


def to_markdown(doc: Dict[str, Any]) -> str:
    """将提取结果转为 Markdown 字符串"""
    lines = []

    # YAML Front Matter
    lines.append("---")
    lines.append(f"filename: {doc['filename']}")
    lines.append(f"filetype: {doc['filetype']}")
    lines.append(f"size: {doc['size']}")
    lines.append("---")
    lines.append("")

    # 标题
    title = doc["filename"].rsplit(".", 1)[0]
    lines.append(f"# {title}")
    lines.append("")

    paragraphs: List[Paragraph] = doc["paragraphs"]

    for para in paragraphs:
        if para.style == "heading":
            level = max(1, min(6, para.level))
            lines.append(f"{'#' * level} {para.text}")
            lines.append("")

        elif para.style == "list":
            lines.append(f"- {para.text}")
            lines.append("")

        elif para.style == "quote":
            lines.append(f"> {para.text}")
            lines.append("")

        elif para.style == "code":
            lines.append("```")
            lines.append(para.text)
            lines.append("```")
            lines.append("")

        elif para.style == "table":
            md_table = _json_to_md_table(para.text)
            lines.append(md_table)
            lines.append("")

        else:  # normal
            lines.append(para.text)
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _json_to_md_table(json_str: str) -> str:
    """将 JSON 二维数组转成 Markdown 表格"""
    import json

    try:
        rows = json.loads(json_str)
    except Exception:
        return json_str

    if not rows or not isinstance(rows, list):
        return json_str

    # 规范成同样列数
    max_cols = max(len(r) for r in rows)
    rows = [r + [""] * (max_cols - len(r)) for r in rows]

    # 转义 | 字符
    rows = [[str(c).replace("|", "\\|").replace("\n", " ") for c in r] for r in rows]

    lines = []
    lines.append("| " + " | ".join(rows[0]) + " |")
    lines.append("| " + " | ".join(["---"] * max_cols) + " |")
    for row in rows[1:]:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)