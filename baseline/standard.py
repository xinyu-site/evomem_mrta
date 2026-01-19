from langchain import PromptTemplate, OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI

from utils import extract_code_from_string


def solve(problem, model_name='deepseek-chat'):
    prompt_template = """You are a Python programmer specializing in operations research and optimization. Your expertise in using the Gurobi solver is essential for this task. You are given a specific optimization problem and must use Gurobi to solve it.
                    Please develop an efficient Python program that utilizes the Gurobi solver to address the following problem:
                    \n{problem}\n
                    Please provide the Python code directly, ensuring that Gurobi is the sole solver used in the solution."""
    #deepseek-chat
    # llm = ChatOpenAI(
    #     model_name=model_name,
    #     temperature=0,
    #     base_url = "https://api.deepseek.com/v1"
    # )
    #硅基流动
    llm = ChatOpenAI(
        model_name=model_name,
        temperature=0,
        base_url = "https://api.siliconflow.cn/v1",
        api_key = 'sk-omgchgrtfkggigckdnqhmetsrlqpezhtbylrhchxcurlowza',
    )
    #qwen2.5:72b
    # llm = ChatOpenAI(
    #     model_name=model_name,
    #     temperature=0,
    #     base_url = "http://localhost:11434/v1/",
    #     api_key='ollama',
    # )    
    llm_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate.from_template(prompt_template)
    )
    answer = llm_chain.predict(problem=problem)
    code = extract_code_from_string(answer)
    return code
