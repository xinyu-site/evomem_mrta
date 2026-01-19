import subprocess
import sys
import time
from collections import deque
import random

# 强制将标准输出和标准错误的编码设置为 utf-8
sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

# --- 1. 定义实验参数列表 ---
base_experiments = []

num_problems_per_dataset = 25
random_order = False

# 这里保留你原来的逻辑，生成 15 个任务
datasets_configs = [
    {'dataset': 'MT_MR_TA', 'useab': 'true','use': 'true','record': 'true','check':'true','evolve':'true','forget':'true'},
    {'dataset': 'MT_SR_TA', 'useab': 'true','use': 'true','record': 'true','check':'true','evolve':'true','forget':'true'},
    {'dataset': 'ST_SR_IA', 'useab': 'true','use': 'true','record': 'true','check':'true','evolve':'true','forget':'true'},
    {'dataset': 'MT_MR_IA', 'useab': 'true','use': 'true','record': 'true','check':'true','evolve':'true','forget':'true'},
    {'dataset': 'ST_SR_TA', 'useab': 'true','use': 'true','record': 'true','check':'true','evolve':'true','forget':'true'},
    {'dataset': 'ST_MR_TA', 'useab': 'true','use': 'true','record': 'true','check':'true','evolve':'true','forget':'true'},
    {'dataset': 'ST_MR_IA', 'useab': 'true','use': 'true','record': 'true','check':'true','evolve':'true','forget':'true'},
    {'dataset': 'MT_SR_IA', 'useab': 'true','use': 'true','record': 'true','check':'true','evolve':'true','forget':'true'},
]

num_problems_per_dataset = 25 if num_problems_per_dataset>25 else num_problems_per_dataset
for config in datasets_configs:
    for i in range(num_problems_per_dataset):
        params = {
            'dataset': config['dataset'],
            'problem': f'prob_{i}',
            'use': config['use'],
            'useab': config['useab'],
            'record': config['record'],
            'check': config['check'],
            'evolve': config['evolve'],
            'forget': config['forget'],
            'retry_count': 0  # 额外记录重试次数，方便观察
        }
        base_experiments.append(params)

if random_order:
    random.shuffle(base_experiments)

# --- 2. 转换为队列 ---
# 使用 deque 方便从左侧弹出，从右侧追加
task_queue = deque(base_experiments)

success_count = 0
total_initial_tasks = len(task_queue)

print(f"🚀 脚本启动，总计任务数: {total_initial_tasks}")
print(f"💡 失败的任务会自动移动到队列末尾，直到成功为止。按 Ctrl+C 可手动停止。")

# --- 3. 循环执行任务 ---
try:
    while task_queue:
        # 获取当前任务
        params = task_queue.popleft()
        
        current_task_info = f"[{params['dataset']}-{params['problem']}-ab{params['useab']}]"
        print(f"\n{'='*60}")
        print(f"正在运行任务: {current_task_info}")
        if params['retry_count'] > 0:
            print(f"🔄 这是该任务的第 {params['retry_count']} 次重试")
        print(f"待处理任务剩余: {len(task_queue) + 1}") # +1 是因为当前任务刚弹出来
        
        try:
            # 构建命令
            cmd = ['python', 'run_exp.py']
            for key, value in params.items():
                if key == 'retry_count': continue # 不把重试次数传给子脚本
                cmd.append(f'--{key}')
                cmd.append(str(value))
            start_time = time.time()
            # 运行命令，设置超时 1800 秒
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=1800,
                encoding='utf-8',     # 显式指定用 utf-8 解码子进程的输出
                errors='ignore',      # 如果遇到无法解析的字节，忽略它，防止崩溃
            )
            
            # 检查返回码
            if result.returncode == 0:
                stop_time = time.time()
                timerecord = stop_time-start_time
                print(f"✅ {current_task_info} 成功完成")
                success_count += 1
                # 打印部分输出
                if result.stdout:
                    print("输出预览:", result.stdout[:150].replace('\n', ' ') + "...")
                dataset_str = params['dataset']
                problem_str = params['problem']
                with open('batch_result.txt', 'a',encoding='utf-8',errors='ignore') as f:
                    f.write(f'dataset: {dataset_str}   problem: {problem_str}  time:{timerecord}\n')
            else:
                print(f"❌ {current_task_info} 失败 (返回码: {result.returncode})")
                if result.stderr:
                    print(f"错误摘要: {result.stderr[-200:].strip()}")
                
                # 失败逻辑：增加重试计数并放回队尾
                params['retry_count'] += 1
                task_queue.append(params)
                print(f"🔁 已将任务重新放入队列末尾")

        except subprocess.TimeoutExpired:
            print(f"⏰ {current_task_info} 超时（超过0.5小时）")
            params['retry_count'] += 1
            task_queue.append(params)
            print(f"🔁 已将任务重新放入队列末尾")
            
        except Exception as e:
            print(f"⚠️ {current_task_info} 发生异常: {type(e).__name__}: {e}")
            params['retry_count'] += 1
            task_queue.append(params)
            print(f"🔁 已将任务重新放入队列末尾")
        
        # 任务之间的短暂间隔，防止过快循环导致 CPU 飙升
        time.sleep(1)

except KeyboardInterrupt:
    print(f"\n\n🛑 用户手动停止了脚本")

# --- 4. 最终统计 ---
print(f"\n{'='*60}")
print("运行结束统计：")
print(f"✅ 成功完成: {success_count} / {total_initial_tasks}")
print(f"📋 剩余未完成: {len(task_queue)}")
if task_queue:
    print("未完成的任务列表预览:")
    for t in list(task_queue)[:5]:
        print(f"  - {t['dataset']} {t['problem']} (重试次数: {t['retry_count']})")
print('='*60)