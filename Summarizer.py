from agents.base_agent import BaseAgent

from langchain import PromptTemplate, OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI

class BaseAgent(object):

    def __init__(self, name, description, model):
        self.name = name
        self.description = description
        self.model = model

        # self.llm = ChatOpenAI(
        #     model_name=model,
        #     temperature=0,
        #     base_url = "https://api.deepseek.com/v1"
        # )

        #GPT-4
        # self.llm = ChatOpenAI(
        #     model_name=model,
        #     temperature=0,
        #     base_url = "https://api.chatanywhere.tech/v1",
        #     api_key = 'sk-eB3amex64yCM01u80urNvM3U5hNoolN3uviq4tecP6rMNNna',
        # )

        #GPT3.5
        # self.llm = ChatOpenAI(
        #     model_name=model,
        #     temperature=0,
        #     base_url = "https://api.chatanywhere.tech/v1",
        #     api_key = 'sk-uqGsFBwEOsAqqn7LQyTVzQhOU4oJ4dsgsyz10UnjHyarnkHg',
        # )

        self.llm = ChatOpenAI(
            model_name=model,
            temperature=0,
            base_url = "https://api.siliconflow.cn/v1",
            api_key = 'sk-eppemmtkctnsbyhfpwdsswibkclczxfaeacjqyqmkdgmhiui',
        )

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

    def forward(self):
        pass

    def __str__(self):
        return f'{self.name}: {self.description}'

class Summarizer(BaseAgent):
    ROLE_DESCRIPTION_TRUE = 'You are an efficient Model Refinement Expert, skilled at condensing complex optimization models into their core essentials.'
    FORWARD_TASK_TRUE = ''' Review the following problem and model. Briefly summarize the problem description, optimization variables, constraints, objective function , and Precautions (1-3 sentences each).
    this is the original problem: {problem_description} 
    this is the model file: {identify_text}
    '''
    REQUIREMENT_TRUE = '''Output Constraints:
One-Sentence Principle: Each item (Variables, Constraints, Objective) must be expressed in exactly one sentence.
Professional Language: Use general mathematical terminology (e.g., binary variables, linear constraints, etc.) where appropriate, but do not use any mathematical formulas.
Minimalist Format: Do not include any redundant explanations. Output the concise summary directly using the following structure:
[Problem Summary]: [Insert summary here]
[Optimization Variables]: [Insert summary here]
[Optimization Constraints]: [Insert summary here]
[Optimization Objective]: [Insert summary here]
[Precautions]: [insert precautions here]
'''

    ROLE_DESCRIPTION_FALSE = 'You are an efficient Model Diagnosis Expert, skilled at quickly identifying core logical errors in optimization models.'
    FORWARD_TASK_FALSE = ''' Please analyze the following original problem and a model known to be incorrect. Your task is to directly and concisely explain why this modeling approach is wrong.
    this is the original problem: {problem_description} 
    this is the model file: {identify_text}
    '''
    REQUIREMENT_FALSE = '''Output Requirements:
    Focus on the Root Cause: Analyze the fundamental logical error or key assumption bias in the modeling, not surface-level or syntax issues.
    Fixed Structure: Use only the following structure for your output, with no introductory summary.
    Concise Language: Explain each part in 1-2 sentences.
    Output Structure (Strictly Follow):
    [Error Cause Analysis]
    [Core Error]: [State the most fundamental error in 1-2 sentences]
    [Specific Analysis]: [Briefly explain the contradiction between the model logic and the problem requirements]
    [Potential Consequences]: [The typical result of such an error, e.g., meaningless solution, infeasible model, etc.]
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

    def forward(self, problem, identify_text, answer_right):
        self.problem = problem
        #comments_text = comment_pool.get_current_comment_text()
        if answer_right==True:
            self.forward_prompt_template = self.ROLE_DESCRIPTION_TRUE + '\n' + self.FORWARD_TASK_TRUE + '\n' + self.REQUIREMENT_TRUE
            self.forward_chain = LLMChain(
                llm=self.llm,
                prompt=PromptTemplate.from_template(self.forward_prompt_template)
            )
            output = self.forward_chain.predict(
                problem_description=problem, 
                identify_text = identify_text 
            )
        else:
            self.forward_prompt_template = self.ROLE_DESCRIPTION_FALSE + '\n' + self.FORWARD_TASK_FALSE + '\n' + self.REQUIREMENT_FALSE
            self.forward_chain = LLMChain(
                llm=self.llm,
                prompt=PromptTemplate.from_template(self.forward_prompt_template)
            )
            output = self.forward_chain.predict(
                problem_description=problem, 
                identify_text = identify_text 
            )

        
        return output