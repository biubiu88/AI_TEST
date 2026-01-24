@echo off
setlocal enabledelayedexpansion

echo === Git Push Script ===

:: 检查是否提供了提交信息参数
if "%~1"=="" (
    set /p msg="请输入提交信息 (Commit Message): "
) else (
    set msg=%~1
)

:: 如果用户没有输入任何内容，设置默认信息
if "!msg!"=="" (
    set msg="auto: update code"
)

echo.
echo 正在添加更改...
git add .

echo 正在提交变更: !msg!
git commit -m "!msg!"

echo 正在推送到 GitHub...
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo [错误] 推送失败，请检查网络或冲突。
) else (
    echo.
    echo [成功] 代码已成功推送到 GitHub。
)

pause
