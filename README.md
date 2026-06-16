# 🧭 AI 辅助数字博物馆展品推荐系统

> An Exploration of AI-Assisted Digital Museum Exhibit Recommendation for College Course Integration

基于「一馆一物说航海」数字展览资源，为交通运输 / 航海相关专业大学生提供 AI 驱动的展品推荐与个性化学习路径生成。

---

## 📖 项目概述

**对应论文**：ICET 2026 会议论文配套原型系统

**核心能力**：
- **TF-IDF 语义匹配**：将学生的课程信息、关键词与展品描述进行语义匹配
- **Top-3 展品推荐**：自动推荐匹配度最高的三件展品
- **AI 学习路径**：调用 LLM（OpenAI / 通义千问 / 文心一言）生成个性化学习建议

---

## 🚀 快速开始（5 分钟跑起来）

### 1. 安装依赖

```bash
cd AI-Museum-Recommendation-System
pip install -r requirements.txt
```

### 2. 配置 API 密钥（可选）

```bash
cp .env.example .env
# 编辑 .env，填入你的 API 密钥
```

不配置 API 密钥时，系统会使用结构化占位文本演示全部功能。

### 3. 启动应用

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`

---

## 📁 项目结构

```
AI-Museum-Recommendation-System/
├── app.py                          # Streamlit 主程序
├── requirements.txt                # Python 依赖
├── .env.example                    # API 密钥配置示例
│
├── data/
│   ├── exhibits.json               # 展品数据库（35 件展品）
│   └── sessions.json               # 用户会话记录（运行时生成）
│
├── src/
│   ├── config.py                   # 系统配置
│   ├── data_loader.py              # 数据加载与预处理
│   ├── matching_engine.py          # TF-IDF 匹配引擎
│   └── llm_generator.py            # LLM 学习路径生成
│
├── prompts/
│   ├── learning_path_zh.txt        # 中文 Prompt 模板
│   └── learning_path_en.txt        # 英文 Prompt 模板
│
├── tools/
│   ├── import_exhibits.py          # 批量导入展品（自动补全）
│   └── add_exhibit.py              # 交互式录入新展品
│
├── templates/
│   ├── exhibits_minimal_template.csv   # Excel 最小输入模板
│   └── exhibits_minimal_template.json  # JSON 最小输入模板
│
├── assets/
│   └── images/                     # 展品图片（35 张 SVG 占位图，可替换为真实照片）
│
├── docs/
│   ├── DEPLOYMENT_GUIDE.md         # 🌐 线上部署指南（保姆级）
│   └── DATABASE_IMPORT_GUIDE.md    # 📦 数据库导入指南（保姆级）
│
└── figures/
    └── (论文用架构图存放处)
```

---

## 🎨 前端设计特色

- **航海主题配色**：深海蓝 + 古铜金 + 中国红印章
- **字体系统**：霞鹜文楷（中文展示）+ Cormorant Garamond（英文）+ Noto Sans SC（正文）
- **中国红印章**：匹配度以传统印章形式呈现
- **指南针 SVG**：动态装饰元素呼应导航主题
- **响应式布局**：桌面 / 平板 / 手机自适应

---

## 🖼️ 展品图片说明

**默认提供**：35 张定制的 SVG 矢量占位图（海事主题，匹配系统前端风格）

**替换为真实照片**：
1. 在你自己电脑上运行自动下载脚本：
   ```bash
   pip install playwright requests Pillow
   python -m playwright install chromium
   python tools/download_exhibit_images.py
   ```
2. 或手动下载图片，命名格式 `E01_main.jpg`，放入 `assets/images/` 目录
3. 重启 Streamlit 应用即可生效

> 💡 从 VM/服务器无法访问 720yun 反爬保护和中国境内博物馆网站，所以自动下载脚本必须在**你自己的电脑**上运行。

| 方式 | 适合场景 | 入口 |
|------|---------|------|
| **交互式录入** | 一两件 | `python tools/add_exhibit.py` |
| **Excel 批量录入** | 多件 | 编辑 `templates/exhibits_minimal_template.csv` → `python tools/import_exhibits.py templates/...csv` |
| **直接编辑 JSON** | 程序员 | 编辑 `data/exhibits.json` |

**最小输入**：只需 6 项（ID、名称、描述、类别、博物馆、标签），其他 12 项自动生成。

详见 `docs/DATABASE_IMPORT_GUIDE.md`

---

## 🌐 线上部署

**推荐方案**：Streamlit Cloud（免费，一键部署）

详见 `docs/DEPLOYMENT_GUIDE.md`

---

## 🔧 技术栈

- **前端**：Streamlit + 自定义 CSS + Google Fonts
- **匹配引擎**：scikit-learn TfidfVectorizer + cosine_similarity
- **中文分词**：jieba
- **LLM**：OpenAI / 通义千问 / 文心一言（可切换）
- **数据存储**：JSON 文件（轻量级原型）

---

## 📜 许可证

本项目为学术研究原型系统，仅供 ICET 2026 论文配套使用。

展品数据来源于「一馆一物说航海」大型数字联展，仅用于非商业学术研究。

---

## 📞 支持与反馈

- 部署问题：参考 `docs/DEPLOYMENT_GUIDE.md`
- 数据录入：参考 `docs/DATABASE_IMPORT_GUIDE.md`
- 系统架构：参考 `系统构建指南.md`（根目录）
