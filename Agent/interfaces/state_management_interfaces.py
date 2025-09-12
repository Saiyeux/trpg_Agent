"""
状态管理接口定义

定义了统一的状态管理接口，支持扩展和解耦的状态变更操作。
将状态变更逻辑从Function中分离，提供可配置的状态管理框架。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
from dataclasses import dataclass
from .data_structures import StateChange


class StateOperationType(Enum):
    """状态操作类型"""
    SET = "set"           # 设置值
    ADD = "add"           # 增加值
    SUBTRACT = "subtract" # 减少值
    MULTIPLY = "multiply" # 乘法
    APPEND = "append"     # 添加到列表
    REMOVE = "remove"     # 从列表移除


@dataclass
class StateOperationRequest:
    """状态操作请求"""
    target: str                    # 目标对象 (player, npc_name, environment)
    property_path: str             # 属性路径 (如 "hp", "inventory.items", "location.name")
    operation: StateOperationType  # 操作类型
    value: Any                     # 操作值
    condition: Optional[Dict[str, Any]] = None  # 操作条件
    reason: str = ""              # 操作原因描述


@dataclass
class StateValidationResult:
    """状态验证结果"""
    valid: bool
    reason: str = ""
    required_resources: Dict[str, Any] = None
    side_effects: List[StateOperationRequest] = None


class StateManager(ABC):
    """状态管理器基类"""
    
    @abstractmethod
    def can_perform_operation(self, request: StateOperationRequest) -> StateValidationResult:
        """检查是否可以执行状态操作"""
        pass
    
    @abstractmethod
    def apply_operation(self, request: StateOperationRequest) -> StateChange:
        """应用状态操作"""
        pass
    
    @abstractmethod
    def get_current_value(self, target: str, property_path: str) -> Any:
        """获取当前状态值"""
        pass
    
    @abstractmethod
    def supports_target(self, target: str) -> bool:
        """检查是否支持指定目标"""
        pass


class PlayerStateManager(StateManager):
    """玩家状态管理器接口"""
    
    @abstractmethod
    def get_player_attribute(self, attribute: str) -> Any:
        """获取玩家属性"""
        pass
    
    @abstractmethod
    def modify_resource(self, resource: str, amount: int, reason: str) -> StateChange:
        """修改玩家资源 (HP, MP, 金币等)"""
        pass
    
    @abstractmethod
    def update_location(self, new_location: str, reason: str) -> StateChange:
        """更新玩家位置"""
        pass
    
    @abstractmethod
    def manage_inventory(self, action: str, item: str, quantity: int = 1) -> StateChange:
        """管理玩家背包"""
        pass


class NPCStateManager(StateManager):
    """NPC状态管理器接口"""
    
    @abstractmethod
    def get_npc_by_name(self, name: str) -> Optional[Any]:
        """通过名称获取NPC"""
        pass
    
    @abstractmethod
    def modify_npc_attribute(self, npc_name: str, attribute: str, value: Any, reason: str) -> StateChange:
        """修改NPC属性"""
        pass
    
    @abstractmethod
    def update_relationship(self, npc_name: str, change: int, reason: str) -> StateChange:
        """更新与NPC的关系"""
        pass


class EnvironmentStateManager(StateManager):
    """环境状态管理器接口"""
    
    @abstractmethod
    def get_location_info(self, location: str) -> Dict[str, Any]:
        """获取位置信息"""
        pass
    
    @abstractmethod
    def modify_object_state(self, object_id: str, property_name: str, value: Any, reason: str) -> StateChange:
        """修改环境对象状态"""
        pass
    
    @abstractmethod
    def check_accessibility(self, from_location: str, to_location: str) -> bool:
        """检查位置可达性"""
        pass


class StateManagerRegistry:
    """状态管理器注册表"""
    
    def __init__(self):
        self._managers: Dict[str, StateManager] = {}
    
    def register(self, category: str, manager: StateManager):
        """注册状态管理器"""
        self._managers[category] = manager
    
    def get_manager(self, category: str) -> Optional[StateManager]:
        """获取状态管理器"""
        return self._managers.get(category)
    
    def get_manager_for_target(self, target: str) -> Optional[StateManager]:
        """根据目标获取合适的状态管理器"""
        for manager in self._managers.values():
            if manager.supports_target(target):
                return manager
        return None


class StateTransactionManager:
    """状态事务管理器"""
    
    def __init__(self, registry: StateManagerRegistry):
        self.registry = registry
        self.pending_operations: List[StateOperationRequest] = []
        self.applied_changes: List[StateChange] = []
    
    def add_operation(self, request: StateOperationRequest) -> bool:
        """添加状态操作请求"""
        manager = self.registry.get_manager_for_target(request.target)
        if not manager:
            return False
        
        validation = manager.can_perform_operation(request)
        if not validation.valid:
            return False
        
        self.pending_operations.append(request)
        
        # 如果有副作用操作，也添加进来
        if validation.side_effects:
            self.pending_operations.extend(validation.side_effects)
        
        return True
    
    def execute_transaction(self) -> Tuple[bool, List[StateChange]]:
        """执行事务中的所有操作"""
        try:
            changes = []
            for request in self.pending_operations:
                manager = self.registry.get_manager_for_target(request.target)
                if manager:
                    change = manager.apply_operation(request)
                    changes.append(change)
                    self.applied_changes.append(change)
            
            return True, changes
        except Exception as e:
            # 回滚操作
            self.rollback()
            return False, []
    
    def rollback(self):
        """回滚已应用的变更"""
        # 实现回滚逻辑
        for change in reversed(self.applied_changes):
            # 这里需要具体的回滚实现
            pass
    
    def clear(self):
        """清空事务"""
        self.pending_operations.clear()
        self.applied_changes.clear()


# 便利函数和常量
class StateConstants:
    """状态相关常量"""
    
    # 玩家属性
    PLAYER_HP = "player.hp"
    PLAYER_MP = "player.mp"
    PLAYER_LOCATION = "player.location"
    PLAYER_INVENTORY = "player.inventory"
    PLAYER_GOLD = "player.gold"
    
    # NPC属性
    NPC_HP = "{npc_name}.hp"
    NPC_ALIVE = "{npc_name}.alive"
    NPC_RELATIONSHIP = "{npc_name}.relationship"
    
    # 环境属性
    DOOR_STATE = "door.{door_id}.state"
    CONTAINER_CONTENTS = "container.{container_id}.contents"


def create_resource_operation(target: str, resource: str, amount: int, reason: str) -> StateOperationRequest:
    """创建资源变更操作的便利函数"""
    operation_type = StateOperationType.ADD if amount >= 0 else StateOperationType.SUBTRACT
    return StateOperationRequest(
        target=target,
        property_path=resource,
        operation=operation_type,
        value=abs(amount),
        reason=reason
    )


def create_inventory_operation(action: str, item: str, quantity: int = 1) -> StateOperationRequest:
    """创建背包操作的便利函数"""
    operation_type = StateOperationType.APPEND if action == "add" else StateOperationType.REMOVE
    return StateOperationRequest(
        target="player",
        property_path="inventory.items",
        operation=operation_type,
        value={"item": item, "quantity": quantity},
        reason=f"{action} {quantity} {item}"
    )