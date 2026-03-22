@echo off
chcp 65001 >nul
echo.
echo   ✧ 正在安装「每日玄学」✧
echo.

set DIR=%USERPROFILE%\daily-mystic

mkdir "%DIR%" 2>nul
mkdir "%DIR%\static" 2>nul

:: 复制文件
copy /Y "%~dp0app.py" "%DIR%\" >nul
copy /Y "%~dp0requirements.txt" "%DIR%\" >nul
copy /Y "%~dp0popup_win.py" "%DIR%\popup.py" >nul
copy /Y "%~dp0static\index.html" "%DIR%\static\" >nul

:: 安装依赖
echo   → 安装依赖…
pip install cnlunar flask pywebview >nul 2>&1

:: 创建桌面快捷方式
echo   → 创建桌面快捷方式…
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%USERPROFILE%\Desktop\每日玄学.lnk'); $sc.TargetPath = 'pythonw'; $sc.Arguments = '%DIR%\popup.py'; $sc.WorkingDirectory = '%DIR%'; $sc.Description = '每日玄学'; $sc.Save()"

echo.
echo   ✓ 安装完成！
echo.
echo   双击桌面上的「每日玄学」快捷方式即可使用
echo   首次打开请点击「命盘」输入你的生辰
echo.
pause
