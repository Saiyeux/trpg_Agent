"""
执行引擎Mock实现

提供ExecutionEngine、FunctionRegistry等的Mock实现，
支持可预测的执行结果和独立测试。
"""

from typing import Dict, List, Any, Optional, Type
import random

from Agent.interfaces.execution_interfaces import (
    ExecutionEngine, GameFunction, FunctionRegistry, FunctionRetriever,
    FunctionMetadata, StateTransaction, ExecutionContext
)
from Agent.interfaces.data_structures import (
    Intent, ExecutionResult, StateChange, DiceRoll, 
    create_successful_result, create_failed_result
)


class MockGameFunction(GameFunction):
    """Mock GameFunction基类"""
    
    def __init__(self, name: str, category: str, success_rate: float = 0.8):
        self.name = name
        self.category = category
        self.success_rate = success_rate
    
    def can_execute(self, intent: Intent, game_state: 'GameState') -> bool:
        return intent.category == self.category
    
    def execute(self, intent: Intent, game_state: 'GameState') -> ExecutionResult:
        # Mock执行逻辑，基于成功率随机决定结果
        success = random.random() < self.success_rate
        
        if success:
            return self._create_success_result(intent, game_state)
        else:
            return self._create_failure_result(intent, game_state)
    
    def _create_success_result(self, intent: Intent, game_state: 'GameState') -> ExecutionResult:
        """创建成功结果 - 子类可重写"""
        return create_successful_result(f"成功执行{self.category}行动: {intent.action}")
    
    def _create_failure_result(self, intent: Intent, game_state: 'GameState') -> ExecutionResult:
        """创建失败结果 - 子类可重写"""
        return create_failed_result(f"尝试{self.category}", f"{self.category}失败")


class MockAttackFunction(MockGameFunction):
    """Mock攻击Function"""
    
    def __init__(self):
        super().__init__("AttackFunction", "攻击", success_rate=0.75)
    
    def can_execute(self, intent: Intent, game_state: 'GameState') -> bool:
        # 检查目标是否存在且为敌人
        if not super().can_execute(intent, game_state):
            return False
        
        target_npc = game_state.world.get_npc(intent.target)
        return target_npc is not None and target_npc.type == "敌人" and target_npc.alive
    
    def _create_success_result(self, intent: Intent, game_state: 'GameState') -> ExecutionResult:
        # 模拟攻击计算
        hit_roll = DiceRoll("攻击检定", "d20", random.randint(1, 20), 2)
        damage_roll = DiceRoll("伤害", "d6", random.randint(1, 6), 1)
        
        # 创建状态变更
        damage_change = StateChange(
            target=f"npc_{intent.target}",
            action="modify",
            property="hp", 
            value=-damage_roll.total
        )
        
        return ExecutionResult(
            success=True,
            action_taken=f"攻击{intent.target}造成{damage_roll.total}点伤害",
            state_changes=[damage_change],
            dice_results=[hit_roll, damage_roll],
            world_changes=[f"{intent.target}受到攻击"]
        )


class MockSearchFunction(MockGameFunction):
    """Mock搜索Function"""
    
    def __init__(self):
        super().__init__("SearchFunction", "搜索", success_rate=0.9)
    
    def _create_success_result(self, intent: Intent, game_state: 'GameState') -> ExecutionResult:
        # 模拟搜索发现物品
        from Agent.interfaces.state_interfaces import Item
        
        found_item = Item(
            name="古老的钥匙",
            type="道具",
            description="一把生锈的钥匙，看起来很古老",
            quantity=1
        )
        
        item_change = StateChange(
            target="player",
            action="add",
            property="items",
            value=found_item
        )
        
        return ExecutionResult(
            success=True,
            action_taken=f"在{intent.target}中找到了{found_item.name}",
            state_changes=[item_change],
            world_changes=[f"{intent.target}已被搜索过"]
        )


class MockFunctionRegistry(FunctionRegistry):
    """Function注册表Mock实现"""
    
    def __init__(self):
        self.functions: Dict[str, Type[GameFunction]] = {}
        self.metadata: Dict[str, FunctionMetadata] = {}
        self._register_default_functions()
    
    def _register_default_functions(self):
        """注册默认的Mock Function"""
        self.register(
            MockAttackFunction,
            FunctionMetadata("攻击", ["敌人", "怪物", "哥布林"], ["攻击", "打击"], 10)
        )
        self.register(
            MockSearchFunction, 
            FunctionMetadata("搜索", ["书桌", "箱子", "房间"], ["搜索", "调查"], 8)
        )
    
    def register(self, function_class: Type[GameFunction], 
                metadata: FunctionMetadata) -> None:
        name = function_class.__name__
        self.functions[name] = function_class
        self.metadata[name] = metadata
    
    def unregister(self, name: str) -> bool:
        if name in self.functions:
            del self.functions[name]
            del self.metadata[name]
            return True
        return False
    
    def get_function(self, name: str) -> Optional[Type[GameFunction]]:
        return self.functions.get(name)
    
    def get_all_functions(self) -> Dict[str, Type[GameFunction]]:
        return self.functions.copy()
    
    def get_functions_by_category(self, category: str) -> List[Type[GameFunction]]:
        result = []
        for name, func_class in self.functions.items():
            if self.metadata[name].category == category:
                result.append(func_class)
        return result


