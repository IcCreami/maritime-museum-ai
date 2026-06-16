# -*- coding: utf-8 -*-
"""
AI辅助数字博物馆展品推荐系统 —— Streamlit 主程序
=================================================
运行：streamlit run app.py
"""

import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中，便于 src 包导入
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import json
from datetime import datetime

from src import config
from src.data_loader import load_exhibits, preprocess_exhibits, build_query_text
from src.matching_engine import MatchingEngine
from src.llm_generator import generate_learning_path, generate_learning_path_fallback


# ============================================================
# 页面基础配置
# ============================================================
st.set_page_config(
    page_title="AI辅助数字博物馆展品推荐系统",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# 注入自定义 CSS + Google Fonts
# ============================================================
def inject_css():
    fonts_css = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=LXGW+WenKai:wght@400;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Noto+Sans+SC:wght@300;400;500;700&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    """
    css = """
    <style>
    /* ============ 根变量 - 主题配色 ============ */
    :root {
        --ink-night: #0D1B2A;
        --ink-soft: #1F2D3D;
        --parchment: #F4EBD8;
        --parchment-warm: #EFE3C8;
        --parchment-deep: #E5D9BC;
        --brass-gold: #B8923F;
        --brass-light: #D4B06A;
        --seal-red: #A23B2C;
        --seal-red-soft: #B85444;
        --wave-teal: #3D6B7E;
        --ink-body: #2A2F3A;
        --ink-mute: #6B6355;
    }

    /* ============ 隐藏 Streamlit 默认元素 ============ */
    #MainMenu, header, footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent;
        height: 0;
    }
    .stApp {
        background: var(--parchment);
        background-image:
            radial-gradient(circle at 20% 10%, rgba(184, 146, 63, 0.04) 0%, transparent 40%),
            radial-gradient(circle at 80% 90%, rgba(61, 107, 126, 0.04) 0%, transparent 40%);
    }
    .stApp > header + div > div {
        /* 主内容区上方留白 */
        padding-top: 0;
    }

    /* ============ 全局字体 ============ */
    html, body, .stApp, .stApp p, .stApp li, .stApp label {
        font-family: 'Noto Sans SC', 'Source Serif 4', system-ui, sans-serif !important;
        color: var(--ink-body) !important;
    }
    h1, h2, h3, h4 {
        font-family: 'LXGW WenKai', 'Cormorant Garamond', serif !important;
        color: var(--ink-night) !important;
        letter-spacing: 0.01em;
    }

    /* ============ 顶部 Hero 区域 ============ */
    .hero {
        position: relative;
        background: linear-gradient(135deg, var(--ink-night) 0%, #12304a 50%, var(--wave-teal) 100%);
        color: var(--parchment) !important;
        padding: 3.5rem 2.5rem 3rem;
        border-radius: 2px;
        margin-bottom: 2rem;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(13, 27, 42, 0.25);
    }
    .hero::before {
        /* 水墨晕染效果 */
        content: "";
        position: absolute;
        inset: 0;
        background:
            radial-gradient(circle at 15% 20%, rgba(184, 146, 63, 0.18) 0%, transparent 35%),
            radial-gradient(circle at 85% 80%, rgba(61, 107, 126, 0.25) 0%, transparent 40%);
        pointer-events: none;
    }
    .hero::after {
        /* 底部装饰线 */
        content: "";
        position: absolute;
        left: 2.5rem;
        right: 2.5rem;
        bottom: 1rem;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--brass-gold), transparent);
    }
    .hero-compass {
        position: absolute;
        top: 1.5rem;
        right: 2rem;
        width: 80px;
        height: 80px;
        opacity: 0.35;
    }
    .hero-title-zh {
        font-family: 'LXGW WenKai', serif !important;
        font-size: 2.6rem;
        font-weight: 700;
        color: var(--parchment) !important;
        margin: 0 0 0.3rem 0;
        letter-spacing: 0.08em;
        position: relative;
    }
    .hero-title-en {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic;
        font-size: 1.1rem;
        color: var(--brass-light) !important;
        margin: 0 0 1.2rem 0;
        letter-spacing: 0.05em;
        position: relative;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        line-height: 1.7;
        color: rgba(244, 235, 216, 0.85) !important;
        max-width: 640px;
        margin: 0;
        position: relative;
    }
    .hero-rule {
        width: 60px;
        height: 2px;
        background: var(--brass-gold);
        margin: 1.2rem 0;
        border: none;
    }

    /* ============ 区块容器 ============ */
    .section-card {
        background: #FBF5E6;
        border: 1px solid var(--parchment-deep);
        border-radius: 3px;
        padding: 2rem 2.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 12px rgba(13, 27, 42, 0.04);
    }
    .section-eyebrow {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.25em;
        color: var(--brass-gold);
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .section-title {
        font-family: 'LXGW WenKai', serif !important;
        font-size: 1.5rem;
        color: var(--ink-night) !important;
        margin: 0 0 1.2rem 0;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid var(--parchment-deep);
    }
    .section-title .en {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic;
        font-size: 0.95rem;
        color: var(--ink-mute) !important;
        margin-left: 0.8rem;
        font-weight: 400;
    }

    /* ============ 表单美化 ============ */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] div {
        background: #FFFBF0 !important;
        border: 1px solid var(--parchment-deep) !important;
        border-radius: 2px !important;
        font-family: 'Noto Sans SC', sans-serif !important;
        color: var(--ink-body) !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--brass-gold) !important;
        box-shadow: 0 0 0 2px rgba(184, 146, 63, 0.15) !important;
    }
    .stTextInput label, .stTextArea label, .stSelectbox label {
        font-family: 'LXGW WenKai', serif !important;
        color: var(--ink-night) !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }

    /* ============ 主按钮 ============ */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"],
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover,
    .stButton > button[kind="primary"]:focus,
    .stButton > button[data-testid="baseButton-primary"]:focus {
        background: var(--ink-night) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 2px !important;
        padding: 0.65rem 2rem !important;
        font-family: 'LXGW WenKai', serif !important;
        font-size: 1rem !important;
        letter-spacing: 0.15em !important;
        transition: all 0.3s ease !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background: var(--wave-teal) !important;
        box-shadow: 0 4px 16px rgba(61, 107, 126, 0.3) !important;
        transform: translateY(-1px);
    }
    .stButton > button[kind="primary"]::before,
    .stButton > button[data-testid="baseButton-primary"]::before {
        content: "🧭 ";
    }

    /* ============ 展品卡片 ============ */
    .exhibit-card {
        background: #FFFDF5;
        border: 1px solid var(--parchment-deep);
        border-radius: 3px;
        padding: 1.5rem;
        position: relative;
        height: 100%;
        box-shadow: 0 4px 20px rgba(13, 27, 42, 0.06);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .exhibit-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 28px rgba(13, 27, 42, 0.12);
    }
    .exhibit-rank {
        position: absolute;
        top: -1px;
        left: -1px;
        background: var(--ink-night);
        color: var(--brass-light) !important;
        font-family: 'Cormorant Garamond', serif;
        font-size: 0.75rem;
        padding: 0.25rem 0.65rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
    }
    .exhibit-image-wrap {
        width: 100%;
        height: 180px;
        background: linear-gradient(135deg, var(--parchment-warm), var(--parchment-deep));
        border: 1px solid var(--parchment-deep);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        overflow: hidden;
        position: relative;
    }
    .exhibit-image-wrap img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .exhibit-image-placeholder {
        font-family: 'LXGW WenKai', serif;
        color: var(--ink-mute);
        font-size: 2.5rem;
        opacity: 0.4;
    }
    .exhibit-name-zh {
        font-family: 'LXGW WenKai', serif !important;
        font-size: 1.25rem;
        color: var(--ink-night) !important;
        margin: 0 0 0.2rem 0;
        line-height: 1.3;
    }
    .exhibit-name-en {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic;
        font-size: 0.85rem;
        color: var(--ink-mute) !important;
        margin: 0 0 0.8rem 0;
    }
    .exhibit-museum {
        font-size: 0.78rem;
        color: var(--ink-mute);
        margin-bottom: 0.8rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px dashed var(--parchment-deep);
    }
    .exhibit-museum::before {
        content: "来源 ";
        color: var(--brass-gold);
        font-family: 'LXGW WenKai', serif;
        margin-right: 0.3rem;
    }
    .exhibit-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
        margin-bottom: 1rem;
    }
    .tag-chip {
        font-family: 'Noto Sans SC', sans-serif;
        font-size: 0.72rem;
        padding: 0.2rem 0.55rem;
        background: var(--parchment);
        color: var(--wave-teal);
        border: 1px solid var(--parchment-deep);
        border-radius: 2px;
    }

    /* 匹配度印章 - 中国红印风格 */
    .match-seal {
        position: absolute;
        top: 1.2rem;
        right: 1.2rem;
        width: 68px;
        height: 68px;
        border: 2.5px solid var(--seal-red);
        border-radius: 4px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: rgba(162, 59, 44, 0.04);
        transform: rotate(-6deg);
        box-shadow: 0 2px 8px rgba(162, 59, 44, 0.15);
    }
    .match-seal-score {
        font-family: 'LXGW WenKai', serif;
        color: var(--seal-red) !important;
        font-size: 1.3rem;
        font-weight: 700;
        line-height: 1;
    }
    .match-seal-label {
        font-family: 'LXGW WenKai', serif;
        color: var(--seal-red) !important;
        font-size: 0.6rem;
        letter-spacing: 0.1em;
        margin-top: 0.15rem;
    }

    .match-reason {
        font-size: 0.85rem;
        line-height: 1.6;
        color: var(--ink-body);
        background: var(--parchment);
        padding: 0.8rem 1rem;
        border-left: 3px solid var(--brass-gold);
        margin-bottom: 1rem;
    }
    .exhibit-desc-toggle {
        font-family: 'Noto Sans SC', sans-serif;
        font-size: 0.8rem;
        color: var(--wave-teal);
        cursor: pointer;
        user-select: none;
        padding: 0.3rem 0;
        border-top: 1px dashed var(--parchment-deep);
        padding-top: 0.6rem;
    }
    .exhibit-desc-full {
        font-size: 0.82rem;
        line-height: 1.7;
        color: var(--ink-body);
        margin-top: 0.6rem;
        padding: 0.8rem;
        background: #FFFDF5;
        border: 1px solid var(--parchment-deep);
        border-radius: 2px;
    }
    .view-original-link {
        display: inline-block;
        margin-top: 0.8rem;
        padding: 0.45rem 1rem;
        background: transparent;
        color: var(--ink-night) !important;
        border: 1px solid var(--ink-night);
        border-radius: 2px;
        font-family: 'LXGW WenKai', serif !important;
        font-size: 0.82rem;
        letter-spacing: 0.1em;
        text-decoration: none;
        transition: all 0.25s ease;
    }
    .view-original-link:hover {
        background: var(--ink-night);
        color: var(--parchment) !important;
    }
    .view-original-link::after {
        content: " →";
    }

    /* ============ 学习路径区域 ============ */
    .learning-path-section {
        background: #FFFDF5;
        border: 1px solid var(--parchment-deep);
        border-top: 3px solid var(--brass-gold);
        padding: 2rem 2.5rem;
        border-radius: 3px;
        margin-top: 1rem;
    }
    .learning-path-section h3 {
        font-family: 'LXGW WenKai', serif !important;
        color: var(--ink-night) !important;
        border-bottom: 1px solid var(--parchment-deep);
        padding-bottom: 0.4rem;
        margin-top: 1.8rem !important;
    }
    .learning-path-section h3:first-child {
        margin-top: 0 !important;
    }
    .learning-path-section p, .learning-path-section li {
        font-family: 'Source Serif 4', 'Noto Sans SC', serif !important;
        font-size: 0.95rem !important;
        line-height: 1.85 !important;
        color: var(--ink-body) !important;
    }
    .learning-path-section strong {
        color: var(--seal-red) !important;
    }

    /* ============ 装饰分隔 ============ */
    .ornamental-rule {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin: 2rem 0;
        color: var(--brass-gold);
    }
    .ornamental-rule::before,
    .ornamental-rule::after {
        content: "";
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--brass-gold), transparent);
    }
    .ornamental-rule .symbol {
        font-family: 'LXGW WenKai', serif;
        font-size: 0.9rem;
        letter-spacing: 0.5em;
    }

    /* ============ 底部 ============ */
    .app-footer {
        margin-top: 3rem;
        padding: 1.5rem 0 1rem;
        border-top: 1px solid var(--parchment-deep);
        text-align: center;
        color: var(--ink-mute) !important;
        font-size: 0.78rem;
        letter-spacing: 0.05em;
    }
    .app-footer a {
        color: var(--wave-teal) !important;
        text-decoration: none;
        border-bottom: 1px solid var(--parchment-deep);
    }

    /* ============ 加载占位 ============ */
    .loading-hint {
        text-align: center;
        padding: 3rem 1rem;
        color: var(--ink-mute);
        font-family: 'LXGW WenKai', serif;
    }
    .loading-hint .compass-spin {
        display: inline-block;
        font-size: 2rem;
        animation: compass-rotate 3s ease-in-out infinite;
    }
    @keyframes compass-rotate {
        0%, 100% { transform: rotate(-15deg); }
        50% { transform: rotate(15deg); }
    }

    /* ============ 响应式 ============ */
    @media (max-width: 768px) {
        .hero { padding: 2rem 1.2rem; }
        .hero-title-zh { font-size: 1.8rem; }
        .hero-compass { width: 50px; height: 50px; top: 1rem; right: 1rem; }
        .section-card { padding: 1.2rem; }
    }

    @media (prefers-reduced-motion: reduce) {
        .loading-hint .compass-spin { animation: none; }
        .exhibit-card:hover { transform: none; }
    }
    </style>
    """
    st.markdown(fonts_css + css, unsafe_allow_html=True)


# ============================================================
# 指南针 SVG
# ============================================================
COMPASS_SVG = """
<svg class="hero-compass" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <g stroke="#D4B06A" stroke-width="0.8" fill="none" opacity="0.9">
    <circle cx="50" cy="50" r="45"/>
    <circle cx="50" cy="50" r="38"/>
    <circle cx="50" cy="50" r="3" fill="#D4B06A"/>
    <!-- 主方位 -->
    <path d="M 50 5 L 53 50 L 50 55 L 47 50 Z" fill="#D4B06A" opacity="0.8"/>
    <path d="M 50 95 L 53 50 L 50 45 L 47 50 Z" fill="#D4B06A" opacity="0.4"/>
    <path d="M 5 50 L 50 47 L 55 50 L 50 53 Z" fill="#D4B06A" opacity="0.4"/>
    <path d="M 95 50 L 50 47 L 45 50 L 50 53 Z" fill="#D4B06A" opacity="0.4"/>
    <!-- 斜方位 -->
    <path d="M 18 18 L 48 48 L 50 50 L 47 50 Z" fill="#D4B06A" opacity="0.3"/>
    <path d="M 82 18 L 52 48 L 50 50 L 53 50 Z" fill="#D4B06A" opacity="0.3"/>
    <path d="M 18 82 L 48 52 L 50 50 L 47 50 Z" fill="#D4B06A" opacity="0.3"/>
    <path d="M 82 82 L 52 52 L 50 50 L 53 50 Z" fill="#D4B06A" opacity="0.3"/>
    <!-- 刻度 -->
    <g stroke-width="0.5">
      <line x1="50" y1="8" x2="50" y2="13"/>
      <line x1="50" y1="87" x2="50" y2="92"/>
      <line x1="8" y1="50" x2="13" y2="50"/>
      <line x1="87" y1="50" x2="92" y2="50"/>
    </g>
    <!-- 北字 -->
    <text x="50" y="22" text-anchor="middle" font-family="LXGW WenKai, serif"
          font-size="7" fill="#D4B06A" font-weight="700">北</text>
  </g>
