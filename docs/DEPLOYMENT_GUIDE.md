# 🧭 线上部署指南（小白保姆级教程）

> 本指南假设你**从未部署过任何网站**，跟着做就能把系统放到互联网上，任何人都能通过链接访问。

---

## 📚 目录

1. [部署方案选择](#1-部署方案选择)
2. [方案 A：Streamlit Cloud（强烈推荐 - 免费最简单）](#2-方案-astreamlit-cloud强烈推荐---免费最简单)
3. [方案 B：Hugging Face Spaces（国内访问稍好）](#3-方案-bhugging-face-spaces国内访问稍好)
4. [方案 C：自己的服务器（阿里云 / 腾讯云）](#4-方案-c自己的服务器阿里云--腾讯云)
5. [API 密钥申请与配置](#5-api-密钥申请与配置)
6. [常见问题 FAQ](#6-常见问题-faq)

---

## 1. 部署方案选择

| 方案 | 费用 | 难度 | 国内访问速度 | 推荐度 |
|------|------|------|-------------|-------|
| **Streamlit Cloud** | 免费 | ⭐ 极易 | 一般 | ⭐⭐⭐⭐⭐ |
| Hugging Face Spaces | 免费 | ⭐⭐ 简单 | 较慢 | ⭐⭐⭐ |
| 阿里云 / 腾讯云 | 付费（约 50 元/月起） | ⭐⭐⭐⭐ 较难 | 快 | ⭐⭐⭐ |

**小白首选：Streamlit Cloud**。只要会上传代码到 GitHub，点几下鼠标就能部署。

---

## 2. 方案 A：Streamlit Cloud（强烈推荐 - 免费最简单）

### 2.1 你需要准备什么？

- ✅ 一个 **GitHub 账号**（没有的话去 https://github.com 免费注册）
- ✅ 你的系统代码已经上传到这个 GitHub 仓库
- ✅ 一个 **Streamlit 账号**（去 https://streamlit.io/cloud 用 GitHub 一键登录）

### 2.2 第一步：把代码上传到 GitHub

如果你已经会用 GitHub，跳过这一段。如果不会，按下面步骤来：

**① 安装 Git（如果没装）**
- Windows 用户去 https://git-scm.com/download/win 下载并安装
- 安装时所有选项保持默认即可

**② 在 GitHub 创建新仓库**
- 登录 GitHub → 右上角 **+** → **New repository**
- 仓库名（Repository name）：`museum-recommendation`
- 选 **Public**（Streamlit Cloud 只支持公开仓库）
- 点 **Create repository**

**③ 把本地代码推送上去**

打开命令提示符（Windows 按 Win+R 输入 `cmd`），执行：

```bash
# 进入你的项目文件夹（按实际路径替换）
cd C:\Users\你的用户名\Desktop\ICE\AI-Museum-Recommendation-System

# 初始化 Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: AI Museum Recommendation System"

# 连接到你的 GitHub 仓库（把"你的用户名"替换掉）
git remote add origin https://github.com/你的用户名/museum-recommendation.git

# 推送
git branch -M main
git push -u origin main
```

**④ 确认 `.env` 文件没有被上传**

```bash
git status
```

应该看不到 `.env` 文件。如果看到了，说明 `.gitignore` 配置不对，执行：

```bash
git rm --cached .env
git commit -m "Remove .env from tracking"
git push
```

### 2.3 第二步：在 Streamlit Cloud 部署

1. 打开 https://share.streamlit.io 用 GitHub 登录
2. 点右上角 **New app**
3. 填写表单：
   - **Repository**：选你的 `museum-recommendation`
   - **Branch**：`main`
   - **Main file path**：`app.py`
4. 点开 **Advanced settings**（重要！）
   - 在 "Secrets" 文本框里粘贴你的 API 密钥配置（见下方）
5. 点 **Deploy!**

**Secrets 框里填的内容（按你使用的 LLM 填）：**

```toml
# 如果用 OpenAI：
OPENAI_API_KEY = "sk-你的真实密钥"
LLM_PROVIDER = "openai"

# 如果用通义千问：
DASHSCOPE_API_KEY = "sk-你的真实密钥"
LLM_PROVIDER = "qwen"

# 如果用文心一言：
BAIDU_API_KEY = "你的key"
BAIDU_SECRET_KEY = "你的secret"
LLM_PROVIDER = "ernie"
```

等待 1~3 分钟，部署完成后会给你一个链接：
`https://museum-recommendation-xxxx.streamlit.app`

**把这个链接分享给同学就能访问了！** 🎉

### 2.4 更新代码怎么办？

本地修改完代码后：

```bash
git add .
git commit -m "更新说明"
git push
```

Streamlit Cloud 会自动检测更新并重新部署，通常 1 分钟内生效。

---

## 3. 方案 B：Hugging Face Spaces（国内访问稍好）

### 3.1 准备
- 注册 Hugging Face 账号：https://huggingface.co/join

### 3.2 创建 Space

1. 登录后点左上角头像 → **New Space**
2. 填写：
   - Space name：`museum-recommendation`
   - SDK：选 **Streamlit**
   - Visibility：**Public**
3. 点 **Create Space**

### 3.3 上传代码

Hugging Face 会给你一个 Git 仓库地址。操作和 GitHub 完全一样：

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://huggingface.co/spaces/你的用户名/museum-recommendation
git push -u origin main
```

### 3.4 配置 API 密钥

在 Space 页面 → **Settings** → **Repository secrets**，添加：
- `OPENAI_API_KEY`（或对应的其他密钥）

---

## 4. 方案 C：自己的服务器（阿里云 / 腾讯云）

适合有服务器或愿意购买的用户。国内访问最快。

### 4.1 购买服务器（以阿里云为例）

- 访问 https://www.aliyun.com
- 注册账号并完成实名认证
- 购买 **ECS 云服务器**：
  - 配置：2核 2G 内存即可
  - 系统：Ubuntu 22.04
  - 地区：上海 / 北京（国内访问快）
- 记下公网 IP 地址（假设 `47.100.xx.xx`）

### 4.2 连接服务器

Windows 用户推荐使用 [MobaXterm](https://mobaxterm.mobatek.net/) 或 Windows Terminal 的 SSH：

```bash
ssh root@47.100.xx.xx
```

输入密码登录。

### 4.3 在服务器上安装环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 和 pip
sudo apt install -y python3 python3-pip python3-venv git

# 克隆你的代码（把 URL 换成你的）
cd /opt
sudo git clone https://github.com/你的用户名/museum-recommendation.git
cd museum-recommendation

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4.4 配置 API 密钥

```bash
cp .env.example .env
nano .env    # 编辑，填入你的真实 API 密钥
# 按 Ctrl+O 保存，Ctrl+X 退出
```

### 4.5 测试运行

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

在浏览器访问 `http://47.100.xx.xx:8501` 应该能看到系统。

### 4.6 让程序在后台持续运行

按 Ctrl+C 停止测试。用 `systemd` 让程序在后台一直运行：

```bash
sudo nano /etc/systemd/system/museum.service
```

粘贴以下内容（注意替换用户名和路径）：

```ini
[Unit]
Description=Museum Recommendation System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/museum-recommendation
Environment="PATH=/opt/museum-recommendation/venv/bin"
ExecStart=/opt/museum-recommendation/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable museum
sudo systemctl start museum
sudo systemctl status museum   # 应该看到 active (running)
```

### 4.7 配置域名（可选）

如果你有域名（如 `museum.yoursite.com`），用 Nginx 反向代理：

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

创建配置：

```bash
sudo nano /etc/nginx/sites-available/museum
```

```nginx
server {
    listen 80;
    server_name museum.yoursite.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

启用：

```bash
sudo ln -s /etc/nginx/sites-available/museum /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 申请 HTTPS 证书（免费）
sudo certbot --nginx -d museum.yoursite.com
```

---

## 5. API 密钥申请与配置

### 5.1 OpenAI（GPT-4o-mini）

1. 访问 https://platform.openai.com/signup 注册
2. 进入 https://platform.openai.com/api-keys
3. 点 **Create new secret key**，复制保存
4. **注意**：OpenAI API 需要绑定国际信用卡，并可能需科学上网

### 5.2 通义千问（推荐国内用户）

1. 访问 https://dashscope.console.aliyun.com/
2. 用阿里云账号登录
3. 开通 DashScope 服务
4. 在 **API Key 管理** 创建新 Key
5. 免费额度足够原型测试

### 5.3 文心一言

1. 访问 https://console.bce.baidu.com
2. 注册百度智能云账号
3. 搜索"文心一言"，开通 API 服务
4. 创建应用获取 API Key 和 Secret Key

---

## 6. 常见问题 FAQ

### Q1: 部署后页面空白或报错？
- 检查 `app.py` 是否在仓库根目录
- 检查 Streamlit Cloud 的 Logs 页面（Deploy 页面的右下角）
- 常见错误：依赖没装全 → 检查 `requirements.txt`

### Q2: LLM 返回空内容或报错？
- 检查 API 密钥是否正确配置
- 检查 API 账户余额
- 临时使用 fallback：不配置任何 API Key 时，系统会自动使用占位文本演示

### Q3: 国内访问 Streamlit Cloud 很慢？
- 考虑用 Hugging Face Spaces 或阿里云服务器
- 或者使用 GitHub Pages 部署静态文档 + 阿里云服务器运行主系统

### Q4: 展品图片没显示？
- 图片应放在 `assets/images/` 目录
- 文件名要与 `exhibits.json` 中的 `image_path` 完全一致（区分大小写）
- 没有图片时，系统会显示占位图标 🏺

### Q5: 想修改系统标题或介绍文案？
- 编辑 `src/config.py` 中的 `SYSTEM_TITLE_ZH`、`SYSTEM_SUBTITLE_ZH` 等
- 修改后 `git push`，自动部署

### Q6: 怎么知道系统运行是否正常？
- 访问你的线上地址，输入测试数据：
  - 专业：航海技术
  - 课程：船舶导航系统
  - 关键词：罗盘 天文导航
- 应该看到 Top-3 推荐和（若有 API Key）AI 生成的学习路径

---

## 📞 需要帮助？

- Streamlit 官方文档：https://docs.streamlit.io
- Streamlit Cloud 帮助：https://docs.streamlit.io/streamlit-community-cloud
- 本项目问题：查看 `docs/` 文件夹下的其他文档

---

> **下一步**：部署完成后，把这个链接发给你要调研的同学，开始收集问卷数据！📊
