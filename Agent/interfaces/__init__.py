"""
TRPG多模型分工系统核心接口定义

这个模块定义了系统中所有核心数据结构和接口，
遵循"接口优先设计"原则，确保模块间的契约稳定。

Phase 0 接口定义 - ✅ 验证完成
所有接口兼容性测试通过，可以进入Phase 1实现阶段。
"""

__version__ = "2.0.0"

from .data_structures import (
    Intent,
    ExecutionResult,
    StateChange,
    DiceRoll,
    Concept,
    IntentType
)

from .execution_interfaces import (
    ExecutionEngine,
    GameFunction,
    FunctionRegistry,
    FunctionRetriever,
    FunctionMetadata,
    StateTransaction,
    ExecutionContext,
    register_function
)

from .state_interfaces import (
    GameState,
    PlayerState,
    WorldState,
    ConceptRegistry,
    Item,
    StatusEffect,
    Location,
    NPC,
    StateValidator,
    StateEventListener
)

from .communication_interfaces import (
    IntentMessage,
    ExecutionMessage,
    ErrorMessage,
    ContextManager,
    PromptTemplate,
    ModelBridge,
    AsyncModelBridge,
    MessageBus,
    CacheManager,
    MetricsCollector
)

# 保持向后兼容
from .memory_interface import MemoryInterface

__all__ = [
    # 核心数据结构
    'Intent',
    'ExecutionResult', 
    'StateChange',
    'DiceRoll',
    'Concept',
    'IntentType',
    
    # 执行引擎接口
    'ExecutionEngine',
    'GameFunction',
    'FunctionRegistry',
    'FunctionRetriever',
    'FunctionMetadata',
    'StateTransaction',
    'ExecutionContext',
    'register_function',
    
    # 状态管理接口
    'GameState',
    'PlayerState',
    'WorldState',
    'ConceptRegistry',
    'Item',
    'StatusEffect',
    'Location',
    'NPC',
    'StateValidator',
    'StateEventListener',
    
    # 通信接口
    'IntentMessage',
    'ExecutionMessage',
    'ErrorMessage', 
    'ContextManager',
    'PromptTemplate',
    'ModelBridge',
    'AsyncModelBridge',
    'MessageBus',
    'CacheManager',
    'MetricsCollector',
    
    # 向后兼容
    'MemoryInterface'
]