from langchain import PromptTemplate, OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI

from utils import extract_code_from_string


def solve(problem, model_name='deepseek-chat'):
    #2d
    # prompt_template = """You are a task allocation expert. When faced with task allocation problems, 
    # you are always able to provide suitable allocation results. following is the given problem: {problem_description}.The defender's coordinates are [[1.203727, 2.969430], [1.727916, -6.355782], [3.139244, 0.343098], [-4.423817, -2.926338], [-6.931869, -5.268187], [1.603833, -0.255801], [-0.419330, -1.707259], [1.087489, -3.886456], [-1.301701, 0.365086], [4.945316, 0.945933]],
    #  and the attacker's coordinates are [[-28.121649, 32.066541], [-7.337243, 41.994851], [-2.856919, -46.448113], [-38.720570, -29.654847], [-45.722895, 3.935132], [-10.851915, 45.113331], [34.614540, -26.756196], [19.535534, 42.926890], [-33.087210, -29.893860], [-28.318632, 40.274682]]. Please provide the allocation result directly."""
    
    #3d
    prompt_template = """You are a task allocation expert. When faced with task allocation problems, 
    you are always able to provide suitable allocation results. following is the given problem: {problem_description}.The defender's coordinates are [[1.8771734771064867, 2.9235244737629444, 0.5194265239629677], [0.7367880047944282, 1.1474793300999155, 3.1101061797875977], [1.1147137651643755, 1.736063828646149, 3.79305077172417], [0.07594909040401536, 0.11828370007572703, 0.7804475392702637], [2.089552767659228, 3.2542856214265115, 3.387517983899654], [0.06873255360222695, 0.10704460991536537, 0.12544197790816544], [0.5784678080547861, 0.9009102327287131, 3.6520718300780977], [0.8657379405800287, 1.3483069561861634, 0.5516515971088848], [1.8042842546398425, 2.810006235649303, 3.6478532033478], [0.3344656043861239, 0.5208993159023199, 0.8270172921454256]],
     and the attacker's coordinates are [[-1.818817817569365, -1.4413917270189331, 0.0], [-0.6916353019634377, 0.07164019094758788, 0.0], [-4.967368142958153, -1.3732311283335128, 0.0], [-3.6155045544511712, -0.1836635632483707, 0.0], [-4.500760384932397, -3.1852118958073268, 0.0], [-3.446753713131527, -0.457581746119771, 0.0], [-5.538219722970499, -1.9076119560181874, 0.0], [-2.663450064905594, -1.7820707475787376, 0.0], [-0.8298298956332999, -0.10113316816382267, 0.0], [-2.7216143336808085, -1.4218926236312033, 0.0]]. Please provide the allocation result directly."""
    
    
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
    problem_description=problem['description']
    answer = llm_chain.predict(problem_description=problem_description)
    return answer
