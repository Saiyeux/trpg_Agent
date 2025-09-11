"""
AI服务配置和检测

自动检测可用的本地AI服务，提供配置管理。
"""

import requests
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Agent.client.model_client import APIType


@dataclass
class AIServiceConfig:
    """AI服务配置"""
    name: str
    api_type: APIType
    base_url: str
    model_name: str
    context_limit: int
    available: bool = False
    response_time: float = 0.0
    error_message: str = ""


class AIServiceDetector:
    """AI服务检测器"""
    
    def __init__(self):
        self.services: List[AIServiceConfig] = []
        self.preferred_service: Optional[AIServiceConfig] = None
    
    def detect_services(self) -> List[AIServiceConfig]:
        """检测所有可用的AI服务"""
        self.services = []
        
        # 检测Ollama
        ollama_configs = [
            ("Ollama-qwen2.5", APIType.OLLAMA, "http://localhost:11434/api/generate", "qwen2.5:3b", 32000),
            ("Ollama-llama3.2", APIType.OLLAMA, "http://localhost:11434/api/generate", "llama3.2:3b", 32000),
            ("Ollama-gemma2", APIType.OLLAMA, "http://localhost:11434/api/generate", "gemma2:2b", 32000),
        ]
        
        for name, api_type, url, model, context_limit in ollama_configs:
            config = AIServiceConfig(name, api_type, url, model, context_limit)
            if self._test_ollama_service(config):
                self.services.append(config)
        
        # 检测LM Studio
        lm_studio_configs = [
            ("LM-Studio", APIType.LM_STUDIO, "http://localhost:1234/v1/chat/completions", "auto", 128000),
        ]
        
        for name, api_type, url, model, context_limit in lm_studio_configs:
            config = AIServiceConfig(name, api_type, url, model, context_limit)
            if self._test_lm_studio_service(config):
                self.services.append(config)
        
        # 选择首选服务
        if self.services:
            # 优先选择响应时间最快的服务
            self.preferred_service = min(self.services, key=lambda s: s.response_time)
        
        return self.services
    
    def _test_ollama_service(self, config: AIServiceConfig) -> bool:
        """测试Ollama服务"""
        try:
            start_time = time.time()
            
            # 首先检查模型是否存在
            list_url = config.base_url.replace('/api/generate', '/api/tags')
            response = requests.get(list_url, timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                if config.model_name not in model_names:
                    config.error_message = f"模型 {config.model_name} 不存在。可用模型: {', '.join(model_names)}"
                    return False
            
            # 测试生成请求
            test_payload = {
                'model': config.model_name,
                'prompt': '你好',
                'stream': False,
                'options': {'num_predict': 10}
            }
            
            response = requests.post(config.base_url, json=test_payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if 'response' in result:
                config.available = True
                config.response_time = time.time() - start_time
                return True
            else:
                config.error_message = "响应格式错误"
                return False
                
        except requests.exceptions.ConnectionError:
            config.error_message = "连接失败 - 请确认Ollama正在运行"
            return False
        except requests.exceptions.Timeout:
            config.error_message = "请求超时"
            return False
        except Exception as e:
            config.error_message = f"测试失败: {str(e)}"
            return False
    
    def _test_lm_studio_service(self, config: AIServiceConfig) -> bool:
        """测试LM Studio服务"""
        try:
            start_time = time.time()
            
            test_payload = {
                'model': config.model_name,
                'messages': [{'role': 'user', 'content': '你好'}],
                'max_tokens': 10,
                'stream': False
            }
            
            response = requests.post(config.base_url, json=test_payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                config.available = True
                config.response_time = time.time() - start_time
                return True
            else:
                config.error_message = "响应格式错误"
                return False
                
        except requests.exceptions.ConnectionError:
            config.error_message = "连接失败 - 请确认LM Studio正在运行且已加载模型"
            return False
        except requests.exceptions.Timeout:
            config.error_message = "请求超时"
            return False
        except Exception as e:
            config.error_message = f"测试失败: {str(e)}"
            return False
    
    def get_preferred_service(self) -> Optional[AIServiceConfig]:
        """获取首选AI服务"""
        return self.preferred_service
    
    def get_available_services(self) -> List[AIServiceConfig]:
        """获取所有可用服务"""
        return [s for s in self.services if s.available]
    
    def print_service_status(self):
        """打印服务状态"""
        print("=" * 60)
        print("AI服务检测结果")
        print("=" * 60)
        
        if not self.services:
            print("❌ 未检测到任何AI服务")
            self._print_setup_instructions()
            return
        
        available_count = len(self.get_available_services())
        print(f"检测到 {len(self.services)} 个服务，其中 {available_count} 个可用\n")
        
        for service in self.services:
            status = "✅ 可用" if service.available else "❌ 不可用"
            print(f"{status} {service.name}")
            print(f"   模型: {service.model_name}")
            print(f"   地址: {service.base_url}")
            
            if service.available:
                print(f"   响应时间: {service.response_time:.2f}s")
                print(f"   上下文限制: {service.context_limit}")
            else:
                print(f"   错误: {service.error_message}")
            print()
        
        if self.preferred_service:
            print(f"🌟 推荐服务: {self.preferred_service.name}")
        else:
            print("⚠️  没有可用的AI服务")
            self._print_setup_instructions()
    
    def _print_setup_instructions(self):
        """打印设置说明"""
        print("\n" + "=" * 60)
        print("AI服务设置说明")
        print("=" * 60)
        print("""
1. Ollama 设置:
   安装: curl -fsSL https://ollama.ai/install.sh | sh
   启动: ollama serve
   下载模型: ollama pull qwen2.5:3b
   
2. LM Studio 设置:
   下载: https://lmstudio.ai/
   启动后在本地服务器标签页启动服务
   确保端口设置为 1234
   
3. 测试连接:
   python3 -c "from Agent.config.ai_config import AIServiceDetector; AIServiceDetector().detect_services()"
""")


def detect_and_configure_ai() -> Optional[AIServiceConfig]:
    """检测并配置AI服务"""
    detector = AIServiceDetector()
    detector.detect_services()
    detector.print_service_status()
    return detector.get_preferred_service()


def create_ai_client_from_config(config: AIServiceConfig):
    """从配置创建AI客户端"""
    from Agent.client.model_client import ModelClient
    
    return ModelClient(
        model_name=config.model_name,
        api_type=config.api_type,
        base_url=config.base_url,
        context_limit=config.context_limit
    )


if __name__ == "__main__":
    # 命令行测试
    detect_and_configure_ai()