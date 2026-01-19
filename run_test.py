import argparse
import time
import os
import re
#from tqdm import tqdm
from pathlib import Path
#from langchain.callbacks import get_openai_callback
#from test_generated_code import test_generated_code, read_test_samples
#from utils import extract_code_from_string, read_problem
#from result import Result
# import baseline.standard as standard
# import baseline.standard2 as standard2
# import baseline.chain_of_thought as cot
# import baseline.progressive_hint as php
# import baseline.reflexion as reflexion
#from main import chain_of_agents
#from Selector import Selector
#import random

# # 加载记忆系统
# from agentic_memory_rb.memory_system_rb import AgenticMemorySystemRB
# proxy_url = 'http://127.0.0.1:7890'
# os.environ['HTTP_PROXY'] = proxy_url
# os.environ['HTTPS_PROXY'] = proxy_url
# from agentic_memory_rb.memory_system_rb import MemoryNote

# algorithms = {
#     'standard': standard,
#     'standard2': standard2,
#     'chain_of_thought': cot,
#     'cot': cot,
#     'progressive_hint': php,
#     'php': php,
#     # 'solo_performance_prompting': ssp,
#     # 'ssp': ssp,
#     'reflexion': reflexion,
# }


def extract_or_assign_classification(text):
    """
    从文段中提取分类字符串，如果没有找到则随机分配一个
    
    参数:
        text: 输入文本字符串
        
    返回:
        str: 提取到或随机分配的分类字符串
    """
    # 所有可能的分类
    all_classes = [
        "ST_SR_IA", "ST_MR_IA", "MT_SR_IA", "MT_MR_IA",
        "ST_SR_TA", "ST_MR_TA", "MT_SR_TA", "MT_MR_TA"
    ]
    
    # 方法1: 使用正则表达式提取
    pattern = r"\b(?:ST|MT)_(?:SR|MR)_(?:IA|TA)\b"
    found = re.findall(pattern, text)
    
    # 如果有找到匹配，返回第一个（或可以根据需要调整）
    if found:
        return found[0]  # 返回第一个匹配项
        # 或者 return list(set(found))  # 返回去重后的所有匹配项
    
    # 如果没有找到匹配，随机分配一个
    else:
        return random.choice(all_classes)

def main():
    parser = argparse.ArgumentParser(description='Generate and test code.')
    parser.add_argument('--dataset', type=str, default='mix_dataset', help='Dataset name, "LPWP" or "ComplexOR"')
    parser.add_argument('--problem', type=str, default='prob_.*', help='Problem name')
    parser.add_argument('--algorithm', type=str, default='coe', help='Algorithm name')
    parser.add_argument('--log_dir', type=str, default='log', help='The directory of log')
    parser.add_argument('--model', type=str, default='deepseek-ai/DeepSeek-V3', help='Base large language model')
    parser.add_argument('--use', type=str, default='true', help='if the system will use memory')
    parser.add_argument('--useab', type=str, default='true', help='if the system will use memory')
    parser.add_argument('--record',type=str, default='true', help='if the system will record and evolve memory')
    parser.add_argument('--max_collaborate_nums', type=int, default=5, help='Number of max collaborations')
    args = parser.parse_args()
    args.algorithm = args.algorithm.lower()

    #catogory = args.dataset
    use_memory = True if args.use == 'true' else False
    record_memory = True if args.use == 'true' else False

    matched_problems = []
    for p in os.listdir(os.path.join('dataset', args.dataset)):
        if re.match(args.problem, p):
            matched_problems.append(p)
    total_num = len(matched_problems)
    print(f'find {total_num}')
    if total_num == 0:
        print('No problem matched! Please check arguements.')
        exit(0)

if __name__ == '__main__':
    main()