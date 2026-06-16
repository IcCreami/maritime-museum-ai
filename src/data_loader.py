# -*- coding: utf-8 -*-
"""
数据加载与预处理模块
=================
负责：读取展品、文本清洗、分词、拼接匹配文本。
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any

import jieba

from . import config


def load_exhibits(path: Path = None) -> List[Dict[str, Any]]:
    path = path or config.EXHIBITS_PATH
    if not path.exists():
        raise FileNotFoundError(f"找不到展品数据文件：{path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "exhibits" in data:
        data = data["exhibits"]
    return data


_HTML_TAG_RE = re.compile(r"<[^>]+>")
_SPECIAL_CHAR_RE = re.compile(r"[^一-龥A-Za-z0-9\s]")
_MULTI_SPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = _HTML_TAG_RE.sub("", text)
    text = _SPECIAL_CHAR_RE.sub(" ", text)
    text = _MULTI_SPACE_RE.sub(" ", text).strip()
    return text


def tokenize_zh(text: str) -> str:
    words = jieba.cut(text, cut_all=False)
    filtered = [w.strip() for w in words if w.strip() and w.strip() not in config.STOP_WORDS]
    return " ".join(filtered)


def build_match_text(exhibit: Dict[str, Any]) -> str:
    name = exhibit.get("name_zh", "")
    tags = " ".join(exhibit.get("tags", []))
    desc = exhibit.get("description_zh", "")
    # 名称重复 2 次（权重 2.0），标签重复 1 次（int(1.5)=1），描述不重复
    name_repeat = 2
    tag_repeat = 1
    name_part = (name + " ") * name_repeat
    tag_part = (tags + " ") * tag_repeat
    desc_part = desc
    full = f"{name_part} {tag_part} {desc_part}"
    return clean_text(full)


def build_query_text(course_name: str, keywords: str, additional_context: str = "") -> str:
    raw = f"{course_name} {keywords} {additional_context}"
    cleaned = clean_text(raw)
    tokenized = tokenize_zh(cleaned)
    return tokenized


def preprocess_exhibits(exhibits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for ex in exhibits:
        match_text = build_match_text(ex)
        ex["_match_text"] = match_text
        ex["_match_text_tokenized"] = tokenize_zh(match_text)
    return exhibits


def build_exhibit_index(exhibits: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {ex["id"]: ex for ex in exhibits}
