"""
配置管理模块

负责TRPG系统的配置文件管理，支持多种AI后端和灵活的参数配置。
提供交互式配置和配置验证功能。

主要功能:
- 配置文件加载和保存
- 多AI后端配置管理
- 交互式配置设置
- 配置验证和默认值
"""

import json
import os
from typing import Dict, Any, List, Optional
from ..client.model_client import APIType


class ConfigManager:
    """
    TRPG系统配置管理器
    
    管理系统的所有配置选项，包括AI后端设置、游戏参数、日志配置等。
    支持配置文件的加载、保存和交互式设置。
    """
    
    def __init__(self, config_file: str = "config/game_config.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
        
    def get_api_type(self) -> APIType:
        """
        获取当前配置的API类型
        
        Returns:
            API类型枚举
            
        调用时机: 初始化AI客户端时
        """
        api_type_str = self.config["api"]["type"]
        return APIType.OLLAMA if api_type_str == "ollama" else APIType.LM_STUDIO
        
    def get_api_config(self) -> Dict[str, Any]:
        """
        获取当前API的配置信息
        
        Returns:
            包含API配置的字典
            
        调用时机: 初始化AI客户端时
        """
        api_type = self.get_api_type()
        config_key = api_type.value
        api_config = self.config[config_key].copy()
        
        # 对于LM Studio，模型名称设为固定值，因为它使用当前加载的模型
        if api_type == APIType.LM_STUDIO:
            api_config["model"] = "current_loaded_model"
            
        return api_config
        
    def get_game_config(self) -> Dict[str, Any]:
        """
        获取游戏相关配置
        
        Returns:
            游戏配置字典
            
        调用时机: 初始化游戏引擎时
        """
        return self.config["game"].copy()
        
    def get_logging_config(self) -> Dict[str, Any]:
        """
        获取日志相关配置
        
        Returns:
            日志配置字典
            
        调用时机: 初始化日志系统时
        """
        return self.config.get("logging", self._get_default_logging_config())
    
    def get_rag_config(self) -> Dict[str, Any]:
        """
        获取RAG相关配置
        
        Returns:
            RAG配置字典
            
        调用时机: 初始化RAG系统时
        """
        return self.config.get("rag", {
            "enabled": False,
            "type": "lightrag", 
            "storage_path": "storage/conversations",
            "auto_create_session": True,
            "query_limit": 3,
            "context_turns": 5
        })
        
    def set_rag_enabled(self, enabled: bool) -> None:
        """
        启用或禁用RAG功能
        
        Args:
            enabled: 是否启用RAG
            
        调用时机: 用户切换RAG功能时
        """
        if "rag" not in self.config:
            self.config["rag"] = self.get_rag_config()
        self.config["rag"]["enabled"] = enabled
        self._save_config()
        print(f"RAG功能已{'启用' if enabled else '禁用'}")
        
    def set_api_type(self, api_type: APIType) -> None:
        """
        设置API类型
        
        Args:
            api_type: 新的API类型
            
        调用时机: 用户切换AI后端时
        """
        self.config["api"]["type"] = api_type.value
        self._save_config()
        print(f"已切换到 {api_type.value}")
        
    def set_ollama_model(self, model_name: str) -> None:
        """
        设置Ollama模型
        
        Args:
            model_name: 模型名称
            
        调用时机: 用户切换Ollama模型时
        """
        if model_name not in self.config["ollama"]["available_models"]:
            print(f"警告: {model_name} 不在推荐模型列表中")
            
        self.config["ollama"]["model"] = model_name
        self._save_config()
        print(f"Ollama模型已设置为: {model_name}")
        
    def add_ollama_model(self, model_name: str) -> None:
        """
        添加新的Ollama模型到可用列表
        
        Args:
            model_name: 模型名称
            
        调用时机: 用户安装了新模型时
        """
        if model_name not in self.config["ollama"]["available_models"]:
            self.config["ollama"]["available_models"].append(model_name)
            self._save_config()
            print(f"已添加模型: {model_name}")
        else:
            print(f"模型 {model_name} 已存在")
            
    def display_config(self) -> None:
        """
        在控制台显示当前配置
        
        调用时机: 游戏开始或用户查询配置时
        """
        api_type = self.get_api_type()
        api_config = self.get_api_config()
        
        print(f"\n=== 当前配置 ===")
        print(f"API类型: {api_type.value}")
        print(f"模型: {api_config['model']}")
        print(f"服务地址: {api_config['base_url']}")
        print(f"AI上下文限制: {api_config['context_limit']} tokens")
        
        if api_type == APIType.LM_STUDIO:
            print("注意: LM Studio使用当前界面加载的模型")
            
        game_config = self.get_game_config()
        rag_config = self.get_rag_config()
        
        print(f"即时上下文: {game_config['context_history_limit']} 轮")
        
        # 显示RAG状态
        if rag_config.get('enabled'):
            print(f"🧠 长期记忆: 已启用 ({rag_config['type']})")
            print(f"   存储路径: {rag_config['storage_path']}")
        else:
            print("🧠 长期记忆: 未启用")
            
        print("=" * 25)
        
    def interactive_setup(self) -> None:
        """
        交互式配置设置
        
        调用时机: 首次使用或用户主动配置时
        """
        print("=== AI-TRPG 系统配置 ===")
        print("选择AI后端:")
        print("1. Ollama (本地模型服务，支持多模型切换)")
        print("2. LM Studio (图形界面管理，高质量模型)")
        
        while True:
            choice = input("\n请选择 (1-2): ").strip()
            
            if choice == "1":
                self._setup_ollama()
                break
            elif choice == "2":
                self._setup_lm_studio()
                break
            else:
                print("无效选择，请输入1或2")
                
        # 设置游戏参数
        self._setup_game_config()
        
        print("\n配置完成！")
        self.display_config()
        
    def validate_config(self) -> List[str]:
        """
        验证配置的有效性
        
        Returns:
            配置错误列表，空列表表示配置有效
            
        调用时机: 系统启动前或配置更新后
        """
        errors = []
        
        # 验证API配置
        api_type = self.get_api_type()
        api_config = self.config[api_type.value]
        
        if not api_config.get("base_url"):
            errors.append(f"{api_type.value} base_url 不能为空")
            
        if api_config.get("context_limit", 0) <= 0:
            errors.append(f"{api_type.value} context_limit 必须大于0")
            
        # 验证游戏配置
        game_config = self.config.get("game", {})
        if game_config.get("context_history_limit", 0) <= 0:
            errors.append("游戏配置中 context_history_limit 必须大于0")
            
        return errors
        
    def reset_to_defaults(self) -> None:
        """
        重置为默认配置
        
        调用时机: 配置损坏或用户要求重置时
        """
        self.config = self._get_default_config()
        self._save_config()
        print("配置已重置为默认值")
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 验证加载的配置
            if self._is_valid_config_structure(config):
                return config
            else:
                print("配置文件结构异常，使用默认配置")
                return self._get_default_config()
                
        except (FileNotFoundError, json.JSONDecodeError):
            print("配置文件不存在或格式错误，创建默认配置")
            default_config = self._get_default_config()
            self._save_config_dict(default_config)
            return default_config
            
    def _save_config(self) -> None:
        """保存当前配置到文件"""
        self._save_config_dict(self.config)
        
    def _save_config_dict(self, config_dict: Dict[str, Any]) -> None:
        """保存指定配置字典到文件"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "api": {
                "type": "ollama",
                "comment": "可选: ollama 或 lm_studio"
            },
            "ollama": {
                "base_url": "http://localhost:11434/api/generate",
                "model": "qwen2.5:3b",
                "context_limit": 32000,
                "available_models": [
                    "qwen2.5:3b",
                    "qwen2.5:7b", 
                    "llama3.1:8b",
                    "gemma2:9b"
                ]
            },
            "lm_studio": {
                "base_url": "http://localhost:1234/v1/chat/completions",
                "model": "current_loaded",
                "context_limit": 128000,
                "note": "模型名称无关紧要，LM Studio自动使用当前加载的模型",
                "recommended_models": [
                    "hermes-3-llama-3.1-8b",
                    "hermes-3-llama-3.1-70b", 
                    "nous-hermes-2-mixtral-8x7b",
                    "qwen2.5-coder-32b-instruct"
                ]
            },
            "game": {
                "context_history_limit": 3,
                "auto_adjust_context": True,
                "max_turns": 1000
            },
            "rag": {
                "enabled": False,
                "type": "lightrag",
                "storage_path": "storage/conversations",
                "auto_create_session": True,
                "query_limit": 3,
                "context_turns": 5
            },
            "logging": {
                "log_file": "logs/trpg_game.log",
                "log_level": "INFO",
                "enable_console_output": True
            }
        }
        
    def _get_default_logging_config(self) -> Dict[str, Any]:
        """获取默认日志配置"""
        return {
            "log_file": "logs/trpg_game.log",
            "log_level": "INFO", 
            "enable_console_output": True
        }
        
    def _is_valid_config_structure(self, config: Dict[str, Any]) -> bool:
        """检查配置结构是否有效"""
        required_keys = ["api", "ollama", "lm_studio", "game"]
        return all(key in config for key in required_keys)
        
    def _setup_ollama(self) -> None:
        """设置Ollama配置"""
        self.set_api_type(APIType.OLLAMA)
        
        available_models = self.config["ollama"]["available_models"]
        current_model = self.config["ollama"]["model"]
        
        print(f"\n可用模型: {', '.join(available_models)}")
        print(f"当前模型: {current_model}")
        
        new_model = input("选择新模型 (回车跳过): ").strip()
        if new_model:
            self.set_ollama_model(new_model)
            
    def _setup_lm_studio(self) -> None:
        """设置LM Studio配置"""
        self.set_api_type(APIType.LM_STUDIO)
        
        recommended = self.config["lm_studio"]["recommended_models"]
        print(f"\n推荐模型: {', '.join(recommended[:3])}...")
        print("请确保LM Studio已启动并加载了模型")
        
        # 可选择性设置端口
        current_url = self.config["lm_studio"]["base_url"]
        print(f"当前服务地址: {current_url}")
        
        new_url = input("自定义服务地址 (回车跳过): ").strip()
        if new_url:
            self.config["lm_studio"]["base_url"] = new_url
            self._save_config()
            
    def _setup_game_config(self) -> None:
        """设置游戏配置"""
        print("\n=== 游戏配置 ===")
        
        current_limit = self.config["game"]["context_history_limit"]
        print(f"当前历史记录限制: {current_limit}")
        
        new_limit = input("设置历史记录数量 (回车跳过): ").strip()
        if new_limit and new_limit.isdigit():
            self.config["game"]["context_history_limit"] = int(new_limit)
            self._save_config()
            print(f"已设置为: {new_limit}")
            
    def get_log_file_path(self) -> str:
        """获取日志文件路径"""
        return self.config.get("logging", {}).get("log_file", "logs/trpg_game.log")