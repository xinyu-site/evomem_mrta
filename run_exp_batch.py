import subprocess
import sys

# 强制将标准输出和标准错误的编码设置为 utf-8
sys.stdout.reconfigure(encoding='utf-8',errors='ignore')
# 如果有用到 stderr 最好也加上
sys.stderr.reconfigure(encoding='utf-8',errors='ignore')

experiments = []

# for i in range(5):  # 0到4
#     params = {}
#     params['dataset'] = 'ST_MR_TA'
#     params['problem'] = f'prob_{i}'  # 设置 problem
#     params['use'] = 'false'
#     params['useab'] = 'false'
#     params['record'] = 'true'
#     experiments.append(params)  # 添加到列表

# for i in range(5):  # 0到4
#     params = {}
#     params['dataset'] = 'ST_MR_TA'
#     params['problem'] = f'prob_{i}'  # 设置 problem
#     params['use'] = 'false'
#     params['useab'] = 'true'
#     params['record'] = 'true'
#     experiments.append(params)  # 添加到列表

# for i in range(5):  # 0到4
#     params = {}
#     params['dataset'] = 'MT_MR_IA'
#     params['problem'] = f'prob_{i}'  # 设置 problem
#     params['use'] = 'false'
#     params['useab'] = 'false'
#     params['record'] = 'true'
#     experiments.append(params)  # 添加到列表

for i in range(5):  # 0到4
    params = {}
    params['dataset'] = 'MT_MR_IA'
    params['problem'] = f'prob_{i}'  # 设置 problem
    params['use'] = 'false'
    params['useab'] = 'true'
    params['record'] = 'true'
    experiments.append(params)  # 添加到列表

for i in range(5):  # 0到4
    params = {}
    params['dataset'] = 'MT_MR_TA'
    params['problem'] = f'prob_{i}'  # 设置 problem
    params['use'] = 'false'
    params['useab'] = 'false'
    params['record'] = 'true'
    experiments.append(params)  # 添加到列表

for i in range(5):  # 0到4
    params = {}
    params['dataset'] = 'MT_MR_TA'
    params['problem'] = f'prob_{i}'  # 设置 problem
    params['use'] = 'false'
    params['useab'] = 'true'
    params['record'] = 'true'
    experiments.append(params)  # 添加到列表

# 运行所有实验
success_count = 0
fail_count = 0

for i, params in enumerate(experiments, 1):
    print(f"\n{'='*60}")
    print(f"开始运行第 {i}/{len(experiments)} 个实验")
    print(f"参数: {params}")
    
    try:
        # 构建命令
        cmd = ['python', 'run_exp.py']
        for key, value in params.items():
            cmd.append(f'--{key}')
            cmd.append(str(value))
        
        print(f"命令: {' '.join(cmd)}")
        
        # 运行命令，设置超时为0.5小时（1800秒）
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=1800
        )
        
        # 检查返回码
        if result.returncode == 0:
            print(f"✅ 实验 {i} 成功完成")
            success_count += 1
            
            # 可选：打印部分输出
            if result.stdout:
                print("输出预览:", result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
        else:
            print(f"❌ 实验 {i} 失败，返回码: {result.returncode}")
            fail_count += 1
            
            if result.stderr:
                print("错误信息:")
                print(result.stderr)
                
    except subprocess.TimeoutExpired:
        print(f"⏰ 实验 {i} 超时（超过1小时）")
        fail_count += 1
        
    except FileNotFoundError:
        print(f"❌ 错误：找不到 run_exp.py 文件或 Python 解释器")
        print("请确保：")
        print("1. run_exp.py 在当前目录")
        print("2. Python 已正确安装")
        fail_count += 1
        
    except Exception as e:
        print(f"⚠️  实验 {i} 发生意外错误: {type(e).__name__}")
        print(f"错误详情: {str(e)}")
        fail_count += 1
        
    finally:
        print(f"第 {i} 个实验处理完成")
        print('='*60)

# 打印最终统计
print(f"\n{'='*60}")
print("所有实验运行完毕！")
print(f"✅ 成功: {success_count} 个")
print(f"❌ 失败: {fail_count} 个")
print(f"📊 总计: {len(experiments)} 个")
print('='*60)

# 如果有失败，以非零退出码退出
if fail_count > 0:
    sys.exit(1)