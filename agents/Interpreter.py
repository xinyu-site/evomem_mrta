import json
from agents.base_agent import BaseAgent
import re
from langchain import PromptTemplate, OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI


class Interpreter(BaseAgent):

    ROLE_DESCRIPTION = 'You are a domain-specific terminology expert who offers additional contextual knowledge to improve problem comprehension and formulation.'
    FORWARD_TASK = '''Your role is to enhance problem understanding by providing additional insights, clarifying key concepts, and suggesting ways to refine the problem definition. 
    Based on the provided problem description 
    {problem_description}. 
    please share your expertise, explain relevant terms, and offer recommendations to improve the problem's clarity and formulation. 

Your output format should be a JSON like this (choose at most 3 hardest terminology):
[
  {{
    "terminology": "...",
    "interpretation": "..."
  }}
]
'''

    def __init__(self, model):
        super().__init__(
            name='Interpreter',
            description='Provides additional domain-specific knowledge to enhance problem understanding and formulation.',
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

        #GPT3-5 
        # self.llm = ChatOpenAI(
        #     model_name=model,
        #     temperature=0,
        #     base_url = "https://api.chatanywhere.tech/v1",
        #     api_key = 'sk-uqGsFBwEOsAqqn7LQyTVzQhOU4oJ4dsgsyz10UnjHyarnkHg',
        # )  
        
        #GPT-4
        # self.llm = ChatOpenAI(
        #     model_name=model,
        #     temperature=0,
        #     base_url = "https://api.chatanywhere.tech/v1",
        #     api_key = 'sk-eB3amex64yCM01u80urNvM3U5hNoolN3uviq4tecP6rMNNna',
        # )  

        self.llm = ChatOpenAI(
            model_name=model,
            temperature=0,
            base_url = "https://api.siliconflow.cn/v1",
            api_key = 'sk-eppemmtkctnsbyhfpwdsswibkclczxfaeacjqyqmkdgmhiui',
        )
        self.forward_prompt_template = self.ROLE_DESCRIPTION + '\n' + self.FORWARD_TASK
        self.forward_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(self.forward_prompt_template)
        )

    def forward(self, problem, comment_pool):
        self.problem = problem
        comments_text = comment_pool.get_current_comment_text()
        print('Input')
        print(self.FORWARD_TASK.format(
            problem_description=problem['description'], 
            comments_text=comments_text
        ))
        print()
        output = self.forward_chain.predict(
            problem_description=problem['description'], 
            comments_text=comments_text
        )
        # output = output.strip()  # 去除首尾空格和换行符
        # if output.startswith('```') and output.endswith('```'):
        #     output = '\n'.join(output.split('\n')[1:-1])  # 去掉开头和结尾的 Markdown 标记
        #     output = output.replace('\n', '').replace('\\(', '(').replace('\\)', ')')
        # output = json.dumps(output, ensure_ascii=False)
        #当大模型输出json需要清理格式时：
        output = re.sub(r"```json|```", "", output)
        output = output.replace('\\', '\\\\') 
        output = re.search(r'\[.*\]', output, re.DOTALL).group()
        output = json.loads(output)
        answer = ''
        for item in output:
            answer += item['terminology'] + ':' + item['interpretation'] + '\n'
        self.previous_answer = answer
        return answer

if __name__ == '__main__':
    from comment_pool import CommentPool
    import numpy as np
    num_experts = 0
    all_experts = []
    problem = {
        'description': 'A telecom company needs to build a set of cell towers to provide signal coverage for the inhabitants of a given city. A number of potential locations where the towers could be built have been identified. The towers have a fixed range, and due to budget constraints only a limited number of them can be built. Given these restrictions, the company wishes to provide coverage to the largest percentage of the population possible. To simplify the problem, the company has split the area it wishes to cover into a set of regions, each of which has a known population. The goal is then to choose which of the potential locations the company should build cell towers on in order to provide coverage to as many people as possible. Please formulate a mathematical programming model for this problem based on the description above.',
    }
    comment_pool = CommentPool(all_experts, visible_matrix=np.ones((num_experts, num_experts)))
    expert = Interpreter('deepseek-chat')
    answer = expert.forward(problem, comment_pool)
    print(answer)
