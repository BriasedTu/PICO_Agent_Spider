@echo off
setlocal enabledelayedexpansion

:: 设置要处理的文件夹路径
set "folderPath="

:: 检查文件夹是否存在
if not exist "%folderPath%" (
    echo 文件夹不存在: %folderPath%
    pause
    exit /b
)

echo 正在处理文件夹: %folderPath%
echo.

:: 计数器初始化
set kept=0
set deleted=0

:: 遍历文件夹中的所有文件
for %%F in ("%folderPath%\*") do (
    set "fileName=%%~nxF"
    
    :: 使用安全的方式检查文件名（避免管道解析问题）
    echo "!fileName!" | findstr /i /c:"guideline" /c:"guidance" >nul
    if !errorlevel! equ 0 (
        set /a kept+=1
        echo 保留: "!fileName!"
    ) else (
        set /a deleted+=1
        echo 删除: "!fileName!"
        del /f /q "%%F"
    )
)

echo.
echo 处理完成:
echo 保留的文件数: %kept%
echo 删除的文件数: %deleted%
pause