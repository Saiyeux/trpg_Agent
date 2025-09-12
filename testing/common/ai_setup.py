"""
AI服务设置和检查工具

复用项目中的AI配置逻辑，为测试提供统一的AI服务管理。
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

# 添加项目根目录到路径以导入Agent模块
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from Agent.config.ai_config import detect_and_configure_ai, create_ai_client_from_config
except ImportError:
    # 如果导入失败，提供占位符实现
    def detect_and_configure_ai():
        return None
    
    def create_ai_client_from_config(config):
        return None

class AISetupHelper:
    """AI服务设置助手"""
    
    def __init__(self):
        self.ai_config = None
        self.model_client = None
    
    def check_ai_availability(self) -> bool:
        """检查AI服务可用性"""
        try:
            print("🔍 检测AI服务可用性...")
            
            # 使用现有的AI配置检测逻辑
            self.ai_config = detect_and_configure_ai()
            
            if not self.ai_config:
                print("❌ 没有检测到可用的AI服务")
                print("请确保以下服务之一正在运行:")
                print("  • Ollama (http://localhost:11434)")
                print("  • LM Studio (http://localhost:1234)")
                return False
            
            print(f"✅ 检测到AI服务: {self.ai_config.name}")
            print(f"   模型: {self.ai_config.model_name}")
            print(f"   地址: {self.ai_config.base_url}")
            
            # 创建客户端
            self.model_client = create_ai_client_from_config(self.ai_config)
            return True
            
        except Exception as e:
            print(f"❌ AI服务检测失败: {str(e)}")
            return False
    
    def get_ai_config(self):
        """获取AI配置"""
        return self.ai_config
    
    def get_model_client(self):
        """获取模型客户端"""
        return self.model_client
    
    def test_ai_connection(self) -> bool:
        """测试AI连接"""
        if not self.model_client:
            return False
        
        try:
            # 发送简单的测试请求
            test_prompt = "测试连接。请回复：连接正常"
            response = self.model_client._make_request(test_prompt, "连接测试")
            
            if response and "连接正常" in response:
                print("✅ AI连接测试通过")
                return True
            else:
                print("⚠️  AI连接测试响应异常")
                return False
                
        except Exception as e:
            print(f"❌ AI连接测试失败: {str(e)}")
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        if not self.ai_config:
            return {}
        
        return {
            "name": getattr(self.ai_config, 'name', 'Unknown'),
            "model": getattr(self.ai_config, 'model_name', 'Unknown'),
            "endpoint": getattr(self.ai_config, 'base_url', 'Unknown'),
            "context_limit": getattr(self.ai_config, 'context_limit', 'Unknown')
        }