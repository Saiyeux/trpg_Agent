"""
AI-TRPG 核心模块

包含游戏引擎和状态管理的核心组件。
"""

from .game_engine import GameEngine
from .game_state import GameState

__all__ = ['GameEngine', 'GameState']