class MockFunctionRetriever(FunctionRetriever):
    """Function检索Mock实现"""
    
    def __init__(self, registry: FunctionRegistry):
        self.registry = registry
        self.performance_stats: Dict[str, Dict[str, Any]] = {}
    
    def query_functions(self, intent: Intent, 
                       game_state: 'GameState' = None, 
                       top_k: int = 5) -> List[GameFunction]:
        # 简单的匹配逻辑：按分类精确匹配
        matching_classes = self.registry.get_functions_by_category(intent.category)
        
        # 创建Function实例
        functions = []
        for func_class in matching_classes:
            func_instance = func_class()
            if game_state is None or func_instance.can_execute(intent, game_state):
                functions.append(func_instance)
        
        # 按优先级排序
        functions.sort(key=lambda f: f.get_priority(), reverse=True)
        
        return functions[:top_k]
    
    def update_function_performance(self, function_name: str, 
                                  intent: Intent, success: bool) -> None:
        if function_name not in self.performance_stats:
            self.performance_stats[function_name] = {
                'total_calls': 0,
                'successful_calls': 0,
                'success_rate': 0.0
            }
        
        stats = self.performance_stats[function_name]
        stats['total_calls'] += 1
        if success:
            stats['successful_calls'] += 1
        stats['success_rate'] = stats['successful_calls'] / stats['total_calls']


class MockStateTransaction(StateTransaction):
    """状态事务Mock实现"""
    
    def __init__(self):
        self.changes: List[StateChange] = []
        self.committed = False
        self.active = False
    
    def begin(self) -> None:
        self.changes.clear()
        self.committed = False
        self.active = True
    
    def add_change(self, change: StateChange) -> None:
        if self.active:
            self.changes.append(change)
    
    def commit(self) -> bool:
        if self.active:
            self.committed = True
            self.active = False
            return True
        return False
    
    def rollback(self) -> None:
        self.changes.clear()
        self.committed = False
        self.active = False
    
    def get_changes(self) -> List[StateChange]:
        return self.changes.copy()


class MockExecutionEngine(ExecutionEngine):
    """执行引擎Mock实现"""
    
    def __init__(self):
        self.registry = MockFunctionRegistry()
        self.retriever = MockFunctionRetriever(self.registry)
        self.execution_history: List[Dict[str, Any]] = []
    
    def process(self, intent: Intent, game_state: 'GameState') -> ExecutionResult:
        """处理玩家意图并返回执行结果"""
        # 记录执行历史
        execution_record = {
            'intent': intent.to_dict(),
            'timestamp': len(self.execution_history)
        }
        
        try:
            # 检索匹配的Function
            functions = self.retriever.query_functions(intent, game_state, top_k=3)
            
            if not functions:
                # 没有找到匹配的Function
                result = create_failed_result(
                    intent.action,
                    f"没有找到处理'{intent.category}'类型行动的方法"
                )
                execution_record['result'] = result.to_dict()
                self.execution_history.append(execution_record)
                return result
            
            # 使用第一个匹配的Function执行
            selected_function = functions[0]
            
            # 创建执行上下文
            transaction = MockStateTransaction()
            context = ExecutionContext(intent, game_state, transaction)
            
            # 执行Function
            transaction.begin()
            result = selected_function.execute(intent, game_state)
            
            # 如果成功，应用状态变更
            if result.success and result.state_changes:
                for change in result.state_changes:
                    transaction.add_change(change)
                
                # 提交事务
                if transaction.commit():
                    game_state.apply_changes(result.state_changes)
            
            # 更新性能统计
            self.retriever.update_function_performance(
                selected_function.__class__.__name__,
                intent,
                result.success
            )
            
            execution_record['function'] = selected_function.__class__.__name__
            execution_record['result'] = result.to_dict()
            self.execution_history.append(execution_record)
            
            return result
            
        except Exception as e:
            # 异常处理
            result = create_failed_result(
                intent.action,
                f"执行过程中发生错误: {str(e)}"
            )
            execution_record['error'] = str(e)
            execution_record['result'] = result.to_dict()
            self.execution_history.append(execution_record)
            return result
    
    def register_function(self, function_class: Type[GameFunction], 
                         metadata: FunctionMetadata = None) -> None:
        if metadata is None:
            # 从类的_metadata属性获取元数据
            metadata = getattr(function_class, '_metadata', 
                             FunctionMetadata("未知", [], [], 5))
        self.registry.register(function_class, metadata)
    
    def get_supported_categories(self) -> List[str]:
        categories = set()
        for metadata in self.registry.metadata.values():
            categories.add(metadata.category)
        return list(categories)
    
    # 测试辅助方法
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history.copy()
    
    def clear_execution_history(self) -> None:
        """清空执行历史"""
        self.execution_history.clear()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return self.retriever.performance_stats.copy()