from agents.base_agent import BaseAgent

from langchain import PromptTemplate, OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI

from typing import List, Dict, Optional, Any, Tuple



def generate_example_str(example_problem_list:List,example_output_list:List)->str:  
    example_num = len(example_problem_list)
    example_str = 'To guide your work, study the following examples carefully. Each example demonstrates the complete thought process from problem description to structured extraction:\n'
    example_output_list=example_output_list.copy()
    example_problem_list=example_problem_list.copy()
    for i in range(example_num):
        #example_problem_list[i].replace('{', '{{').replace('}', '}}')
        #example_output_list[i].replace('{', '{{').replace('}', '}}')
        example_str += '---\n'
        example_str += f'### EXAMPLE {i+1} ###\n'
        example_str += f'Problem Description:\n{example_problem_list[i]}\n'
        example_str += f'Example Output:\n{example_output_list[i]}\n\n'
        example_str += '---\n'
    example_str += '***End of Examples***\n'
    # print('####xuyang_test####')
    # example_str=example_str.replace('{', '{{').replace('}', '}}')
    # print(example_str)
    #print(example_str)
    return example_str

def generate_summary_str(example_summary_list)->str:
    example_num = len(example_summary_list)
    example_str = 'To guide your work, study the following examples carefully. Each example demonstrates the complete thought process from problem description to structured extraction:\n'
    for i in range(example_num):
        #example_problem_list[i].replace('{', '{{').replace('}', '}}')
        #example_output_list[i].replace('{', '{{').replace('}', '}}')
        example_str += '---\n'
        example_str += f'### EXAMPLE {i+1} ###\n'
        example_str += f'Problem Description:\n{example_summary_list[i]}\n'
        example_str += '---\n'

    return example_str


class Identifier(BaseAgent):

#     ROLE_DESCRIPTION = 'You are an expert in identifying and extracting key decision variables from the problem description to support accurate modeling.'
#     FORWARD_TASK = '''As an Identifier agent, your task is to analyze the problem description and extract relevant variables, constraints, and objectives. 
#     Use your domain expertise to ensure these elements are accurately defined and suitable for formulating a solvable LP or MIP model. 
#     Specifically, ensure constraints use only ≥, ≤, or = operators (avoid > or <). Review the problem description 
#     {problem_description} 
#     and the comments from other experts 
#     {comments_text} 
#     then provide the extracted variables, constraints, and objectives along with their definitions.
# '''
#     EXAMPLE = '''You have the following problem example to refer to:
#     Problem Description:
#     {example_problem_description}
#     Extracted Variables, Constraints, and Objectives:
#     {example_output}        
# '''

    ROLE_DESCRIPTION= '''You are an expert in identifying and extracting key decision variables from the problem description to support accurate modeling.
    As an Identifier agent, your task is to analyze the problem description and extract relevant variables, constraints, and objectives. 
    Use your domain expertise to ensure these elements are accurately defined and suitable for formulating a solvable LP or MIP model. 
    Specifically, ensure constraints use only ≥, ≤, or = operators (avoid > or <).'''
    
    EXAMPLE = 'this is the specific example : {example_str}'
    EXAMPLE_AB = 'If the following information describes a successful summary or unsuccessful analysis, you may refer to it for context.: {example_str}'

    FORWARD_TASK = '''Review the problem description 
    {problem_description} 
    and the comments from other experts 
    {comments_text} 
    then provide the extracted variables, constraints, and objectives along with their definitions.'''


    def __init__(self, model,example_problem_list:List,example_output_list:List,example_summary_list:List):
        super().__init__(
            name='Identifier',
            description='Extracts and defines the key decision variables, constraints, and objectives from the problem description, ensuring they are accurately formulated for the optimization model.',
            model=model   
        )
        # self.llm = ChatOpenAI(
        #     model_name=model,
        #     temperature=0,
        #     base_url = "https://api.deepseek.com/v1"
        # )

        # self.llm = ChatOpenAI(
        # model_name=model,
        # temperature=0,
        # base_url = "http://localhost:11434/v1/",
        # api_key='ollama',
        # )   
        
        # 火山引擎
        # self.llm = ChatOpenAI(
        #     model_name=model,
        #     temperature=0,
        #     base_url = "https://ark.cn-beijing.volces.com/api/v3",
        #     api_key = '089c0369-1972-4924-9d30-22731ec58d27',
        # )    

        self.example_problem_list = example_problem_list
        self.example_output_list = example_output_list
        self.example_summary_list = example_summary_list

        self.llm = ChatOpenAI(
            model_name=model,
            temperature=0,
            base_url = "https://api.siliconflow.cn/v1",
            api_key = 'sk-eppemmtkctnsbyhfpwdsswibkclczxfaeacjqyqmkdgmhiui',
        )

        #GPT3-5 
        # self.llm = ChatOpenAI(
        #     model_name=model,
        #     temperature=0,
        #     base_url = "https://api.chatanywhere.tech/v1",
        #     api_key = 'sk-uqGsFBwEOsAqqn7LQyTVzQhOU4oJ4dsgsyz10UnjHyarnkHg',
        # )  

        # gpt-4    
        # self.llm = ChatOpenAI(
        #     model_name=model,
        #     temperature=0,
        #     base_url = "https://api.chatanywhere.tech/v1",
        #     api_key = 'sk-eB3amex64yCM01u80urNvM3U5hNoolN3uviq4tecP6rMNNna',
        # )

        if len(self.example_problem_list)!=0:
            self.forward_prompt_template = self.ROLE_DESCRIPTION + '\n' + self.EXAMPLE + self.FORWARD_TASK + '\n'
        elif len(self.example_summary_list)!=0:
            self.forward_prompt_template = self.ROLE_DESCRIPTION + '\n' + self.EXAMPLE_AB + self.FORWARD_TASK + '\n'
        else:
            self.forward_prompt_template = self.ROLE_DESCRIPTION + '\n' + self.FORWARD_TASK + '\n'
        
        self.forward_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(self.forward_prompt_template)
        )

    def forward(self, problem, comment_pool):
        self.problem = problem
        comments_text = comment_pool.get_current_comment_text()
        # print('Input')
        # print(self.forward_prompt_template.format(
        #     problem_description=problem['description'], 
        #     comments_text=comments_text
        # ))
        # print()

       
            #self.forward_prompt_template = self.ROLE_DESCRIPTION + '\n' + self.FORWARD_TASK
        print('Input')
        if len(self.example_problem_list)!=0:
            print(self.forward_prompt_template.format(
                example_str=generate_example_str(self.example_problem_list,self.example_output_list),
                problem_description=problem['description'], 
                comments_text=comments_text,
            ))
        elif len(self.example_summary_list)!=0:
            print(self.forward_prompt_template.format(
                example_str=generate_summary_str(self.example_summary_list),
                problem_description=problem['description'], 
                comments_text=comments_text,
            ))
        else:
            print(self.forward_prompt_template.format(
                problem_description=problem['description'], 
                comments_text=comments_text,
            ))
        print()
        
        if len(self.example_problem_list)!=0:
            output = self.forward_chain.predict(
                example_str=generate_example_str(self.example_problem_list,self.example_output_list),
                problem_description=problem['description'], 
                comments_text=comments_text,
                )
        elif len(self.example_summary_list)!=0:
            output = self.forward_chain.predict(
                example_str=generate_summary_str(self.example_summary_list),
                problem_description=problem['description'], 
                comments_text=comments_text,
                )
        else:
            output = self.forward_chain.predict(
                problem_description=problem['description'], 
                comments_text=comments_text,
                )
       
        self.previous_answer = output
        return output
