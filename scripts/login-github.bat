@echo off
echo ========================================
echo   GitHub CLI 登录
echo ========================================
echo.
echo 即将打开浏览器，请用 GitHub 账号登录
echo.
echo 按任意键继续...
pause >nul
gh auth login --web
echo.
echo 登录完成后，运行以下命令检查：
echo   gh auth status
echo.
echo 然后查看你的仓库：
echo   gh repo list
echo.
pause
