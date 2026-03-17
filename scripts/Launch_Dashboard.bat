
@echo off
title 奇点量化终端调试器
echo ============================================================
echo 🌌 [DEBUG]: 正在启动启动序列...
echo ============================================================

:: 强制进入目录
cd /d "C:\Users\huangruiran\ai_test"
echo [1/3] 当前目录: %CD%

:: 检查 Python 路径
set PYTHON_EXE=C:\Users\huangruiran\ai_test\.venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
    echo ❌ [错误]: 找不到虚拟环境路径: %PYTHON_EXE%
    pause
    exit
)
echo [2/3] 引擎路径: %PYTHON_EXE%

:: 尝试运行并捕获所有输出
echo [3/3] 正在点亮全息终端...
echo ------------------------------------------------------------
"%PYTHON_EXE%" dashboard.py 2>&1

echo ------------------------------------------------------------
echo 🏁 [FINISH]: 进程已结束。
echo 💡 [INFO]: 如果上面有报错，请截图或复制给 AI。
echo 💡 [INFO]: 窗口不会自动关闭，请手动关闭或按任意键。
pause
