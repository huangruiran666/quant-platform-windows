@echo off
chcp 65001 >nul
echo ========================================
echo   推送代码到 GitHub
echo ========================================
echo.

cd /d C:\Users\huangruiran\ai_test

echo 正在推送代码到 GitHub...
echo 第一次推送可能需要确认指纹，输入 yes 并回车
echo.

git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo   推送失败！
    echo ========================================
    echo.
    echo 请检查：
    echo 1. SSH 密钥已添加到 GitHub
    echo 2. 仓库已创建：https://github.com/huangruiran666/quant-platform
    echo.
) else (
    echo.
    echo ========================================
    echo   成功！
    echo ========================================
    echo.
    echo 仓库地址：https://github.com/huangruiran666/quant-platform
    echo.
)

pause
