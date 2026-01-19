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


        self.forward_prompt_template = self.ROLE_DESCRIPTION + '\n' + self.FORWARD_TASK
        self.forward_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate.from_template(self.forward_prompt_template)
        )

    def forward(self):
        pass

    def __str__(self):
        return f'{self.name}: {self.description}'
    
class Evolver(BaseAgent):

    ROLE_DESCRIPTION = 'You are an experienced work review expert, proficient in summarization, comparison, and iterative writing. Your core capability is: by comparing old summary and new summary, extracting effective patterns, preserving the essence, and integrating new insights to generate a more mature and more instructive iterative version of the work summary.'

    FORWARD_TASK = '''
You will receive two inputs:

1-{current_summary}
2-{original_summary}

Your Task: Revise and upgrade the Original Work Summary by integrating the new insights and lessons from the Current Work Problem and Current Work Summary.
Output Rules:
1-Output only the final, revised summary text. No explanations.
2-Preserve the original's core structure, successful conclusions, and its overall tone/style.
'''


    def __init__(self, model):
        super().__init__(
            name='Modeler',
            description='Proficient in constructing mathematical optimization models based on the extracted information.',
            model=model  
        )

    def forward(self, problem_cur, summary_cur, summary_orin):
        output = self.forward_chain.predict(
            current_problem=problem_cur,
            current_summary=summary_cur, 
            original_summary=summary_orin,
        )
        
        return output
