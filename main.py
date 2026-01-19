import os
import json
import numpy as np
from comment import Comment
from Orchestrator import Orchestrator
from reducer import Reducer
from agents import (
    Modeler, 
    Developer,
    Identifier,
)
from comment_pool import CommentPool
from utils import extract_code_from_string
import re

from agentic_memory_rb.memory_system_rb import MemoryNote
from typing import Optional

def chain_of_agents(problem, 
                     max_collaborate_nums, 
                     model_name,
                     mode,
                     memory_notes:Optional[list[MemoryNote]]=None):
    """Run Chain of agents pipeline
    
    Args:
        problem: a dict of problem_description and code_example.
    
    Return:
        code: code of problem
    """
    #print(memory_notes[0].problem_description if memory_notes else "No memory notes provided.")
    if mode==1:
        example_problem_list = [note.problem_description for note in memory_notes] if memory_notes else []
        example_output_list = [note.problem_analysis for note in memory_notes] if memory_notes else []
        example_code_list = [note.code for note in memory_notes] if memory_notes else []
    else:
        example_summary_list = [note.resolve_summary for note in memory_notes] if memory_notes else []
    
    if mode==1:
        all_agents = [
            Identifier(model_name,example_problem_list=example_problem_list,
                   example_output_list=example_output_list,example_summary_list=[]),
            Modeler(model_name),
            Developer(model_name, example_problem_list=example_problem_list,
                  example_code_list=example_code_list),
        ]
    else:
         all_agents = [
            Identifier(model_name,[],[],example_summary_list=example_summary_list),
            Modeler(model_name),
            Developer(model_name,[],[]),
        ]

    num_agents = len(all_agents)
    reducer = Reducer(model_name)
    #summarizer = Summarizer(model_name)
    comment_pool = CommentPool(all_agents, visible_matrix=np.ones((num_agents, num_agents))) #可见矩阵全1即所有专家都可见其他评论
    orchestrator = Orchestrator(model_name)

    comment_log = open('comment_log.txt', 'w',encoding='utf-8',errors='ignore')
    comment_log_formemory = ''

    for i in range(max_collaborate_nums):
        next_agent = orchestrator.forward(problem, comment_pool, max_collaborate_nums)
        print(f'Choose next agent: {next_agent.name}')
        comment_log.write(f'--------- Round {i+1} ----------\n')
        comment_log.write(f'Agent {next_agent.name} comment:\n')
        #comment_log_formemory += f'Agent {next_agent.name} comment:\n'
        comment_text = next_agent.forward(problem, comment_pool)
        print(f'Given comment:\n{comment_text}')
        comment_log.write(f'{comment_text}\n\n')
        if next_agent.name == 'Identifier':
            comment_log_formemory = f'{comment_text}'
        if next_agent.name == 'Developer':
            comment_log_forcode = f'{comment_text}'
        comment_pool.add_comment(Comment(next_agent, comment_text))
    answer = reducer.forward(problem, comment_pool)
    #summary = summarizer.forward(problem , comment_log_formemory)
    #total_comments = comment_pool.get_current_comment_text()

    comment_log.close()
    code = extract_code_from_string(answer)
    ### Fix common syntax errors
    code = code.replace('inrange', 'in range')
    with open('generated_code.py', 'w', encoding='utf8', errors='ignore') as f:
        f.write(code)
    return answer,comment_log_formemory,comment_log_forcode


# if __name__ == '__main__':
#     from utils import read_problem
#     problem = read_problem('assignment_2d', 'prob_250')
#     chain_of_agents(problem, model_name='deepseek-chat')
