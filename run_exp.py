import argparse
import time
import os
import re
from tqdm import tqdm
from pathlib import Path
from langchain.callbacks import get_openai_callback
from test_generated_code import test_generated_code, read_test_samples
from utils import extract_code_from_string, read_problem
from result import Result
import baseline.standard as standard
import baseline.standard2 as standard2
import baseline.chain_of_thought as cot
import baseline.progressive_hint as php
import baseline.reflexion as reflexion
from main import chain_of_agents
from Selector import Selector
from Summarizer import Summarizer
import random
import sys

# 加载记忆系统
from agentic_memory_rb.memory_system_rb import AgenticMemorySystemRB
proxy_url = 'http://127.0.0.1:7890'
os.environ['HTTP_PROXY'] = proxy_url
os.environ['HTTPS_PROXY'] = proxy_url
from agentic_memory_rb.memory_system_rb import MemoryNote

algorithms = {
    'standard': standard,
    'standard2': standard2,
    'chain_of_thought': cot,
    'cot': cot,
    'progressive_hint': php,
    'php': php,
    # 'solo_performance_prompting': ssp,
    # 'ssp': ssp,
    'reflexion': reflexion,
}

# 强制将标准输出和标准错误的编码设置为 utf-8
sys.stdout.reconfigure(encoding='utf-8')
# 如果有用到 stderr 最好也加上
sys.stderr.reconfigure(encoding='utf-8')


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
    parser.add_argument('--useab', type=str, default='true', help='if the system will use abstruct memory')
    parser.add_argument('--record',type=str, default='true', help='if the system will record and evolve memory')
    parser.add_argument('--evolve',type=str, default='true', help='if the system will record and evolve memory')
    parser.add_argument('--forget',type=str, default='true', help='if the system will forget memory')
    parser.add_argument('--check',type=str, default='true', help='if the system will check memory')

    parser.add_argument('--max_collaborate_nums', type=int, default=5, help='Number of max collaborations')
    args = parser.parse_args()
    args.algorithm = args.algorithm.lower()

    #catogory = args.dataset
    use_memory = True if args.use == 'true' else False
    use_ab_memory = True if args.useab == 'true' else False
    test_shift = True if use_ab_memory==True and use_memory==False else False
    record_memory = True if args.record == 'true' else False
    evolve = True if args.evolve == 'true' else False
    forget = True if args.forget == 'true' else False
    check = True if args.check == 'true' else False

    matched_problems = []
    for p in os.listdir(os.path.join('dataset', args.dataset)):
        if args.problem == p:
            matched_problems.append(p)
    total_num = len(matched_problems)
    if total_num == 0:
        print('No problem matched! Please check arguements.')
        exit(0)

    Path(args.log_dir).mkdir(parents=True, exist_ok=True)
    log_dir_name = f'run_{args.algorithm}_{args.dataset}_{str(round(time.time()))}'
    path = os.path.join(args.log_dir, log_dir_name)
    print(f'Save log to {path}')
    Path(path).mkdir(parents=True, exist_ok=True)

    # initialize with memory system
    memory_system = AgenticMemorySystemRB(
        dir_memory="memory",
        model_name='all-MiniLM-L6-v2',
        llm_name=args.model,
        category_abstruct_memory_num=1,
    )

    print("\nProcessing memory...\n")
    memory_system.process_memory('memory')
    print("\nMemory processed.\n")

    correct_num = 0
    ce_num = 0
    re_num = 0
    pbar = tqdm(total=len(matched_problems))
    current_num = 0
    selector=Selector(args.model)
    summarizer = Summarizer(args.model)
    for problem in matched_problems:
        comment_log_formemory=''
        problem_data = read_problem(args.dataset, problem)
        with get_openai_callback() as cb:
            if args.algorithm == 'chain_of_agents' or args.algorithm == 'coe':
                #catogory_str=selector.forward(problem_data['description'])
                #catogory=extract_or_assign_classification(catogory_str)
                catogory = args.dataset  # 直接使用数据集名称作为类别
                print(f'匹配到类型：{catogory}')
                mode = 1
                selected_memory_note=memory_system.select_memory_bycatogory_content(problem_data['description'],catogory,k=1,tolerance_level=0)
                if use_memory == False:
                    selected_memory_note = []
                if len(selected_memory_note)==0:
                    mode = 2
                    selected_memory_note=memory_system.select_abstruct_memory_bycatogory_distance(catogory,test_shift=test_shift,target_num=2,tolerance_level=2)
                if use_ab_memory == False:
                    selected_memory_note = []
                answer,comment_log_formemory,comment_log_forcode = chain_of_agents(
                    problem_data, 
                    args.max_collaborate_nums, 
                    model_name=args.model,
                    mode = mode,
                    memory_notes=selected_memory_note)
                
                time.sleep(10)
                
            else:
                if args.algorithm == "reflexion":
                    algorithm = algorithms[args.algorithm]
                    answer = algorithm.solve(problem_data,args.dataset, problem, model_name=args.model)
                else:
                    algorithm = algorithms[args.algorithm]
                    answer = algorithm.solve(problem_data, model_name=args.model)
            
            print('-' * 10 + 'Token usage' + '-' * 20)
            print(cb)
            print('-' * 25)
        # print("问题分配结果",answer)
        # print("总结内容：")
        # print(summary)


        with open(os.path.join(path, f'{problem}_original_answer.txt'), 'w', encoding='utf8',errors='ignore') as f:
            f.write(answer)
        
        code = extract_code_from_string(answer)
        code = code.replace('inrange', 'in range')
        
        
        with open(os.path.join(path, f'{problem}_generated_code.py'), 'w', encoding='utf8',errors='ignore') as f:
            f.write(code)

        with open('generated_code.py', 'w',encoding='utf8', errors='ignore') as f:
            f.write(code)

        with open(os.path.join(path, f'{problem}_analysis.txt'), 'w', encoding='utf8',errors='ignore') as f:
            f.write(comment_log_formemory)

        
        with open(os.path.join(path, f'{problem}_using_memory.txt'), 'w', encoding='utf8',errors='ignore') as f:
            f.write(f'use_memory: {use_memory}    use_abstruct_memory: {use_ab_memory}\n')
            if selected_memory_note != None and len(selected_memory_note) != 0:
                for note in selected_memory_note:
                    f.write(note.id)
                    f.write('\n')
                    f.write(note.memory_level)


        test_samples = read_test_samples(args.dataset, problem)
        with open(os.path.join(path, f'{problem}_test_log.txt'), 'w', encoding='utf8', errors='ignore') as f:
            result = test_generated_code(problem, test_samples, f)
        renew_summary = 'null'
        if result == Result.ACCEPT:
            summary = summarizer.forward(problem_data['description'],comment_log_formemory,True)
        elif result == Result.WRONG_ANSWER:
            summary = summarizer.forward(problem_data['description'],comment_log_formemory,False)
        else:
            summary = summarizer.forward(problem_data['description'],comment_log_forcode,False)

        if record_memory:
            existing_abstruct_memory=memory_system.select_abstruct_memory_bycatogory(catogory)
            if evolve and check:
                if len(existing_abstruct_memory)==0:
                    memory_system.add_abstruct_note(summary=summary,category=catogory)
                else:
                    renew_summary = memory_system.evolving_abstruct_memory(description=problem_data['description'],
                                                   summary=summary,
                                                   category=catogory)
            elif evolve and not check:
                if result == Result.ACCEPT:
                    if len(existing_abstruct_memory)==0:
                        memory_system.add_abstruct_note(summary=summary,category=catogory)
                    else:
                        renew_summary = memory_system.evolving_abstruct_memory(description=problem_data['description'],
                                                       summary=summary,
                                                       category=catogory)
            elif not evolve and check:
                memory_system.add_abstruct_note(summary=summary,category=catogory)
            
            else:
                if result == Result.ACCEPT:
                    memory_system.add_abstruct_note(summary=summary,category=catogory)

                
            if result == Result.ACCEPT:
                id=memory_system.add_note(description=problem_data['description'],
                               analysis=comment_log_formemory,
                               code=code,
                               category=catogory)
                if forget:
                    memory_system.scoring_memory_bynewnote(new_note_id=id, addscore_num=2)
                    memory_system.retrenching_memory_byscore(target_num=5)

        if result == Result.ACCEPT:
            correct_num += 1
        elif result == Result.COMPILE_ERROR:
            ce_num += 1
        elif result == Result.RUNTIME_ERROR:
            re_num += 1
        
        with open(os.path.join(path, f'{problem}_summary.txt'), 'w', encoding='utf8',errors='ignore') as f:
            f.write(summary)
        
        with open(os.path.join(path, f'{problem}_renew_summary.txt'), 'w', encoding='utf8',errors='ignore') as f:
            f.write(renew_summary)

        pbar.update()
        current_num += 1
        pbar.set_description(f'Accuracy: {correct_num / current_num * 100:.2f}% | Compile error: {ce_num / current_num * 100:.2f}% | Runtime error: {re_num / current_num * 100:.2f}%')

    print(f'Passed: {correct_num}/{total_num}')
    print(f'Accuracy: {correct_num / total_num * 100:.2f}%')
    print(f'Compile error: {ce_num / total_num * 100:.2f}%')
    print(f'Runtime error{re_num / total_num * 100:.2f}%')

if __name__ == '__main__':
    main()
