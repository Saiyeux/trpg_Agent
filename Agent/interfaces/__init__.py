"""
接口层模块

定义系统各功能模块的统一接口规范，支持插件化架构。
通过接口抽象实现模块间的解耦，便于扩展和替换实现。
"""

__version__ = "1.0.0"

from .memory_interface import MemoryInterface

__all__ = [
    'MemoryInterface'
]