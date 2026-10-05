"""
将提取的内容转换为 JSON 格式
"""
import json
from typing import Dict, Any
from .extractor import Paragraph


def to_json(doc: Dict[str, Any], indent: int = 2) -> str:
    """将提取结果转为 JSON 字符串"""
    paragraphs = doc["paragraphs"]

    data = {
        "metadata": {
            "filename": doc["filename"],
            "filetype": doc["filetype"],
            "size_bytes": doc["size"],
            "paragraph_count": len(paragraphs),
            "generated_by": "Universal Converter",
        },
        "content": {
            "title": doc["filename"].rsplit(".", 1)[0],
            "paragraphs": [_paragraph_to_obj(p) for p in paragraphs],
            "plain_text": _build_plain_text(paragraphs),
        },
    }

    return json.dumps(data, ensure_ascii=False, indent=indent)


def _paragraph_to_obj(p: Paragraph) -> Dict[str, Any]:
    """段落 → JSON 对象"""
    obj = {
        "type": p.style,
        "text": p.text,
    }
    if p.style == "heading":
        obj["level"] = p.level
    if p.style == "table":
        import json as _json
        try:
            obj["rows"] = _json.loads(p.text)
        except Exception:
            obj["rows"] = []
    return obj


def _build_plain_text(paragraphs) -> str:
    """构建纯文本全文"""
    return "\n\n".join(p.text for p in paragraphs if p.text)