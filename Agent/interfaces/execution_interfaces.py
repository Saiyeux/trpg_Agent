"""
执行引擎接口定义

定义Layer 2执行引擎层的所有接口，包括执行引擎、Function库、
RAG检索等核心组件的抽象接口。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Type, Callable
from .data_structures import Intent, ExecutionResult, StateChange


class GameFunction(ABC):
    """
    游戏Function基类
    
    所有游戏Function都必须继承此类并实现核心方法。
    这是系统扩展性的核心接口。
    """
    
    @abstractmethod
    def can_execute(self, intent: Intent, game_state: 'GameState') -> bool:
        """
        检查是否可以执行此Function
        
        Args:
            intent: 玩家意图对象
            game_state: 当前游戏状态
            
        Returns:
            bool: 是否可以执行
        """
        pass
    
    @abstractmethod
    def execute(self, intent: Intent, game_state: 'GameState') -> ExecutionResult:
        """
        执行Function逻辑
        
        Args:
            intent: 玩家意图对象
            game_state: 当前游戏状态
            
        Returns:
            ExecutionResult: 执行结果
        """
        pass
    
    def get_priority(self) -> int:
        """
        获取Function优先级
        
        Returns:
            int: 优先级数值，越高优先级越高
        """
        return 5
    
    def get_description(self) -> str:
        """
        获取Function描述
        
        Returns:
            str: Function功能描述
        """
        return self.__class__.__name__
    
    def get_categories(self) -> List[str]:
        """
        获取支持的意图分类
        
        Returns:
            List[str]: 支持的分类列表
        """
        return []
    
    def get_targets(self) -> List[str]:
        """
        获取支持的目标类型
        
        Returns:
            List[str]: 支持的目标列表
        """
        return []


class FunctionMetadata:
    """Function元数据"""
    def __init__(self, category: str, targets: List[str] = None, 
                 keywords: List[str] = None, priority: int = 5):
        self.category = category
        self.targets = targets or []
        self.keywords = keywords or []
        self.priority = priority


class FunctionRegistry(ABC):
    """
    Function注册表接口
    
    管理系统中所有可用的Function，支持动态注册和查询。
    """
    
    @abstractmethod
    def register(self, function_class: Type[GameFunction], 
                metadata: FunctionMetadata) -> None:
        """
        注册Function
        
        Args:
            function_class: Function类
            metadata: Function元数据
        """
        pass
    
    @abstractmethod
    def unregister(self, name: str) -> bool:
        """
        注销Function
        
        Args:
            name: Function名称
            
        Returns:
            bool: 是否成功注销
        """
        pass
    
    @abstractmethod
    def get_function(self, name: str) -> Optional[Type[GameFunction]]:
        """
        获取指定Function
        
        Args:
            name: Function名称
            
        Returns:
            Optional[Type[GameFunction]]: Function类或None
        """
        pass
    
    @abstractmethod
    def get_all_functions(self) -> Dict[str, Type[GameFunction]]:
        """
        获取所有已注册的Function
        
        Returns:
            Dict[str, Type[GameFunction]]: Function字典
        """
        pass
    
    @abstractmethod
    def get_functions_by_category(self, category: str) -> List[Type[GameFunction]]:
        """
        根据分类获取Function
        
        Args:
            category: 分类名称
            
        Returns:
            List[Type[GameFunction]]: Function列表
        """
        pass


class FunctionRetriever(ABC):
    """
    Function检索接口
    
    基于Intent检索最匹配的Function，支持RAG增强的智能匹配。
    """
    
    @abstractmethod
    def query_functions(self, intent: Intent, 
                       game_state: 'GameState' = None, 
                       top_k: int = 5) -> List[GameFunction]:
        """
        检索匹配的Function
        
        Args:
            intent: 玩家意图
            game_state: 当前游戏状态
            top_k: 返回的最大Function数量
            
        Returns:
            List[GameFunction]: 匹配的Function实例列表(按优先级排序)
        """
        pass
    
    @abstractmethod
    def update_function_performance(self, function_name: str, 
                                  intent: Intent, success: bool) -> None:
        """
        更新Function执行性能统计
        
        Args:
            function_name: Function名称
            intent: 相关Intent
            success: 执行是否成功
        """
        pass


class ExecutionEngine(ABC):
    """
    执行引擎接口
    
    Layer 2的核心接口，协调意图解析、Function检索、执行和状态更新。
    """
    
    @abstractmethod
    def process(self, intent: Intent, game_state: 'GameState') -> ExecutionResult:
        """
        处理玩家意图并返回执行结果
        
        Args:
            intent: 玩家意图对象
            game_state: 当前游戏状态
            
        Returns:
            ExecutionResult: 执行结果
        """
        pass
    
    @abstractmethod
    def register_function(self, function_class: Type[GameFunction], 
                         metadata: FunctionMetadata = None) -> None:
        """
        注册新的Function
        
        Args:
            function_class: Function类
            metadata: Function元数据
        """
        pass
    
    @abstractmethod
    def get_supported_categories(self) -> List[str]:
        """
        获取支持的意图分类
        
        Returns:
            List[str]: 支持的分类列表
        """
        pass


# Function装饰器，便于注册
def register_function(category: str, targets: List[str] = None, 
                     keywords: List[str] = None, priority: int = 5):
    """
    Function注册装饰器
    
    使用示例:
    @register_function(category="攻击", targets=["敌人", "怪物"], priority=10)
    class AttackFunction(GameFunction):
        pass
    """
    def decorator(function_class: Type[GameFunction]):
        # 将元数据附加到类上
        function_class._metadata = FunctionMetadata(
            category=category,
            targets=targets or [],
            keywords=keywords or [],
            priority=priority
        )
        return function_class
    return decorator


# 事务处理接口
class StateTransaction(ABC):
    """
    状态事务接口
    
    确保状态变更的原子性和一致性。
    """
    
    @abstractmethod
    def begin(self) -> None:
        """开始事务"""
        pass
    
    @abstractmethod
    def add_change(self, change: StateChange) -> None:
        """添加状态变更"""
        pass
    
    @abstractmethod
    def commit(self) -> bool:
        """提交事务"""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """回滚事务"""
        pass
    
    @abstractmethod
    def get_changes(self) -> List[StateChange]:
        """获取所有变更"""
        pass


# 执行上下文
class ExecutionContext:
    """
    执行上下文
    
    在Function执行过程中提供必要的上下文信息。
    """
    def __init__(self, intent: Intent, game_state: 'GameState', 
                 transaction: StateTransaction):
        self.intent = intent
        self.game_state = game_state
        self.transaction = transaction
        self.metadata: Dict[str, Any] = {}
    
    def add_metadata(self, key: str, value: Any) -> None:
        """添加执行元数据"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取执行元数据"""
        return self.metadata.get(key, default)