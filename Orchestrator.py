import random

from langchain import PromptTemplate, OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI

from agents.base_agent import BaseAgent


class Orchestrator(BaseAgent):

    ROLE_DESCRIPTION='''you will take on the role of the Orchestrator for a multi-agent system.'''
    FORWARD_TASK = '''Now, you are presented with an operational optimization-related problem: 
{problem_description}

In this multi-agent system, there are many agents, each of whom is responsible for solving part of the problem.
Your task is to CHOOSE THE NEXT agent TO CONSULT and your objective is to ultimately solve the target optimization problem through programming.

The names of the agents and their capabilities are listed below:
{agents_info} 

agents that have already been commented include: 
{commented_agents}

Please select an agent to consult from the remaining agent names {remaining_agents}.

Please note that the maximum number of asked agents is {max_collaborate_nums}.

You should output the name of agent directly. The next agent is:'''

    def __init__(self, model):
        super().__init__(
            name='Conductor',
            description='An special agent that collaborates all other agents.',
            model=model
        )
        self.llm.max_tokens = 10


    def forward(self, problem, comment_pool, max_collaborate_nums):
        all_agents = comment_pool.all_agents
        all_agents_name = [e.name for e in all_agents]
        commented_agents_name = [c.agent.name for c in comment_pool.comments]

        agents_info = '\n'.join([str(e) for e in all_agents]) #role_description
        
        ########test########
        # print('\n\n-----xuyang_test-----\n')
        # print('\n'.join([str(e) for e in all_agents]))
        # print('\n\n-----test_over-----\n')
        ########test########
        
        commented_agents = str(commented_agents_name)     
        remaining_agents = str(list(set(all_agents_name) - set(commented_agents_name)))
        answer = self.forward_chain.predict(
            problem_description=problem['description'], 
            agents_info=agents_info,
            commented_agents=commented_agents,
            remaining_agents=remaining_agents,
            max_collaborate_nums=max_collaborate_nums,
            remaining_collaborate_nums=max_collaborate_nums-len(commented_agents_name),
        )
        agent_name_to_obj = { e.name: e for e in all_agents }
        for name, agent in agent_name_to_obj.items():
            if name in answer:
                return agent

        print('Can not find agent, random choice!')
        return random.choice(list(agent_name_to_obj.values()))

