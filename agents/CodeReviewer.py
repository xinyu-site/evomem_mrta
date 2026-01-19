from agents.base_agent import BaseAgent

from langchain import PromptTemplate, OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI


class CodeReviewer(BaseAgent):

    ROLE_DESCRIPTION = 'You are a code reviewer tasked with testing and evaluating the implemented code, identifying runtime errors or inefficiencies, and providing clear feedback to ensure the final solution is correct, efficient, and fully functional.'
    FORWARD_TASK = '''As a Code Reviewer, your primary focus is to identify and correct errors in the provided code while ensuring it adheres to the given function name and variable names as specified in the starter code {code_example},DO NOT MODIFY THE FUNCTION NAME OR INPUT VARIABLE NAMES. 
    Review the code thoroughly for potential issues, inefficiencies, or deviations from best practices, and ensure it aligns with the problem requirements {problem_description}. 
    Incorporate insights from your colleagues' comments {comments_text} to provide actionable feedback and improvements, ensuring the code is robust, efficient, and fully functional.'''


    def __init__(self, model):
        super().__init__(
            name='Code Reviewer',
            description='Tests and evaluates the implemented code, identifies errors or inefficiencies, and provides clear feedback to ensure the final solution is correct, efficient, and fully functional.',
            model=model   
        )
        # self.llm = ChatOpenAI(
        #     model_name=model,
        #     temperature=0,
        #     base_url = "https://api.deepseek.com/v1"
        # )

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


        self.forward_prompt_template = self.ROLE_DESCRIPTION + '\n' + self.FORWARD_TASK
        self.forward_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(self.forward_prompt_template)
        )

    def forward(self, problem, comment_pool):
        self.problem = problem
        comments_text = comment_pool.get_current_comment_text()
        output = self.forward_chain.predict(
            problem_description=problem['description'], 
            code_example = problem['code_example'],
            comments_text=comments_text
        )
        self.previous_code = output
        return output