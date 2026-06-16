# -*- coding: utf-8 -*-
"""
LLM 学习路径生成模块
=================
根据 Top-3 推荐结果 + 用户信息，调用大语言模型生成：
  - 展品知识解读
  - 课程关联分析
  - 个性化学习路径建议

支持三家后端：OpenAI / 通义千问 / 文心一言
"""

from pathlib import Path
from typing import List, Dict

from . import config


# ============================================================
# 1. Prompt 模板加载
# ============================================================
def _load_prompt_template(lang: str = "zh") -> str:
    fname = f"learning_path_{lang}.txt"
    path = config.PROMPTS_DIR / fname
    if not path.exists():
        raise FileNotFoundError(f"找不到 Prompt 模板文件：{path}")
    return path.read_text(encoding="utf-8")


def _format_prompt(
    template: str,
    user_info: Dict,
    matches: List[Dict],
    lang: str = "zh",
) -> str:
    """将模板中的占位符替换为实际内容。"""
    # 根据语言选择字段后缀
    suffix = "_zh" if lang == "zh" else "_en"

    # 构建填充字典
    fill = {}

    # 用户信息
    fill["major"] = user_info.get("major", "")
    fill["major_en"] = user_info.get("major_en", "")
    fill["course_name"] = user_info.get("course_name", "")
    fill["course_name_en"] = user_info.get("course_name_en", "")
    fill["keywords"] = user_info.get("keywords", "")
    fill["keywords_en"] = user_info.get("keywords_en", "")
    fill["additional_context"] = user_info.get("additional_context", "")

    # 展品信息（3 件）
    for i in range(3):
        idx = i + 1
        if i < len(matches):
            match = matches[i]
            exhibit = match["exhibit"]
            score = match["similarity_score"]

            # 提取展品字段（根据语言后缀）
            fill[f"exhibit_{idx}_name"] = exhibit.get(f"name{suffix}", "")
            fill[f"exhibit_{idx}_museum"] = exhibit.get(f"source_museum{suffix}", "")
            fill[f"exhibit_{idx}_description"] = exhibit.get(f"description{suffix}", "")
            fill[f"score_{idx}"] = int(score * 100)
        else:
            # 如果不足 3 件，填空值
            fill[f"exhibit_{idx}_name"] = "（无）"
            fill[f"exhibit_{idx}_museum"] = ""
            fill[f"exhibit_{idx}_description"] = ""
            fill[f"score_{idx}"] = 0

    # 使用 format_map 填充模板，缺失的键保留原样
    class SafeDict(dict):
        def __missing__(self, key):
            return "{" + key + "}"

    return template.format_map(SafeDict(fill))


# ============================================================
# 2. 各后端调用
# ============================================================
def _call_openai(prompt: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("请先安装 openai：pip install openai")
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "你是一位航海与交通领域的教育专家。"},
            {"role": "user", "content": prompt},
        ],
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_TOKENS,
        top_p=config.LLM_TOP_P,
    )
    return resp.choices[0].message.content.strip()


def _call_qwen(prompt: str) -> str:
    try:
        import dashscope
        from dashscope import Generation
    except ImportError:
        raise ImportError("请先安装 dashscope：pip install dashscope")
    dashscope.api_key = config.DASHSCOPE_API_KEY
    resp = Generation.call(
        model=config.DASHSCOPE_MODEL,
        messages=[
            {"role": "system", "content": "你是一位航海与交通领域的教育专家。"},
            {"role": "user", "content": prompt},
        ],
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.LLM_MAX_TOKENS,
        top_p=config.LLM_TOP_P,
        result_format="message",
    )
    return resp.output.choices[0].message.content.strip()


def _call_ernie(prompt: str) -> str:
    try:
        import qianfan
    except ImportError:
        raise ImportError("请先安装 qianfan：pip install qianfan")
    chat = qianfan.ChatCompletion(
        ak=config.BAIDU_API_KEY,
        sk=config.BAIDU_SECRET_KEY,
    )
    resp = chat.do(
        model=config.BAIDU_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=config.LLM_TEMPERATURE,
        top_p=config.LLM_TOP_P,
    )
    return resp["result"].strip()


_BACKENDS = {
    "openai": _call_openai,
    "qwen": _call_qwen,
    "ernie": _call_ernie,
}


# ============================================================
# 3. 统一入口
# ============================================================
def generate_learning_path(
    user_info: Dict,
    matches: List[Dict],
    lang: str = "zh",
) -> str:
    """
    根据用户信息和匹配结果生成学习路径文本。

    参数：
      user_info: {
          "major": "航海技术",
          "major_en": "Marine Navigation",
          "course_name": "船舶导航系统",
          "course_name_en": "Ship Navigation Systems",
          "keywords": "罗盘 天文导航",
          "keywords_en": "compass celestial navigation",
          "additional_context": "...",
      }
      matches: MatchingEngine.query() 的返回结果（Top-3）
      lang: "zh" 或 "en"
    """
    template = _load_prompt_template(lang)
    prompt = _format_prompt(template, user_info, matches, lang)

    provider = config.LLM_PROVIDER.lower()
    if provider not in _BACKENDS:
        raise ValueError(f"不支持的 LLM_PROVIDER: {provider}")

    return _BACKENDS[provider](prompt)


# ============================================================
# 4. 离线 / 调试用 fallback（无 API Key 时返回占位文本）
# ============================================================
def generate_learning_path_fallback(
    user_info: Dict,
    matches: List[Dict],
    lang: str = "zh",
) -> str:
    """不调用 API，返回结构化占位文本，用于演示或调试。"""
    course = user_info.get("course_name", "您的课程")
    lines = []
    if lang == "zh":
        lines.append("### 一、展品知识解读\n")
        for i, m in enumerate(matches, 1):
            ex = m["exhibit"]
            name = ex.get("name_zh", "")
            desc = ex.get("description_zh", "")[:120]
            lines.append(f"**{i}. {name}**  ")
            lines.append(f"{desc}……\n")
        lines.append(f"### 二、课程关联分析\n")
        lines.append(f"以上展品与课程「{course}」在知识点上存在显著关联，建议结合实物理解理论。\n")
        lines.append("### 三、建议学习路径\n")
        lines.append("建议按推荐顺序依次学习，由基础概念到综合应用，逐步深入。\n")
    else:
        lines.append("### I. Exhibit Interpretations\n")
        for i, m in enumerate(matches, 1):
            ex = m["exhibit"]
            name = ex.get("name_en", "")
            desc = ex.get("description_en", "")[:200]
            lines.append(f"**{i}. {name}**  ")
            lines.append(f"{desc}...\n")
        lines.append(f"### II. Course Relevance Analysis\n")
        lines.append(f"These exhibits connect strongly with the course \"{course}\".\n")
        lines.append("### III. Suggested Learning Path\n")
        lines.append("Proceed in the recommended order, from foundational concepts to integrated applications.\n")
    return "\n".join(lines)
