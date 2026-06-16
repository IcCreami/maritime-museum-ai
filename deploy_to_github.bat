@echo off
chcp 65001 >nul
REM ============================================================
REM  AI 博物馆推荐系统 - GitHub 推送 + 部署准备脚本
REM  使用方法：双击运行即可
REM ============================================================

echo.
echo ============================================================
echo   AI 博物馆推荐系统 - GitHub 部署脚本
echo ============================================================
echo.

REM 检查 git 是否安装
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [错误] 未检测到 git，请先安装 git:
    echo   https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo [1/4] 检查 git 环境... OK
echo.

REM 进入项目目录
cd /d "%~dp0"
echo [2/4] 进入项目目录: %CD%
echo.

REM 删除旧的 .git 文件夹（如果有）
if exist .git (
    echo [清理] 删除旧的 .git 文件夹...
    rmdir /s /q .git 2>nul
)

REM 初始化 git 仓库
echo [3/4] 初始化 git 仓库...
git init
git branch -M main

REM 添加文件（.gitignore 会自动忽略 .env 等敏感文件）
echo.
echo [3/4] 添加文件（敏感文件 .env 会被自动忽略）...
git add .

echo.
echo [3/4] 待提交文件预览（前 20 个）:
git status --short | more

echo.
echo [4/4] 提交代码...
git commit -m "Initial commit: AI museum recommendation system"

echo.
echo ============================================================
echo   本地 git 仓库准备完成！
echo ============================================================
echo.
echo 接下来请在浏览器中完成以下步骤：
echo.
echo 步骤 A: 在 GitHub 创建仓库
echo   1. 打开 https://github.com/new
echo   2. Repository name: maritime-museum-ai
echo   3. 选择 Public
echo   4. 不要勾选任何"Add file"选项
echo   5. 点击 Create repository
echo   6. 复制仓库的 HTTPS 地址（形如 https://github.com/你的用户名/maritime-museum-ai.git）
echo.
echo 步骤 B: 推送代码（复制下面的命令，替换 URL）
echo   git remote add origin https://github.com/你的用户名/maritime-museum-ai.git
echo   git push -u origin main
echo.
echo 步骤 C: 部署到 Streamlit Cloud
echo   1. 打开 https://share.streamlit.io
echo   2. 用 GitHub 登录
echo   3. New app -^> 选择 maritime-museum-ai 仓库
echo   4. Main file path: app.py
echo   5. Advanced settings -^> Secrets 里粘贴 API Key（见下方）
echo.
echo ============================================================
echo   Secrets 配置（复制到 Streamlit Cloud 的 Secrets 框）:
echo ============================================================
echo.
echo DASHSCOPE_API_KEY = "sk-ws-H.（你的完整API密钥）"
echo LLM_PROVIDER = "qwen"
echo DASHSCOPE_MODEL = "qwen-plus"
echo.
echo ============================================================
echo.
pause
