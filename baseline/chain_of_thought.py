from langchain import PromptTemplate, OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI

from utils import extract_code_from_string
#qwen2.5:72b
from transformers import AutoModelForCausalLM, AutoTokenizer
from langchain.llms import HuggingFacePipeline
from transformers import pipeline
def solve(problem_data, model_name='deepseek-chat'):
    problem_description = problem_data['description']
    code_example = problem_data['code_example']
    # In addition to your expertise in Gurobi, it would be great if you could also provide some background in related libraries or tools, like NumPy, SciPy, or PuLP.
    prompt_template = """You are a Python programmer specializing in operations research and optimization. Your expertise in using the Gurobi solver is essential for this task. You are given a specific optimization problem and must use Gurobi to solve it.
You are given a specific problem. You aim to develop an efficient Python program that addresses the given problem.
Now the origin problem is as follow:
{problem_description}
Let's analyse the problem step by step, and then give your Python code.
Here is a starter code:
{code_example}"""
    #deepseek-chat
    # llm = ChatOpenAI(
    #     model_name=model_name,
    #     temperature=0,
    #     base_url = "https://api.deepseek.com/v1"
    # )
    # #qwen2.5:72b
    # llm = ChatOpenAI(
    #     model_name=model_name,
    #     temperature=0,
    #     base_url = "http://localhost:11434/v1/",
    #     api_key='ollama',
    # )    
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=0,
        base_url = "https://api.siliconflow.cn/v1",
        api_key = 'sk-omgchgrtfkggigckdnqhmetsrlqpezhtbylrhchxcurlowza',
    )
    llm_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate.from_template(prompt_template)
    )
    answer = llm_chain.predict(problem_description=problem_description, code_example=code_example)
    return answer
