"""
真实实现模块

包含所有接口的真实实现类。
"""

from .execution_engine import RealExecutionEngine, AttackFunction, SearchFunction
from .model_bridge import RealModelBridge, SimpleContextManager, TRPGPromptTemplate

__all__ = [
    'RealExecutionEngine',
    'AttackFunction', 
    'SearchFunction',
    'RealModelBridge',
    'SimpleContextManager',
    'TRPGPromptTemplate'
]