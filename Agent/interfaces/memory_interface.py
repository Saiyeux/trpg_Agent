"""
记忆接口定义

定义统一的记忆查询接口，支持多种RAG后端实现。
提供对话存储、历史检索和上下文增强功能的抽象接口。

主要功能:
- 对话数据存储
- 语义检索查询  
- 上下文摘要生成
- 跨会话记忆管理
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ConversationTurn:
    """单轮对话数据结构"""
    user_input: str
    ai_response: str
    turn: int
    timestamp: str
    scene: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass 
class RetrievalResult:
    """检索结果数据结构"""
    content: str
    relevance: float
    turn: int
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class MemoryInterface(ABC):
    """
    统一记忆查询接口
    
    定义所有RAG实现必须遵循的接口规范。
    支持路径配置、按需调用和容错处理。
    """
    
    @staticmethod
    @abstractmethod
    def store_turn(storage_path: str, turn_data: ConversationTurn) -> bool:
        """
        存储单轮对话数据
        
        Args:
            storage_path: 存储路径，如 "storage/session_20250910_143022"
            turn_data: 对话轮次数据
            
        Returns:
            bool: 存储是否成功
            
        调用时机: 每轮对话完成后
        """
        pass
    
    @staticmethod
    @abstractmethod
    def query_relevant(storage_path: str, query: str, limit: int = 3) -> List[RetrievalResult]:
        """
        查询相关历史记录
        
        Args:
            storage_path: 存储路径
            query: 查询内容（用户输入或关键词）
            limit: 返回结果数量限制
            
        Returns:
            List[RetrievalResult]: 相关度排序的检索结果列表
            
        调用时机: 生成回复时增强上下文
        """
        pass
    
    @staticmethod
    @abstractmethod  
    def get_recent_context(storage_path: str, turns: int = 5) -> str:
        """
        获取最近N轮的上下文摘要
        
        Args:
            storage_path: 存储路径
            turns: 获取的轮次数量
            
        Returns:
            str: 格式化的上下文摘要字符串
            
        调用时机: 生成场景时提供背景信息
        """
        pass
    
    @staticmethod
    @abstractmethod
    def initialize_storage(storage_path: str) -> bool:
        """
        初始化存储路径
        
        Args:
            storage_path: 存储路径
            
        Returns:
            bool: 初始化是否成功
            
        调用时机: 游戏会话开始时
        """
        pass
    
    @staticmethod
    @abstractmethod
    def storage_exists(storage_path: str) -> bool:
        """
        检查存储路径是否存在
        
        Args:
            storage_path: 存储路径
            
        Returns:
            bool: 存储是否存在
            
        调用时机: 加载已有会话时
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_storage_stats(storage_path: str) -> Dict[str, Any]:
        """
        获取存储统计信息
        
        Args:
            storage_path: 存储路径
            
        Returns:
            Dict[str, Any]: 统计信息，包含总轮数、存储大小等
            
        调用时机: 显示游戏统计时
        """
        pass