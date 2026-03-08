@echo off
chcp 65001 >nul
echo ========================================
echo   GitHub 登录 + 创建仓库
echo ========================================
echo.

cd /d C:\Users\huangruiran\ai_test

echo [1/3] 登录 GitHub...
echo 按任意键打开浏览器登录
pause >nul
gh auth login --web

echo.
echo [2/3] 检查登录状态...
gh auth status

echo.
echo [3/3] 创建仓库并推送...
gh repo create quant-platform --public --description "Singularity Quant Trading Platform" --source . --push

echo.
echo ========================================
echo   完成！
echo ========================================
echo.
echo 仓库地址：https://github.com/huangruiran666/quant-platform
echo.
pause
