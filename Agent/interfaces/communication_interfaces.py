"""
模型间通信接口定义

定义Layer间通信的标准接口，包括消息格式、上下文管理、
ModelBridge等核心通信组件。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from .data_structures import Intent, ExecutionResult


@dataclass
class IntentMessage:
    """
    意图消息 - Layer 1 到 Layer 2 的消息格式
    """
    intent: Intent                      # 识别出的意图
    confidence: float                   # 识别置信度
    raw_input: str                      # 原始用户输入
    context: Dict[str, Any] = field(default_factory=dict)  # 上下文信息
    timestamp: float = 0.0              # 时间戳
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'intent': self.intent.to_dict(),
            'confidence': self.confidence,
            'raw_input': self.raw_input,
            'context': self.context,
            'timestamp': self.timestamp
        }


@dataclass
class ExecutionMessage:
    """
    执行消息 - Layer 2 到 Layer 3 的消息格式
    """
    execution_result: ExecutionResult   # 执行结果
    original_intent: Intent             # 原始意图
    game_state_snapshot: Dict[str, Any] = field(default_factory=dict)  # 状态快照
    rag_context: str = ""              # RAG检索的相关上下文
    timestamp: float = 0.0              # 时间戳
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'execution_result': self.execution_result.to_dict(),
            'original_intent': self.original_intent.to_dict(),
            'game_state_snapshot': self.game_state_snapshot,
            'rag_context': self.rag_context,
            'timestamp': self.timestamp
        }


@dataclass  
class ErrorMessage:
    """
    错误消息 - 跨Layer的错误处理消息
    """
    layer: str                          # 出错的层级
    error_type: str                     # 错误类型
    message: str                        # 错误描述
    fallback_data: Any = None          # 降级数据
    original_input: str = ""            # 原始输入
    timestamp: float = 0.0              # 时间戳


class ContextManager(ABC):
    """
    上下文管理器接口
    
    负责构建和管理各Layer间传递的上下文信息。
    """
    
    @abstractmethod
    def build_intent_context(self, user_input: str, 
                           game_state: 'GameState') -> Dict[str, Any]:
        """
        构建意图识别的上下文
        
        Args:
            user_input: 用户输入
            game_state: 当前游戏状态
            
        Returns:
            Dict[str, Any]: 上下文字典
        """
        pass
    
    @abstractmethod
    def build_execution_context(self, intent: Intent, 
                              game_state: 'GameState') -> Dict[str, Any]:
        """
        构建执行引擎的上下文
        
        Args:
            intent: 玩家意图
            game_state: 当前游戏状态
            
        Returns:
            Dict[str, Any]: 上下文字典
        """
        pass
    
    @abstractmethod
    def build_scene_context(self, execution_result: ExecutionResult,
                          intent: Intent, game_state: 'GameState') -> Dict[str, Any]:
        """
        构建场景生成的上下文
        
        Args:
            execution_result: 执行结果
            intent: 原始意图
            game_state: 当前游戏状态
            
        Returns:
            Dict[str, Any]: 上下文字典
        """
        pass
    
    @abstractmethod
    def get_history_context(self, game_state: 'GameState', 
                          limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取历史上下文
        
        Args:
            game_state: 游戏状态
            limit: 历史记录数量限制
            
        Returns:
            List[Dict[str, Any]]: 历史记录列表
        """
        pass


class PromptTemplate(ABC):
    """
    Prompt模板接口
    
    管理各个AI模型的Prompt模板。
    """
    
    @abstractmethod
    def get_intent_recognition_prompt(self, user_input: str, 
                                    context: Dict[str, Any]) -> str:
        """获取意图识别的Prompt"""
        pass
    
    @abstractmethod
    def get_scene_generation_prompt(self, execution_message: ExecutionMessage) -> str:
        """获取场景生成的Prompt"""
        pass
    
    @abstractmethod
    def format_execution_result(self, execution_result: ExecutionResult) -> str:
        """格式化执行结果用于Prompt"""
        pass


