@echo off
echo ========================================
echo   奇点量化平台 - 一键部署脚本
echo ========================================
echo.

REM 检查 Railway CLI
echo [1/4] 检查 Railway CLI...
where railway >nul 2>nul
if %errorlevel% neq 0 (
    echo 正在安装 Railway CLI...
    npm install -g @railway/cli
) else (
    echo Railway CLI 已安装
)
echo.

REM 登录
echo [2/4] 登录 Railway...
echo 按任意键打开浏览器登录
railway login
echo.

REM 初始化项目
echo [3/4] 初始化项目...
railway init
echo.

REM 部署
echo [4/4] 开始部署...
railway up
echo.

echo ========================================
echo   部署完成！
echo ========================================
echo.
echo 运行以下命令绑定域名：
echo   railway domain
echo.
pause
