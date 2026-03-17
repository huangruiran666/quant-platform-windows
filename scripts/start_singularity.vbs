' 奇点量化 — 静默启动脚本（无控制台窗口）
' 双击运行，或放入开机启动文件夹实现自启
Dim python, script, cmd
python = "C:\Users\huangruiran\ai_test\.venv\Scripts\pythonw.exe"
script = "C:\Users\huangruiran\ai_test\gcp_scheduler_daemon.py"
cmd    = """" & python & """ """ & script & """"

CreateObject("WScript.Shell").Run cmd, 0, False
WScript.Echo "奇点量化守护进程已在后台启动。"
