@echo off
chcp 65001 >nul
echo ========================================
echo   部署到 Railway
echo ========================================
echo.

cd /d C:\Users\huangruiran\ai_test

echo 步骤 1: 打开浏览器访问 https://railway.app
echo 步骤 2: 用 GitHub 账号登录
echo 步骤 3: 点击 "New Project"
echo 步骤 4: 选择 "Deploy from GitHub repo"
echo 步骤 5: 选择 "QUANT-PLATFORM-WINDOWS"
echo.
echo 按任意键打开 Railway...
pause >nul
start https://railway.app
echo.
echo ========================================
echo   部署完成后，网站地址类似：
echo   https://quant-platform-windows-production.up.railway.app
echo ========================================
echo.
pause
