"""
API模块

提供TRPG系统的RESTful API接口，供前端页面和客户端应用使用。

主要功能:
- 对话历史查询和展示
- 多格式数据导出
- 会话管理和统计
- 搜索和过滤功能
"""

__version__ = "1.0.0"

from .conversation_api import ConversationAPI

__all__ = [
    'ConversationAPI'
]