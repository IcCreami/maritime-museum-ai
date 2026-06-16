# -*- coding: utf-8 -*-
"""
展品数据导入与自动补全工具
========================
作用：
  - 从最小输入（CSV 或 JSON）自动生成完整的 exhibits.json
  - 自动填充：英文名/描述、英文标签、相关课程、相关关键词等
  - 极大减少人工输入工作量

使用方法：
  1. 复制 templates/exhibits_minimal_template.csv 或 .json
  2. 按你的展品信息填入（只需填有把握的字段，其他留空）
  3. 运行：
       python tools/import_exhibits.py templates/exhibits_minimal_template.csv
     或
       python tools/import_exhibits.py templates/exhibits_minimal_template.json

  4. 生成的完整数据会保存到 data/exhibits.json
"""

import sys
import json
import csv
from pathlib import Path
from typing import Dict, List, Any

# 确保能导入 src
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import jieba
import jieba.analyser

from src import config


# ============================================================
# 1. 类别 → 相关课程 的映射（自动生成 related_courses）
# ============================================================
CATEGORY_COURSES_MAP = {
    "船舶结构与建造": ["船舶阻力", "船舶结构力学", "造船工艺学", "船舶设计原理"],
    "航海技术与仪器": ["船舶导航系统", "航海仪器", "航海学基础", "天文航海学"],
    "港口与航运":     ["港口规划", "航运管理", "港口水工建筑物", "交通运输史"],
    "海军与军事航海": ["舰船原理", "海军史", "军事航海学"],
    "海上贸易与文化": ["交通运输史", "航运管理", "国际航运", "海上保险"],
    "航海人物与历史": ["交通运输史", "航海学基础", "海事法规"],
}


# ============================================================
# 2. 从中文描述自动提取关键词
# ============================================================
def auto_extract_keywords(description_zh: str, topk: int = 8) -> List[str]:
    """使用 jieba.analyser 提取描述中的关键词。"""
    keywords = jieba.analyser.extract_tags(description_zh, topK=topk)
    return keywords


# ============================================================
# 3. 英文占位生成（如有 LLM 可替换为真实翻译）
# ============================================================
def auto_translate_placeholder(zh_text: str, field_type: str = "text") -> str:
    """
    生成占位英文。
    生产环境中可替换为真实翻译 API 调用。
    """
    if field_type == "category":
        return {
            "船舶结构与建造": "Ship Structure & Construction",
            "航海技术与仪器": "Navigation Technology & Instruments",
            "港口与航运": "Port & Shipping",
            "海军与军事航海": "Naval & Military Maritime",
            "海上贸易与文化": "Maritime Trade & Culture",
            "航海人物与历史": "Maritime Figures & History",
        }.get(zh_text, zh_text)
    if field_type == "tags":
        # 输入为 list
        return [f"{t} (en)" for t in zh_text]
    return f"[EN translation placeholder] {zh_text[:100]}..."


# ============================================================
# 4. 加载最小输入
# ============================================================
def load_minimal_csv(path: Path) -> List[Dict]:
    """从 CSV 读取最小输入。"""
    items = []
    with path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # tags 和 related_courses 用 | 分隔
            item = dict(row)
            if isinstance(item.get("tags"), str):
                item["tags"] = [t.strip() for t in item["tags"].split("|") if t.strip()]
            if isinstance(item.get("related_courses"), str):
                item["related_courses"] = [c.strip() for c in item["related_courses"].split("|") if c.strip()]
            if isinstance(item.get("related_keywords"), str):
                item["related_keywords"] = [k.strip() for k in item["related_keywords"].split("|") if k.strip()]
            # 去除空字符串
            for k, v in list(item.items()):
                if v == "" or v is None:
                    item[k] = None
            items.append(item)
    return items


def load_minimal_json(path: Path) -> List[Dict]:
    """从 JSON 读取最小输入。"""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "exhibits" in data:
        return data["exhibits"]
    return data


