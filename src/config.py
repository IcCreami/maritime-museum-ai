# -*- coding: utf-8 -*-
"""
系统配置模块
===========
集中管理所有可调整的参数、API 密钥、路径等。
"""

import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# 路径配置
DATA_DIR = PROJECT_ROOT / "data"
EXHIBITS_PATH = DATA_DIR / "exhibits.json"
SESSIONS_PATH = DATA_DIR / "sessions.json"
PROMPTS_DIR = PROJECT_ROOT / "prompts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

# TF-IDF 匹配引擎参数
TFIDF_CONFIG = dict(
    analyzer="char_wb",
    ngram_range=(1, 3),
    max_df=0.95,
    min_df=1,
    max_features=8000,
    sublinear_tf=True,
    strip_accents="unicode",
)

MATCH_WEIGHTS = dict(description=1.0, tags=1.5, name=2.0)
TOP_K = 3

# LLM 配置
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_MODEL = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
BAIDU_API_KEY = os.getenv("BAIDU_API_KEY", "")
BAIDU_SECRET_KEY = os.getenv("BAIDU_SECRET_KEY", "")
BAIDU_MODEL = os.getenv("BAIDU_MODEL", "ernie-bot-4")
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 1200
LLM_TOP_P = 0.9

# 专业方向
MAJORS = [
    ("航海技术", "Marine Navigation"),
    ("船舶与海洋工程", "Naval Architecture & Ocean Engineering"),
    ("交通运输", "Transportation"),
    ("港口航道与海岸工程", "Port & Waterway Engineering"),
    ("轮机工程", "Marine Engineering"),
    ("船舶电子电气工程", "Marine Electrical & Electronic Engineering"),
    ("海事管理", "Maritime Management"),
]

GRADES = ["大一", "大二", "大三", "大四", "研究生"]

# 停用词（精简）
STOP_WORDS = set(
    "的 了 和 是 就 都 而 及 与 着 或 一个 没有 我们 你们 他们 "
    "在 上 下 左 右 中 前 后 里 外 来 去 又 也 很 最 更 这 那 "
    "有 为 以 对 从 到 被 把 让 向 往 各 每 其 之 于 并 等".split()
)

EXHIBITION_NAME_ZH = "「一馆一物说航海」——中国航海类博物馆文物精品数字展"
EXHIBITION_NAME_EN = "One Museum, One Object: Maritime Digital Exhibition"
EXHIBITION_URL = "https://www.720yun.com/vr/01028c8da4r"
SYSTEM_TITLE_ZH = "AI辅助数字博物馆展品推荐系统"
SYSTEM_TITLE_EN = "AI-Assisted Digital Museum Exhibit Recommendation System"
SYSTEM_SUBTITLE_ZH = (
    "本系统基于「一馆一物说航海——中国航海类博物馆文物精品数字展」资源，运用 AI 语义匹配技术，"
    "为航海与交通相关专业的大学生推荐与课程高度关联的展品，并生成个性化学习路径。"
)
SYSTEM_SUBTITLE_EN = (
    "Leveraging AI semantic matching on the 'One Museum, One Object' digital exhibition, "
    "this system recommends highly course-relevant exhibits for maritime and transportation students, "
    "and generates personalized learning paths."
)
