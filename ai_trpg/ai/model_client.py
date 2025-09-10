"""
AI模型客户端

统一的大语言模型调用接口，支持多种AI后端（Ollama、LM Studio等）。
负责与不同AI服务进行通信，处理请求格式转换和响应解析。

主要功能:
- 多后端AI服务支持
- 统一的调用接口
- 自动格式转换
- 错误处理和重试
"""

import requests
import json
from typing import Dict, Any, Optional, List
from enum import Enum


class APIType(Enum):
    """支持的AI后端类型"""
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"


class ModelClient:
    """
    统一的AI模型客户端
    
    提供统一接口调用不同的AI后端服务，自动处理不同API格式的差异。
    支持场景生成和意图分析两种主要调用模式。
    """
    
    def __init__(self, model_name: str, api_type: APIType, base_url: str, context_limit: int = 32000):
        """
        初始化模型客户端
        
        Args:
            model_name: 模型名称（对LM Studio无效，使用当前加载的模型）
            api_type: API类型（Ollama或LM Studio）
            base_url: API服务地址
            context_limit: 上下文token限制
        """
        self.model_name = model_name
        self.api_type = api_type
        self.base_url = base_url
        self.context_limit = context_limit
        
        # 验证配置
        self._validate_config()
        
    def generate_scene(self, context_history: List[Dict], player_name: str, turn_count: int) -> str:
        """
        生成游戏场景描述
        
        Args:
            context_history: 游戏历史上下文
            player_name: 玩家角色名
            turn_count: 当前回合数
            
        Returns:
            生成的场景描述文本
            
        调用时机: 每轮游戏需要推进场景时
        """
        # 构建场景生成的prompt
        context_text = self._format_history_context(context_history)
        
        prompt = f"""你是一个TRPG城主，负责描述游戏场景和推进故事。
当前回合: {turn_count}
玩家: {player_name or "冒险者"}

历史记录:
{context_text}

请生成一个生动的场景描述，包含环境、氛围和可能的选择。保持在100-200字。"""

        return self._make_request(prompt, "场景生成")
        
    def analyze_intent(self, player_input: str, current_scene: str) -> str:
        """
        分析玩家行动意图
        
        Args:
            player_input: 玩家输入的行动
            current_scene: 当前场景描述
            
        Returns:
            JSON格式的意图分析结果
            
        调用时机: 每次接收到玩家输入后
        """
        prompt = f"""你是TRPG城主，需要分析玩家行动意图。

当前场景: {current_scene}
玩家行动: {player_input}

请仔细分析玩家的真实意图，不要局限于预设分类。
重要：请直接返回纯JSON格式，不要用```json包装，不要添加任何其他文本。

输出格式：
{{
    "intent": "玩家的具体意图描述",
    "category": "你认为最合适的意图分类",
    "target": "行动目标",
    "response": "城主对该行动的直接回应"
}}"""

        return self._make_request(prompt, "意图分析")
        
    def _make_request(self, prompt: str, request_type: str) -> str:
        """
        向AI服务发送请求
        
        Args:
            prompt: 发送给AI的提示文本
            request_type: 请求类型（用于日志）
            
        Returns:
            AI的响应文本
            
        Raises:
            RequestException: API调用失败时
        """
        try:
            if self.api_type == APIType.OLLAMA:
                return self._ollama_request(prompt)
            elif self.api_type == APIType.LM_STUDIO:
                return self._lm_studio_request(prompt)
            else:
                raise ValueError(f"不支持的API类型: {self.api_type}")
                
        except requests.RequestException as e:
            raise Exception(f"{request_type}请求失败: {str(e)}")
        except KeyError as e:
            raise Exception(f"{request_type}响应格式错误: {str(e)}")
            
    def _ollama_request(self, prompt: str) -> str:
        """
        发送Ollama格式的请求
        
        Args:
            prompt: 提示文本
            
        Returns:
            响应文本
        """
        payload = {
            'model': self.model_name,
            'prompt': prompt,
            'stream': False
        }
        
        response = requests.post(self.base_url, json=payload, timeout=60)
        response.raise_for_status()
        
        return response.json()['response']
        
    def _lm_studio_request(self, prompt: str) -> str:
        """
        发送LM Studio格式的请求（OpenAI兼容）
        
        Args:
            prompt: 提示文本
            
        Returns:
            响应文本
        """
        payload = {
            'model': self.model_name,  # LM Studio会忽略此参数
            'messages': [{'role': 'user', 'content': prompt}],
            'stream': False,
            'temperature': 0.7
        }
        
        response = requests.post(self.base_url, json=payload, timeout=60)
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']
        
    def _format_history_context(self, history: List[Dict]) -> str:
        """
        格式化历史记录为上下文文本
        
        Args:
            history: 历史记录列表
            
        Returns:
            格式化的上下文文本
        """
        if not history:
            return "暂无历史记录"
            
        return "\n".join([f"{entry['type']}: {entry['content']}" for entry in history])
        
    def _validate_config(self) -> None:
        """
        验证客户端配置
        
        Raises:
            ValueError: 配置无效时
        """
        if not self.base_url:
            raise ValueError("base_url不能为空")
        if not self.model_name:
            raise ValueError("model_name不能为空")
        if self.context_limit <= 0:
            raise ValueError("context_limit必须大于0")
            
    def get_client_info(self) -> Dict[str, Any]:
        """
        获取客户端配置信息
        
        Returns:
            包含客户端配置的字典
            
        调用时机: 显示当前配置或调试时
        """
        return {
            'model_name': self.model_name,
            'api_type': self.api_type.value,
            'base_url': self.base_url,
            'context_limit': self.context_limit
        }