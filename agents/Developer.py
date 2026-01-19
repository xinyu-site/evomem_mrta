from agents.base_agent import BaseAgent

from langchain import PromptTemplate, OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI

from typing import List, Dict, Optional, Any, Tuple

def generate_example_str(example_problem_list:List,example_code_list:List):
    example_num = len(example_problem_list)
    example_str = 'To guide your work, study the following examples carefully. Each example demonstrates the complete thought process from problem description to structured extraction:\n'
    for i in range(example_num):
        example_str += '---\n'
        example_str += f'### EXAMPLE {i+1} ###\n'
        example_str += f'Problem Description:\n{example_problem_list[i]}\n'
        example_str += f'Example Code Implementation:\n{example_code_list[i]}\n\n'
    example_str += '---\n'
    example_str += '***End of Examples***\n'
    #example_str=example_str.replace('{', '{{').replace('}', '}}')
    return example_str
        


class Developer(BaseAgent):

#     ROLE_DESCRIPTION = 'You are a Python programmer specializing in operations research and optimization, with expertise in implementing and solving mathematical problems using Gurobi. Your main responsibility is to write, debug, and optimize code that transforms given optimization formulations into executable solutions using Gurobi. Ensure your implementation aligns with the problem objectives and constraints, and deliver clean, efficient, and well-documented code. While Gurobi is your primary tool, knowledge of related libraries such as NumPy, SciPy, or PuLP can support additional functionality or preprocessing tasks. Your goal is to provide robust, solver-ready code that effectively addresses the optimization problem.'
#     FORWARD_TASK = '''You are tasked with developing an efficient Python program to solve a specific optimization problem using Gurobi. 
#     Analyze the problem step by step based on the provided description 
#     {problem_description} 
#     and the comments from other agents 
#     {comments_text}. 
#     Using the starter code template {code_example} write a Python function that strictly follows the given format and defines a solvable linear programming (LP) or mixed-integer programming (MIP) model. 
#     Include only the necessary import statements and ensure no external test code is provided. Deliver clean, efficient, and well-structured code that aligns with the problem requirements.'''
#     EXAMPLE = '''You have the following problem example to refer to:
#     Problem Description:
#     {example_problem_description}
#     Example Code Implementation:
#     {example_code}        
# '''

    ROLE_DESCRIPTION= '''You are a Python programmer specializing in operations research and optimization, with expertise in implementing and solving mathematical problems using Gurobi. Your main responsibility is to write, debug, and optimize code that transforms given optimization formulations into executable solutions using Gurobi. Ensure your implementation aligns with the problem objectives and constraints, and deliver clean, efficient, and well-documented code. While Gurobi is your primary tool, knowledge of related libraries such as NumPy, SciPy, or PuLP can support additional functionality or preprocessing tasks. Your goal is to provide robust, solver-ready code that effectively addresses the optimization problem.
    As the Modeling Identifier agent, your core task is to meticulously analyze the problem description and any provided expert comments. Your output must be a structured, immediately usable extraction of the model's components.
    Crucially, you MUST ensure all constraints are expressed using only the operators `≥`, `≤`, or `=`; the use of strict inequalities (`>` or `<`) is prohibited for linear programming formulations.'''

    EXAMPLE = '{example_str}'
    
    FORWARD_TASK = '''Analyze the problem step by step based on the provided description 
    {problem_description} 
    and the comments from other agents 
    {comments_text}. 
    Using the starter code template {code_example} write a Python function that strictly follows the given format and defines a solvable linear programming (LP) or mixed-integer programming (MIP) model. 
    Include only the necessary import statements and ensure no external test code is provided. Deliver clean, efficient, and well-structured code that aligns with the problem requirements.'''

    def __init__(self, model,example_problem_list:List,example_code_list:List):
        super().__init__(
            name='Developer',
            description='Skilled in programming and coding, capable of implementing the optimization solution in a programming language.',
            model=model   
        )
        self.example_problem_list = example_problem_list
        self.example_code_list = example_code_list
        if len(self.example_problem_list)!=0:
            #self.forward_prompt_template = self.ROLE_DESCRIPTION + '\n' + self.FORWARD_TASK + '\n' + self.EXAMPLE
            self.forward_prompt_template = self.ROLE_DESCRIPTION + '\n' + self.EXAMPLE + self.FORWARD_TASK + '\n'
        else:
            #self.forward_prompt_template = self.ROLE_DESCRIPTION + '\n' + self.FORWARD_TASK
            self.forward_prompt_template = self.ROLE_DESCRIPTION + '\n' + self.FORWARD_TASK + '\n'
        #self.forward_prompt_template = self.ROLE_DESCRIPTION + '\n' + self.FORWARD_TASK
        self.forward_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(self.forward_prompt_template)
        )


    def forward(self, problem, comment_pool):
        self.problem = problem
        comments_text = comment_pool.get_current_comment_text()
        print('Input')
        if len(self.example_problem_list)!=0:
            print(self.forward_prompt_template.format(
                example_str=generate_example_str(self.example_problem_list,self.example_code_list),
                problem_description=problem['description'], 
                code_example=problem['code_example'],
                comments_text=comments_text,
            ))
        else:
            print(self.forward_prompt_template.format(
                problem_description=problem['description'], 
                code_example=problem['code_example'],
                comments_text=comments_text,
            ))
        # print(self.forward_prompt_template.format(
        #         problem_description=problem['description'], 
        #         code_example=problem['code_example'],
        #         comments_text=comments_text,
        #     ))
        print()
        if len(self.example_problem_list)!=0:
            output = self.forward_chain.predict(
                example_str=generate_example_str(self.example_problem_list,self.example_code_list),
                problem_description=problem['description'], 
                code_example=problem['code_example'],
                comments_text=comments_text,
                )
        else:
            output = self.forward_chain.predict(
                problem_description=problem['description'], 
                code_example=problem['code_example'],
                comments_text=comments_text,
                )
        # output = self.forward_chain.predict(
        #         problem_description=problem['description'], 
        #         code_example=problem['code_example'],
        #         comments_text=comments_text,
        #         )
        self.previous_code = output
        return output
