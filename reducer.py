from langchain import PromptTemplate, OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI

from agents.base_agent import BaseAgent


class Reducer(BaseAgent):

    ROLE_DESCRIPTION = 'You are an agent responsible for synthesizing feedback from all other agents and delivering a clear, concise final answer.'
    FORWARD_TASK = '''You are an Operations Research agent tasked with delivering the final code to solve a given problem. 
    Carefully analyze the problem description: {problem_description}. 
    Thoroughly review the detailed insights provided by your colleagues: {comment_text}. 
    Incorporate their feedback to ensure your implementation is accurate, efficient, and aligned with the problem requirements. 
    Provide only the necessary import statements and the function code, avoiding any external test code. Your goal is to deliver a robust and well-structured solution that effectively addresses the problem while reflecting the collective expertise of your team.
    Your final code is as following:
'''

    def __init__(self, model):
        super().__init__(
            name='Solver',
            description='Reduce all comments given by other agents',
            model=model
        )

    def forward(self, problem_description, workspace):
        comment_text = workspace.get_current_comment_text()
        answer = self.forward_chain.predict(
            problem_description=problem_description, 
            comment_text=comment_text
        )
        return answer

