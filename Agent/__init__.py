"""
AI-TRPG: 基于大语言模型的桌游角色扮演游戏系统

一个支持多种AI模型的TRPG游戏引擎，具备意图识别、场景生成和游戏状态管理功能。
支持Ollama和LM Studio两种AI后端，可配置不同模型以获得最佳游戏体验。

主要特性:
- 智能意图识别和分类
- 动态场景生成
- 完整的游戏状态追踪
- 多AI后端支持
- 详细的游戏日志记录
- 可配置的上下文管理

作者: AI Assistant
版本: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"

from .core.game_engine import GameEngine
from .core.game_state import GameState
from .client.model_client import ModelClient
from .utils.intent_analyzer import IntentAnalyzer
from .utils.logger import GameLogger
from .config.settings import ConfigManager

__all__ = [
    'GameEngine',
    'GameState', 
    'ModelClient',
    'IntentAnalyzer',
    'GameLogger',
    'ConfigManager'
]