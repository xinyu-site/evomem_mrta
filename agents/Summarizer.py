from agents.base_agent import BaseAgent

from langchain import PromptTemplate, OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI

class Summarizer(BaseAgent):
    ROLE_DESCRIPTION = 'You are an efficient Model Refinement Expert, skilled at condensing complex optimization models into their core essentials.'
    FORWARD_TASK = ''' Review the following problem and model. Briefly summarize the problem description, optimization variables, constraints, objective function , and Precautions (1-3 sentences each).
    this is the original problem: {problem_description} 
    this is the model file: {identify_text}
    '''
    REQUIREMENT = '''Output Constraints:
One-Sentence Principle: Each item (Variables, Constraints, Objective) must be expressed in exactly one sentence.
Professional Language: Use general mathematical terminology (e.g., binary variables, linear constraints, etc.) where appropriate, but do not use any mathematical formulas.
Minimalist Format: Do not include any redundant explanations. Output the concise summary directly using the following structure:
[Problem Summary]: [Insert summary here]
[Optimization Variables]: [Insert summary here]
[Optimization Constraints]: [Insert summary here]
[Optimization Objective]: [Insert summary here]
[Precautions]: [insert precautions here]
'''

    def __init__(self, model):
        super().__init__(
            name='Summarizer',
            description='consolidate the task brief and agent discussions into a concise, retained summary for project continuity.',
            model=model   
        )

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
        
        #GPT-4
        # self.llm = ChatOpenAI(
        #     model_name=model,
        #     temperature=0,
        #     base_url = "https://api.chatanywhere.tech/v1",
        #     api_key = 'sk-eB3amex64yCM01u80urNvM3U5hNoolN3uviq4tecP6rMNNna',
        # )

        # 火山引擎
        # self.llm = ChatOpenAI(
        #     model_name=model,
        #     temperature=0,
        #     base_url = "https://ark.cn-beijing.volces.com/api/v3",
        #     api_key = '089c0369-1972-4924-9d30-22731ec58d27',
        # )      
          
        # self.llm = ChatOpenAI(
        # model_name=model,
        # temperature=0,
        # base_url = "http://localhost:11434/v1/",
        # api_key='ollama',
        # )   


        self.forward_prompt_template = self.ROLE_DESCRIPTION + '\n' + self.FORWARD_TASK + '\n' + self.REQUIREMENT
        self.forward_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(self.forward_prompt_template)
        )

    def forward(self, problem, identify_text):
        self.problem = problem
        #comments_text = comment_pool.get_current_comment_text()
        output = self.forward_chain.predict(
            problem_description=problem['description'], 
            identify_text = identify_text 
        )
        return output