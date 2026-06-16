# -*- coding: utf-8 -*-
"""
交互式展品录入工具
===============
通过问答方式一步步引导你添加一件新展品。
适合不想编辑 JSON / CSV 的小白用户。

使用方法：
  python tools/add_exhibit.py
"""

import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import config


def ask(prompt, required=True, default=None):
    """询问用户输入。"""
    suffix = "（必填）" if required else "（选填，回车跳过）"
    default_hint = f" [{default}]" if default else ""
    while True:
        value = input(f"\n{prompt}{suffix}{default_hint}: ").strip()
        if not value and required and not default:
            print("   ❗ 此项为必填，请重新输入")
            continue
        return value or default or ""


def main():
    print("=" * 60)
    print("🧭 AI 辅助数字博物馆展品推荐系统 - 展品录入工具")
    print("=" * 60)
    print("\n我会一步步问你关于展品的信息，只需按提示填写即可。\n")

    # 加载现有数据
    output_path = config.EXHIBITS_PATH
    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        exhibits = data.get("exhibits", data) if isinstance(data, dict) else data
    else:
        exhibits = []

    next_id = f"E{len(exhibits)+1:02d}"
    print(f"💡 下一件展品的默认 ID 是：{next_id}（可直接回车接受）")

    # 收集最小信息
    ex = {}
    ex["id"] = ask("展品编号 (例 E01)", required=False, default=next_id)
    ex["name_zh"] = ask("展品中文名称 (例 清代水罗盘)")
    ex["description_zh"] = ask("展品详细描述 (100-500字，越详细匹配越准)")

    print("\n可选类别：")
    for i, cat in enumerate(config.CATEGORY_COURSES_MAP if hasattr(config, "CATEGORY_COURSES_MAP") else {}, start=1):
        print(f"  {i}. {cat}")
    print("  （如不匹配，可直接输入自定义类别名）")
    ex["category_zh"] = ask("展品类别")

    ex["source_museum_zh"] = ask("来源博物馆")
    tags_str = ask("专业标签 (用空格分隔，例 指南针 航海导航)")
    ex["tags"] = [t.strip() for t in tags_str.split() if t.strip()]
    ex["exhibition_url"] = ask("原始展览链接", required=False, default=f"https://example.com/exhibit/{ex['id']}")

    # 自动补全（复用 import_exhibits 的逻辑）
    from tools.import_exhibits import complete_exhibit
    completed = complete_exhibit(ex)

    # 展示生成的完整记录
    print("\n" + "=" * 60)
    print("📋 生成的完整展品记录：")
    print("=" * 60)
    print(json.dumps(completed, ensure_ascii=False, indent=2))

    confirm = input("\n确认保存？(y/n): ").strip().lower()
    if confirm != "y":
        print("❌ 已取消")
        return

    # 检查 ID 是否已存在
    existing_ids = [e["id"] for e in exhibits]
    if completed["id"] in existing_ids:
        idx = existing_ids.index(completed["id"])
        exhibits[idx] = completed
        print(f"\n✅ 已更新展品 {completed['id']}")
    else:
        exhibits.append(completed)
        print(f"\n✅ 已新增展品 {completed['id']}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump({"exhibits": exhibits}, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存到：{output_path}")
    print(f"\n🎉 当前共 {len(exhibits)} 件展品。")
    print("   重启 Streamlit 应用即可看到新展品：streamlit run app.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消。")
        sys.exit(0)
