from agents.base_agent import BaseAgent

from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI


class Modeler(BaseAgent):

    ROLE_DESCRIPTION = 'You are a modeling expert in Operations Research and Optimization, specializing in Mixed-Integer Programming (MIP). Your task is to construct a mathematical optimization model based on the problem description and insights provided by other agents. Leverage your expertise to formulate the optimization objectives and constraints, ensuring the model is comprehensive and suitable for solving the given production challenge. Please integrate all inputs and provide a well-defined model that aligns with operational research principles.'

    FORWARD_TASK = '''Now the origin problem is as follow:
{problem_description}
And the comments from other agents are as follow:
{comments_text}

Give your MIP model of this problem. Additionally, please note that your model needs to be a solvable linear programming model or a mixed-integer programming model. This also means that the expressions of the constraint conditions can only be equal to, greater than or equal to, or less than or equal to (> or < are not allowed to appear and should be replaced to be \geq or \leq).

Your output format should be a JSON like this:
{{
    "VARIABLES": "A mathematical description about variables",
    "CONSTRAINS": "A mathematical description about constrains",
    "OBJECTIVE": "A mathematical description about objective"
}}
'''


    def __init__(self, model):
        super().__init__(
            name='Modeler',
            description='Proficient in constructing mathematical optimization models based on the extracted information.',
            model=model  
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
        # Meet the rule of MIP
        output = output.replace(' < ', ' \leq ').replace(' > ', ' \geq ')
        self.previous_answer = output
        return output


if __name__ == '__main__':
    from comment_pool import CommentPool
    import numpy as np
    num_agents = 0
    all_agents = []
    problem = {
        'description': 'A telecom company needs to build a set of cell towers to provide signal coverage for the inhabitants of a given city. A number of potential locations where the towers could be built have been identified. The towers have a fixed range, and due to budget constraints only a limited number of them can be built. Given these restrictions, the company wishes to provide coverage to the largest percentage of the population possible. To simplify the problem, the company has split the area it wishes to cover into a set of regions, each of which has a known population. The goal is then to choose which of the potential locations the company should build cell towers on in order to provide coverage to as many people as possible. Please formulate a mathematical programming model for this problem based on the description above.',
    }
    comment_pool = CommentPool(all_agents, visible_matrix=np.ones((num_agents, num_agents)))
    agent = Modeler('deepseek-chat')
    answer = agent.forward(problem, comment_pool)
    print(answer)
