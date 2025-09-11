"""
Mock框架

提供系统各组件的Mock实现，支持独立开发和渐进式集成测试。
遵循接口优先设计原则，确保Mock与真实实现的兼容性。
"""

from .mock_game_state import MockGameState, MockPlayerState, MockWorldState
from .mock_execution_engine import MockExecutionEngine, MockFunctionRegistry
from .mock_model_bridge import MockModelBridge, MockContextManager
from .integration_levels import IntegrationLevel

__all__ = [
    'MockGameState',
    'MockPlayerState', 
    'MockWorldState',
    'MockExecutionEngine',
    'MockFunctionRegistry',
    'MockModelBridge',
    'MockContextManager',
    'IntegrationLevel'
]