from typing import Dict, Optional, Literal, Any
import os
import json
from abc import ABC, abstractmethod
from litellm import completion

class BaseLLMController(ABC):
    @abstractmethod
    def get_completion(self, prompt: str) -> str:
        """Get completion from LLM"""
        pass

class OpenAIController(BaseLLMController):
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None):
        try:
            from openai import OpenAI
            self.model = model
            if api_key is None:
                api_key = os.getenv('OPENAI_API_KEY')
            if api_key is None:
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI package not found. Install it with: pip install openai")
    
    def get_completion(self, prompt: str, response_format: dict, temperature: float = 0.7) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You must respond with a JSON object."},
                {"role": "user", "content": prompt}
            ],
            response_format=response_format,
            temperature=temperature,
            max_tokens=1000
        )
        return response.choices[0].message.content

class SiliconFlowController(BaseLLMController):
    def __init__(self, 
                 model: str = "deepseek-ai/DeepSeek-v3",
                 api_key: Optional[str] = None,
                 base_url: str = "https://api.siliconflow.cn/v1"):
        """
        初始化硅基流动控制器
        
        参数:
            model: 硅基流动平台上的模型名称，例如 'deepseek-ai/DeepSeek-V3'
            api_key: 硅基流动的 API 密钥。如果为 None，则从环境变量读取
            base_url: 硅基流动的 API 端点
        """
        try:
            from openai import OpenAI
            
            self.model = model
            
            # 获取 API 密钥
            if api_key is None:
                # 优先尝试硅基流动专用环境变量
                api_key = os.getenv('SILICONFLOW_API_KEY')
            if api_key is None:
                raise ValueError(
                    "硅基流动 API 密钥未找到。请执行以下任一操作：\n"
                    "1. 设置 SILICONFLOW_API_KEY 环境变量\n"
                    "2. 设置 OPENAI_API_KEY 环境变量\n"
                    "3. 在初始化时传入 api_key 参数"
                )
            
            # 初始化 OpenAI 客户端，指定硅基流动的 base_url
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
        except ImportError:
            raise ImportError("OpenAI 包未找到。请使用 `pip install openai` 安装。")

    def get_completion(self, prompt: str, response_format: dict, temperature: float = 0.7) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You must respond with a JSON object."},
                {"role": "user", "content": prompt}
            ],
            response_format=response_format,
            temperature=temperature,
            max_tokens=1000
        )
        return response.choices[0].message.content

class OllamaController(BaseLLMController):
    def __init__(self, model: str = "llama2"):
        from ollama import chat
        self.model = model
    
    def _generate_empty_value(self, schema_type: str, schema_items: dict = None) -> Any:
        if schema_type == "array":
            return []
        elif schema_type == "string":
            return ""
        elif schema_type == "object":
            return {}
        elif schema_type == "number":
            return 0
        elif schema_type == "boolean":
            return False
        return None

    def _generate_empty_response(self, response_format: dict) -> dict:
        if "json_schema" not in response_format:
            return {}
            
        schema = response_format["json_schema"]["schema"]
        result = {}
        
        if "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                result[prop_name] = self._generate_empty_value(prop_schema["type"], 
                                                            prop_schema.get("items"))
        
        return result

    def get_completion(self, prompt: str, response_format: dict, temperature: float = 0.7) -> str:
        try:
            response = completion(
                model="ollama_chat/{}".format(self.model),
                messages=[
                    {"role": "system", "content": "You must respond with a JSON object."},
                    {"role": "user", "content": prompt}
                ],
                response_format=response_format,
            )
            return response.choices[0].message.content
        except Exception as e:
            empty_response = self._generate_empty_response(response_format)
            return json.dumps(empty_response)

class LLMController:
    """LLM-based controller for memory metadata generation"""
    def __init__(self, 
                 backend: Literal["openai", "ollama"] = "openai",
                 model: str = "gpt-4", 
                 api_key: Optional[str] = None):
        if backend == "openai":
            self.llm = OpenAIController(model, api_key)
        elif backend == "ollama":
            self.llm = OllamaController(model)
        elif backend == "siliconflow":
            self.llm = SiliconFlowController(model, api_key)
        else:
            raise ValueError("Backend must be one of: 'openai', 'ollama'")
            
    def get_completion(self, prompt: str, response_format: dict = None, temperature: float = 0.7) -> str:
        return self.llm.get_completion(prompt, response_format, temperature)
