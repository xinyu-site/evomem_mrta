from langchain import PromptTemplate, OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI
from test_generated_code import test_generated_code, read_test_samples
from utils import extract_code_from_string
import subprocess
import os
from result import Result
#检查生成代码是否正确：
def execute_code(file_path):
    try:
        # Using Python's subprocess to execute the code as a separate process
        result = subprocess.run(
            ["python", file_path], capture_output=True, text=True, check=True
        )
        # save result in a file
        with open(
            os.path.join(os.path.dirname(file_path), "ref_optimal_value.txt"), "w"
        ) as f:
            f.write(f"Optimal Revenue: {result.stdout}\n")
        return result.stdout, "Success"
    except subprocess.CalledProcessError as e:
        return e.stderr, "Error"


def solve(problem_data, dataset, problem, model_name='deepseek-chat'):
    problem_description = problem_data['description']
    code_example = problem_data['code_example']
    code_answer = []
    code_comment = []
    max_iter = 2
    for i in range(max_iter):
        prompt_template = """You are an expert operations research analyst.Your task is to generate Gurobi code to solve the following optimization problem:{problem_description} 
        Here is a starter code:{code_example}"""

        if len(code_answer) != 0:
            prompt_template = prompt_template + '\nYou have been given the task to generate Gurobi code to solve an optimization problem.You have generated the following Gurobi code:\n {code_answer}'
        if len(code_comment) != 0:
            prompt_template = prompt_template + '\nThe feedback is :\n {code_comment}'
        #deepseek-chat
        # llm = ChatOpenAI(
        #     model_name=model_name,
        #     temperature=0,
        #     base_url = "https://api.deepseek.com/v1",
        #     api_key = 'sk-9b1412c4779a440b8de2656cd64b27e6'
        # )
            #qwen2.5:72b
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
        answer = llm_chain.predict(problem_description=problem_description, code_example=code_example, code_answer=code_answer, code_comment=code_comment)
        code = extract_code_from_string(answer)
        code_filenames = 'generated_code.py'
        with open(code_filenames, 'w') as f:
            f.write(code)
        test_sample = read_test_samples(dataset, problem)
        result = test_generated_code(problem, test_sample, None)

        if result == Result.ACCEPT:
            print(f"Iteration {i+1}: Code executed successfully.")
            break   
        else:
            code_answer.append(code)
            if result == Result.COMPILE_ERROR:
                output = "There is grammar error in generated code!\n"
            else:
                output = "Runtime Error!\n"
            code_comment.append(output)        
        # output, status = execute_code(code_filenames)
        # if status == "Success":
        #     print(f"Iteration {i+1}: Code executed successfully.")
        #     break
        # else:
        #     print(f"Iteration {i+1}: Error encountered during code execution:\n{output}")
        #     code_answer.append(code)
        #     code_comment.append(output)
    return code
