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
    
class Selector(BaseAgent):

    ROLE_DESCRIPTION = '''You are a classifier that categorizes task descriptions according to the following three rules, and directly outputs one of the 8 corresponding classes (ST_SR_IA, ST_MR_IA, MT_SR_IA, MT_MR_IA, ST_SR_TA, ST_MR_TA, MT_SR_TA, MT_MR_TA):
Classification Rules:
1. ST/MT: Determine whether single robot execute multiple tasks. If yes, output MT; otherwise, output ST.
2. SR/MR: Determine whether there are any tasks that require multiple robots to collaborate for completion. If yes, output MR; otherwise, output SR.
3. IA/TA: Determine whether task planning considers timesteps. If yes, output TA; otherwise, output IA.
Class Explanation (combined in order):
- First part: ST (Single Task) or MT (Multi-Task)
- Second part: SR (Single Robot) or MR (Multi-Robot)
- Third part: IA (Ignore Time) or TA (Time-Aware)
Carefully read the task description, apply the three rules in sequence, and then output only the final class name without any additional text.'''

    FORWARD_TASK = '''
Task Description:
{problem_description}
'''


    def __init__(self, model):
        super().__init__(
            name='Selector',
            description='A classifier that categorizes task scenarios based on multitasking capability, robot requirements, and time‑awareness into one of eight predefined classes.',
            model=model  
        )

    def forward(self, problem_description):
        output = self.forward_chain.predict(
            problem_description=problem_description
        )
        
        return output