class ModelBridge(ABC):
    """
    模型桥接器接口
    
    协调三个Layer间的通信和数据流。
    """
    
    @abstractmethod
    def process_user_input(self, user_input: str) -> str:
        """
        处理用户输入的完整流程
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            str: 最终回复给用户的文本
        """
        pass
    
    @abstractmethod
    def classify_intent(self, user_input: str) -> IntentMessage:
        """
        Layer 1: 意图分类
        
        Args:
            user_input: 用户输入
            
        Returns:
            IntentMessage: 意图消息
        """
        pass
    
    @abstractmethod
    def execute_intent(self, intent_message: IntentMessage) -> ExecutionMessage:
        """
        Layer 2: 意图执行
        
        Args:
            intent_message: 意图消息
            
        Returns:
            ExecutionMessage: 执行消息
        """
        pass
    
    @abstractmethod
    def generate_scene(self, execution_message: ExecutionMessage) -> str:
        """
        Layer 3: 场景生成
        
        Args:
            execution_message: 执行消息
            
        Returns:
            str: 生成的场景文本
        """
        pass
    
    @abstractmethod
    def handle_error(self, error: ErrorMessage) -> str:
        """
        错误处理
        
        Args:
            error: 错误消息
            
        Returns:
            str: 错误回复文本
        """
        pass


class AsyncModelBridge(ModelBridge):
    """
    异步模型桥接器接口
    
    支持异步处理和并行优化。
    """
    
    @abstractmethod
    async def process_user_input_async(self, user_input: str) -> str:
        """异步处理用户输入"""
        pass
    
    @abstractmethod
    async def classify_intent_async(self, user_input: str) -> IntentMessage:
        """异步意图分类"""
        pass
    
    @abstractmethod
    async def execute_intent_async(self, intent_message: IntentMessage) -> ExecutionMessage:
        """异步意图执行"""
        pass
    
    @abstractmethod
    async def generate_scene_async(self, execution_message: ExecutionMessage) -> str:
        """异步场景生成"""
        pass


class MessageBus(ABC):
    """
    消息总线接口
    
    支持发布-订阅模式的消息传递。
    """
    
    @abstractmethod
    def publish(self, topic: str, message: Any) -> None:
        """发布消息"""
        pass
    
    @abstractmethod
    def subscribe(self, topic: str, callback: callable) -> None:
        """订阅消息"""
        pass
    
    @abstractmethod
    def unsubscribe(self, topic: str, callback: callable) -> None:
        """取消订阅"""
        pass


class CacheManager(ABC):
    """
    缓存管理器接口
    
    管理各种计算结果的缓存。
    """
    
    @abstractmethod
    def get_intent_cache(self, user_input: str) -> Optional[Intent]:
        """获取意图识别缓存"""
        pass
    
    @abstractmethod
    def set_intent_cache(self, user_input: str, intent: Intent) -> None:
        """设置意图识别缓存"""
        pass
    
    @abstractmethod
    def get_execution_cache(self, intent: Intent) -> Optional[ExecutionResult]:
        """获取执行结果缓存"""
        pass
    
    @abstractmethod
    def set_execution_cache(self, intent: Intent, result: ExecutionResult) -> None:
        """设置执行结果缓存"""
        pass
    
    @abstractmethod
    def clear_cache(self) -> None:
        """清空所有缓存"""
        pass


class MetricsCollector(ABC):
    """
    性能指标收集器接口
    
    收集系统运行的各种性能指标。
    """
    
    @abstractmethod
    def record_intent_classification_time(self, duration: float) -> None:
        """记录意图分类耗时"""
        pass
    
    @abstractmethod
    def record_execution_time(self, function_name: str, duration: float) -> None:
        """记录Function执行耗时"""
        pass
    
    @abstractmethod
    def record_scene_generation_time(self, duration: float) -> None:
        """记录场景生成耗时"""
        pass
    
    @abstractmethod
    def record_total_response_time(self, duration: float) -> None:
        """记录总响应时间"""
        pass
    
    @abstractmethod
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        pass