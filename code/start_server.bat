@echo off
@cd /d"D:\demooo\code"
chcp 65001 >nul
echo ============================================
echo        启动 Django 开发服务器
echo ============================================
echo.
echo 当前目录: %cd%
echo.

:: 检查 Python 是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查是否已安装 Django
python -c "import django; print('Django 版本:', django.VERSION)" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装 Django...
    pip install django
    if %errorlevel% neq 0 (
        echo 错误: 安装 Django 失败
        pause
        exit /b 1
    )
)

:: 启动开发服务器
echo 正在启动开发服务器...
echo.
echo 访问地址:
echo   主游戏: http://localhost:8000/
echo   图片测试: http://localhost:8000/test/
echo.
echo 按 Ctrl+C 停止服务器
echo ============================================
echo.

python manage.py runserver 8000

pause