</svg>
"""


# ============================================================
# 页面渲染组件
# ============================================================
def render_hero():
    hero_html = """
    <div class="hero">
    """ + COMPASS_SVG + """
        <div class="hero-title-zh">""" + config.SYSTEM_TITLE_ZH + """</div>
        <div class="hero-title-en">""" + config.SYSTEM_TITLE_EN + """</div>
        <hr class="hero-rule">
        <p class="hero-subtitle">""" + config.SYSTEM_SUBTITLE_ZH + """</p>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)


def render_input_form():
    st.markdown("""
    <div class="section-card">
        <div class="section-eyebrow">STEP · 01</div>
        <div class="section-title">填写您的学习信息 <span class="en">Your Learning Profile</span></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.3, 1], gap="large")

    with col1:
        major_zh = st.selectbox(
            "专业方向 · Major",
            options=[m[0] for m in config.MAJORS] + ["其他 (Other)"],
            index=0,
        )
        if major_zh == "其他 (Other)":
            major_custom = st.text_input("请输入您的专业名称")
            major_zh = major_custom or "其他"
            major_en = major_custom or "Other"
        else:
            major_en = dict(config.MAJORS).get(major_zh, major_zh)

        course_name = st.text_input(
            "当前课程名称 · Course Name",
            placeholder="例：船舶导航系统 / 船舶结构力学 / 港口规划",
            max_chars=50,
        )

        keywords = st.text_input(
            "知识点关键词 · Keywords",
            placeholder="多个关键词请用空格分隔，例：罗盘 天文导航 航向",
            max_chars=200,
        )

    with col2:
        grade = st.selectbox(
            "年级 · Grade（选填）",
            options=["（不选择）"] + config.GRADES,
            index=0,
        )
        grade = None if grade == "（不选择）" else grade

        additional = st.text_area(
            "补充说明 · Notes（选填）",
            placeholder="如有特定需求，请补充说明。",
            max_chars=500,
            height=120,
        )

    # 校验
    submit_disabled = False
    validation_msg = None
    if st.session_state.get("_submitted_once"):
        if not course_name or len(course_name.strip()) < 2:
            validation_msg = "⚠ 请输入课程名称（至少 2 个字符）"
        elif not keywords or len(keywords.strip()) < 2:
            validation_msg = "⚠ 请输入至少一个知识点关键词"

    if validation_msg:
        st.warning(validation_msg)

    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        submitted = st.button(
            "开 始 推 荐",
            type="primary",
            use_container_width=True,
            disabled=not course_name or not keywords,
        )
    return {
        "submitted": submitted,
        "major_zh": major_zh,
        "major_en": major_en,
        "course_name": course_name.strip() if course_name else "",
        "keywords": keywords.strip() if keywords else "",
        "grade": grade,
        "additional_context": additional.strip() if additional else "",
    }


def render_exhibit_card(match_result: dict, course_name: str, top_keyword: str, index: int):
    """渲染单件展品卡片。"""
    from src.matching_engine import MatchingEngine
    ex = match_result["exhibit"]
    score_pct = int(match_result["similarity_score"] * 100)
    rank_label = ["TOP · 01", "TOP · 02", "TOP · 03"][index]
    reason = MatchingEngine.generate_reason_zh(match_result, course_name, top_keyword)

    tags_html = "".join(
        f'<span class="tag-chip">{t}</span>' for t in ex.get("tags", [])
    )

    # 图片处理：使用 SVG 占位图或用户提供的真实照片
    raw_path = ex.get("image_path", "")
    # Streamlit 会直接从项目根目录提供静态文件
    # 直接使用相对路径，Streamlit Cloud 会自动处理
    image_html = f'<img src="{raw_path}" alt="{ex.get("name_zh", "")}" style="width:100%;height:100%;object-fit:cover;">'

    card_html = f"""
    <div class="exhibit-card">
        <div class="exhibit-rank">{rank_label}</div>
        <div class="match-seal">
            <div class="match-seal-score">{score_pct}</div>
            <div class="match-seal-label">匹配度</div>
        </div>
        <div class="exhibit-image-wrap">{image_html}</div>
        <div class="exhibit-name-zh">{ex.get("name_zh", "")}</div>
        <div class="exhibit-name-en">{ex.get("name_en", "")}</div>
        <div class="exhibit-museum">{ex.get("source_museum_zh", "")}</div>
        <div class="exhibit-tags">{tags_html or '<span class="tag-chip">—</span>'}</div>
        <div class="match-reason">{reason}</div>
        <details>
            <summary class="exhibit-desc-toggle">展开展品详情 ›</summary>
            <div class="exhibit-desc-full">{ex.get("description_zh", "")}</div>
        </details>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_results(matches, user_info):
    st.markdown("""
    <div class="ornamental-rule"><span class="symbol">❖ 推荐展品 ❖</span></div>
    <div class="section-card">
        <div class="section-eyebrow">STEP · 02</div>
        <div class="section-title">基于您的课程为您精选 · Top 3 <span class="en">Curated Exhibits</span></div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3, gap="medium")
    top_keyword = (user_info["keywords"].split() or [""])[0]
    for i, match in enumerate(matches):
        with cols[i]:
            render_exhibit_card(match, user_info["course_name"], top_keyword, i)


def render_learning_path(llm_text: str):
    st.markdown("""
    <div class="ornamental-rule"><span class="symbol">❖ AI 学习路径 ❖</span></div>
    <div class="section-card">
        <div class="section-eyebrow">STEP · 03</div>
        <div class="section-title">AI 个性化学习路径建议 <span class="en">Personalized Learning Path</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="learning-path-section">
        {llm_text}
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown(f"""
    <div class="ornamental-rule"><span class="symbol">❖ 展览资源 ❖</span></div>
    <div class="section-card" style="text-align: center;">
        <div style="font-family: 'LXGW WenKai', serif; font-size: 1.05rem; color: var(--ink-night); margin-bottom: 0.4rem;">
            {config.EXHIBITION_NAME_ZH}
        </div>
        <div style="font-size: 0.82rem; color: var(--ink-mute); margin-bottom: 1rem;">
            所有推荐展品均来源于该数字展览，点击访问完整展览内容
        </div>
        <a class="view-original-link" href="{config.EXHIBITION_URL}" target="_blank" rel="noopener"
           style="display: inline-block; padding: 0.6rem 2rem; background: var(--ink-night); color: #FFFFFF !important; font-size: 0.95rem; text-decoration: none; border-radius: 2px;">
            🏛 访问完整数字展览
        </a>
    </div>
    <div class="app-footer">
        © 2026 ICET 2026 会议论文配套原型系统
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 主流程
# ============================================================
def main():
    inject_css()
    render_hero()

    # 初始化 session state
    if "matches" not in st.session_state:
        st.session_state.matches = None
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    if "llm_text" not in st.session_state:
        st.session_state.llm_text = None

    form_result = render_input_form()

    # 缓存加载过的展品（避免每次 rerun 重新预处理）
    @st.cache_resource
    def get_engine():
        exhibits = load_exhibits()
        exhibits = preprocess_exhibits(exhibits)
        engine = MatchingEngine()
        engine.build_corpus(exhibits)
        return engine, exhibits

    if form_result["submitted"]:
        st.session_state._submitted_once = True
        course = form_result["course_name"]
        kws = form_result["keywords"]

        if not course or len(course) < 2 or not kws or len(kws) < 2:
            st.stop()

        engine, exhibits = get_engine()
        query = build_query_text(course, kws, form_result["additional_context"])
        matches = engine.query(query, top_k=3)

        user_info = {
            "major": form_result["major_zh"],
            "major_en": form_result["major_en"],
            "course_name": form_result["course_name"],
            "course_name_en": form_result["course_name"],
            "keywords": form_result["keywords"],
            "keywords_en": form_result["keywords"],
            "grade": form_result["grade"],
            "additional_context": form_result["additional_context"],
        }

        # 调用 LLM（若无 API Key 则用 fallback）
        api_key_present = bool(
            config.OPENAI_API_KEY
            or config.DASHSCOPE_API_KEY
            or (config.BAIDU_API_KEY and config.BAIDU_SECRET_KEY)
        )
        try:
            if api_key_present:
                llm_text = generate_learning_path(user_info, matches, lang="zh")
            else:
                llm_text = generate_learning_path_fallback(user_info, matches, lang="zh")
        except Exception as e:
            llm_text = generate_learning_path_fallback(user_info, matches, lang="zh")
            st.warning(f"LLM 调用失败，已启用结构化占位文本。（原因：{e}）")

        st.session_state.matches = matches
        st.session_state.user_info = user_info
        st.session_state.llm_text = llm_text

    # 渲染已有结果
    if st.session_state.matches and st.session_state.user_info:
        render_results(st.session_state.matches, st.session_state.user_info)
        if st.session_state.llm_text:
            render_learning_path(st.session_state.llm_text)

    render_footer()


if __name__ == "__main__":
    main()
