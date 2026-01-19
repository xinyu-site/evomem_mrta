@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo 正在激活conda环境...
call conda activate coe

if errorlevel 1 (
    echo ========================================
    echo 错误: 无法激活conda环境 'coe'
    echo 请检查:
    echo 1. 是否已安装conda
    echo 2. 环境名是否正确
    echo 3. 是否有管理员权限
    echo ========================================
    pause
    exit /b 1
)

echo 环境激活成功！
python --version

python run_exp.py --dataset ST_MR_TA