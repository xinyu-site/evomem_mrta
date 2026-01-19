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
