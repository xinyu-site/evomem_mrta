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

echo 开始顺序执行Python脚本...
echo ========================================

set "datasets=ST_SR_IA MT_SR_IA ST_SR_TA ST_MR_IA MT_MR_IA MT_MR_TA MT_SR_TA ST_MR_TA"
set "error_count=0"

for %%d in (%datasets%) do (
    echo 正在处理数据集: %%d
    echo ========================================
    
    python run_exp.py --dataset %%d
    
    if errorlevel 1 (
        echo 警告: 执行 %%d 失败，跳过继续执行下一个
        set /a error_count+=1
        echo 错误计数: !error_count!
    ) else (
        echo 数据集 %%d 执行成功！
    )
    
    echo.
    timeout /t 2 /nobreak > nul
    echo ========================================
    echo.
)

echo ========================================
if !error_count! equ 0 (
    echo 所有脚本执行成功！
) else (
    echo 执行完成，共有 !error_count! 个数据集执行失败
)
echo ========================================
pause