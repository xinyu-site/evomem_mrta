from langchain import PromptTemplate, OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI

from utils import extract_code_from_string


def solve(problem_data, model_name='deepseek-chat'):
    problem_description = problem_data['description']
    code_example = problem_data['code_example']

    max_iter = 2  #1能行，1以上会报错
    history_answer = []
    for i in range(max_iter):
        prompt_template = """You are a Python programmer in the field of operations research and optimization. Your expertise in using the Gurobi solver is essential for this task. You are given a specific optimization problem and must use Gurobi to solve it.
        You are given a specific problem. You aim to develop an efficient Python program that addresses the given problem.
        Now the origin problem is as follow: {problem_description} Let's analyse the problem step by step, and then give your Python code. Here is a starter code: {code_example}"""
        if len(history_answer) != 0:
            prompt_template = prompt_template  + '\nThe code looks like as following:\n {history_answer}' +  "\n You need to check that the code is correct and can be executed directly."
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
        # 创建 LLMChain 实例
        # llm_chain = LLMChain(
        #     llm=llm,
        #     prompt=PromptTemplate.from_template(prompt_template)
        # )

        llm_chain = LLMChain(
            llm=llm,
            prompt=PromptTemplate.from_template(prompt_template)
        )
        # 调用 predict 时传入对应的参数
        answer = llm_chain.predict(problem_description=problem_description, code_example=code_example, history_answer=history_answer)

        # 提取并处理返回的代码
        code = extract_code_from_string(answer)

        # 将代码保存到历史回答中
        history_answer.append(code)

    return code
    