# ============================================================
# 5. 单件展品自动补全
# ============================================================
def complete_exhibit(minimal: Dict) -> Dict:
    """从最小输入生成完整展品记录。"""
    ex = {}

    # 必填字段
    ex["id"] = minimal.get("id") or f"E{len(existing_exhibits)+1:02d}"
    ex["name_zh"] = minimal.get("name_zh", "").strip()
    ex["description_zh"] = minimal.get("description_zh", "").strip()
    ex["category_zh"] = minimal.get("category_zh", "").strip()
    ex["source_museum_zh"] = minimal.get("source_museum_zh", "").strip()

    # 标签
    ex["tags"] = minimal.get("tags") or []
    if isinstance(ex["tags"], str):
        ex["tags"] = [t.strip() for t in ex["tags"].split("|") if t.strip()]

    # 自动补全 - 英文名/描述（占位）
    ex["name_en"] = minimal.get("name_en") or auto_translate_placeholder(ex["name_zh"], "name")
    ex["description_en"] = minimal.get("description_en") or auto_translate_placeholder(ex["description_zh"], "description")
    ex["source_museum_en"] = minimal.get("source_museum_en") or auto_translate_placeholder(ex["source_museum_zh"], "museum")
    ex["category_en"] = minimal.get("category_en") or auto_translate_placeholder(ex["category_zh"], "category")

    # 自动补全 - 英文标签
    ex["tags_en"] = minimal.get("tags_en") or auto_translate_placeholder(ex["tags"], "tags")

    # 自动补全 - 历史背景
    ex["historical_context_zh"] = minimal.get("historical_context_zh") or ""
    ex["historical_context_en"] = minimal.get("historical_context_en") or ""

    # 自动补全 - 相关课程（基于类别映射）
    ex["related_courses"] = minimal.get("related_courses") or CATEGORY_COURSES_MAP.get(ex["category_zh"], [])

    # 自动补全 - 相关关键词（使用 jieba 提取）
    if minimal.get("related_keywords"):
        ex["related_keywords"] = minimal["related_keywords"]
    elif ex["description_zh"]:
        ex["related_keywords"] = auto_extract_keywords(ex["description_zh"], topk=8)
    else:
        ex["related_keywords"] = []

    # 图片路径（约定格式）
    ex["image_path"] = minimal.get("image_path") or f"assets/images/{ex['id']}_main.jpg"
    ex["image_thumbnail"] = minimal.get("image_thumbnail") or f"assets/images/{ex['id']}_thumb.jpg"

    # 展览链接
    ex["exhibition_url"] = minimal.get("exhibition_url") or f"https://example.com/exhibit/{ex['id']}"

    return ex


# ============================================================
# 6. 主流程
# ============================================================
def main():
    global existing_exhibits

    if len(sys.argv) < 2:
        print(__doc__)
        print("\n❌ 错误：请提供输入文件路径")
        print("示例：python tools/import_exhibits.py templates/exhibits_minimal_template.csv")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"❌ 文件不存在：{input_path}")
        sys.exit(1)

    # 加载已有展品（合并模式）
    output_path = config.EXHIBITS_PATH
    existing_exhibits = []
    if output_path.exists():
        print(f"📖 读取现有展品库：{output_path}")
        with output_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        existing_exhibits = data.get("exhibits", data) if isinstance(data, dict) else data
        print(f"   已有 {len(existing_exhibits)} 件展品")

    # 加载新输入
    print(f"📥 读取最小输入：{input_path}")
    if input_path.suffix == ".csv":
        new_items = load_minimal_csv(input_path)
    elif input_path.suffix == ".json":
        new_items = load_minimal_json(input_path)
    else:
        print(f"❌ 不支持的文件格式：{input_path.suffix}（请用 .csv 或 .json）")
        sys.exit(1)
    print(f"   读取到 {len(new_items)} 条待导入记录")

    # 补全 + 合并
    for minimal in new_items:
        print(f"\n🔧 处理：{minimal.get('id', '?')} · {minimal.get('name_zh', '?')}")
        completed = complete_exhibit(minimal)

        # 检查 ID 是否已存在（存在则更新）
        existing_ids = [e["id"] for e in existing_exhibits]
        if completed["id"] in existing_ids:
            idx = existing_ids.index(completed["id"])
            existing_exhibits[idx] = completed
            print(f"   ✅ 已更新已有展品 {completed['id']}")
        else:
            existing_exhibits.append(completed)
            print(f"   ✅ 已新增展品 {completed['id']}")

        print(f"      - 自动关键词：{', '.join(completed['related_keywords'][:5])}")
        print(f"      - 自动课程：{', '.join(completed['related_courses'][:3])}")

    # 保存
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump({"exhibits": existing_exhibits}, f, ensure_ascii=False, indent=2)
    print(f"\n🎉 完成！已保存 {len(existing_exhibits)} 件展品到：{output_path}")
    print("\n⚠️  请检查自动生成的英文内容，必要时替换为真实翻译。")
    print("   如需使用 LLM 进行真实翻译，请参考 docs/DATABASE_IMPORT_GUIDE.md")


if __name__ == "__main__":
    main()
