"""
状态管理接口定义

定义游戏状态管理的所有接口，包括玩家状态、世界状态、
动态概念管理等核心组件。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from .data_structures import StateChange, Concept


@dataclass
class Item:
    """物品数据结构"""
    name: str                           # 物品名称
    type: str                          # 物品类型
    description: str = ""               # 描述
    quantity: int = 1                   # 数量
    properties: Dict[str, Any] = field(default_factory=dict)  # 属性
    consumable: bool = False            # 是否为消耗品
    

@dataclass  
class StatusEffect:
    """状态效果数据结构"""
    name: str                           # 效果名称
    type: str                          # 效果类型(buff/debuff/neutral)
    description: str = ""               # 描述
    duration: int = -1                  # 持续回合数(-1表示永久)
    properties: Dict[str, Any] = field(default_factory=dict)  # 效果属性
    stacks: int = 1                     # 叠加层数


@dataclass
class Location:
    """地点数据结构"""
    name: str                           # 地点名称
    description: str = ""               # 描述
    connections: List[str] = field(default_factory=list)  # 连接的地点
    items: List[Item] = field(default_factory=list)       # 地点物品
    properties: Dict[str, Any] = field(default_factory=dict)  # 地点属性


@dataclass
class NPC:
    """NPC数据结构"""
    name: str                           # NPC名称
    type: str                          # NPC类型
    hp: int = 10                        # 生命值
    max_hp: int = 10                    # 最大生命值
    ac: int = 10                        # 护甲等级
    alive: bool = True                  # 是否存活
    properties: Dict[str, Any] = field(default_factory=dict)  # NPC属性
    inventory: List[Item] = field(default_factory=list)       # NPC物品


class PlayerState(ABC):
    """
    玩家状态接口
    
    管理玩家的所有状态信息，包括属性、物品、技能等。
    """
    
    @abstractmethod
    def get_attribute(self, name: str) -> int:
        """获取玩家属性"""
        pass
    
    @abstractmethod
    def set_attribute(self, name: str, value: int) -> None:
        """设置玩家属性"""
        pass
    
    @abstractmethod
    def get_hp(self) -> Tuple[int, int]:
        """获取当前HP和最大HP"""
        pass
    
    @abstractmethod
    def set_hp(self, hp: int) -> None:
        """设置当前HP"""
        pass
    
    @abstractmethod
    def get_mp(self) -> Tuple[int, int]:
        """获取当前MP和最大MP"""
        pass
    
    @abstractmethod
    def set_mp(self, mp: int) -> None:
        """设置当前MP"""
        pass
    
    @abstractmethod
    def add_item(self, item: Item) -> bool:
        """添加物品到背包"""
        pass
    
    @abstractmethod
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """从背包移除物品"""
        pass
    
    @abstractmethod
    def has_item(self, item_name: str, quantity: int = 1) -> bool:
        """检查是否拥有物品"""
        pass
    
    @abstractmethod
    def get_inventory(self) -> List[Item]:
        """获取背包物品列表"""
        pass
    
    @abstractmethod
    def add_status_effect(self, effect: StatusEffect) -> None:
        """添加状态效果"""
        pass
    
    @abstractmethod
    def remove_status_effect(self, effect_name: str) -> bool:
        """移除状态效果"""
        pass
    
    @abstractmethod
    def has_status_effect(self, effect_name: str) -> bool:
        """检查是否有指定状态效果"""
        pass
    
    @abstractmethod
    def get_status_effects(self) -> List[StatusEffect]:
        """获取所有状态效果"""
        pass
    
    @abstractmethod
    def get_location(self) -> str:
        """获取当前位置"""
        pass
    
    @abstractmethod
    def set_location(self, location: str) -> None:
        """设置当前位置"""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        pass


class WorldState(ABC):
    """
    世界状态接口
    
    管理游戏世界的状态，包括地点、NPC、全局标志等。
    """
    
    @abstractmethod
    def get_location(self, name: str) -> Optional[Location]:
        """获取指定地点"""
        pass
    
    @abstractmethod
    def add_location(self, location: Location) -> None:
        """添加新地点"""
        pass
    
    @abstractmethod
    def get_all_locations(self) -> Dict[str, Location]:
        """获取所有地点"""
        pass
    
    @abstractmethod
    def get_npc(self, name: str) -> Optional[NPC]:
        """获取指定NPC"""
        pass
    
    @abstractmethod
    def add_npc(self, npc: NPC) -> None:
        """添加NPC"""
        pass
    
    @abstractmethod
    def remove_npc(self, name: str) -> bool:
        """移除NPC"""
        pass
    
    @abstractmethod
    def get_all_npcs(self) -> Dict[str, NPC]:
        """获取所有NPC"""
        pass
    
    @abstractmethod
    def set_global_flag(self, key: str, value: bool) -> None:
        """设置全局标志"""
        pass
    
    @abstractmethod
    def get_global_flag(self, key: str) -> bool:
        """获取全局标志"""
        pass
    
    @abstractmethod
    def get_items_at_location(self, location: str) -> List[Item]:
        """获取指定地点的物品"""
        pass
    
    @abstractmethod
    def add_item_at_location(self, location: str, item: Item) -> None:
        """在指定地点添加物品"""
        pass
    
    @abstractmethod
    def remove_item_at_location(self, location: str, item_name: str) -> bool:
        """从指定地点移除物品"""
        pass


class ConceptRegistry(ABC):
    """
    概念注册表接口
    
    管理动态创建的概念，如新技能、新状态效果等。
    """
    
    @abstractmethod
    def create_concept(self, concept_type: str, name: str, 
                      description: str, properties: Dict[str, Any] = None) -> Concept:
        """创建新概念"""
        pass
    
    @abstractmethod
    def get_concept(self, name: str) -> Optional[Concept]:
        """获取指定概念"""
        pass
    
    @abstractmethod
    def update_concept(self, name: str, properties: Dict[str, Any]) -> bool:
        """更新概念属性"""
        pass
    
    @abstractmethod
    def delete_concept(self, name: str) -> bool:
        """删除概念"""
        pass
    
    @abstractmethod
    def get_concepts_by_type(self, concept_type: str) -> List[Concept]:
        """根据类型获取概念"""
        pass
    
    @abstractmethod
    def get_all_concepts(self) -> Dict[str, Concept]:
        """获取所有概念"""
        pass
    
    @abstractmethod
    def search_concepts(self, query: str) -> List[Concept]:
        """搜索概念"""
        pass


class GameState(ABC):
    """
    游戏状态接口
    
    游戏状态的顶层接口，协调玩家状态、世界状态和概念管理。
    """
    
    @property
    @abstractmethod
    def player(self) -> PlayerState:
        """玩家状态"""
        pass
    
    @property
    @abstractmethod
    def world(self) -> WorldState:
        """世界状态"""
        pass
    
    @property
    @abstractmethod
    def concepts(self) -> ConceptRegistry:
        """概念注册表"""
        pass
    
    @abstractmethod
    def get_turn_count(self) -> int:
        """获取当前回合数"""
        pass
    
    @abstractmethod
    def next_turn(self) -> None:
        """推进到下一回合"""
        pass
    
    @abstractmethod
    def apply_changes(self, changes: List[StateChange]) -> bool:
        """应用状态变更列表"""
        pass
    
    @abstractmethod
    def apply_change(self, change: StateChange) -> bool:
        """应用单个状态变更"""
        pass
    
    @abstractmethod
    def get_recent_history(self, n: int = 5) -> List[Dict[str, Any]]:
        """获取最近的历史记录"""
        pass
    
    @abstractmethod
    def add_to_history(self, event_type: str, content: str, 
                      metadata: Dict[str, Any] = None) -> None:
        """添加历史记录"""
        pass
    
    @abstractmethod
    def get_current_context(self) -> Dict[str, Any]:
        """获取当前上下文信息"""
        pass
    
    @abstractmethod
    def save_state(self, filepath: str = None) -> bool:
        """保存状态到文件"""
        pass
    
    @abstractmethod
    def load_state(self, filepath: str) -> bool:
        """从文件加载状态"""
        pass
    
    @abstractmethod
    def create_snapshot(self) -> Dict[str, Any]:
        """创建状态快照"""
        pass
    
    @abstractmethod
    def restore_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """恢复状态快照"""
        pass


class StateValidator(ABC):
    """
    状态验证器接口
    
    验证状态变更的合法性和一致性。
    """
    
    @abstractmethod
    def validate_change(self, change: StateChange, game_state: GameState) -> bool:
        """验证单个状态变更"""
        pass
    
    @abstractmethod
    def validate_changes(self, changes: List[StateChange], 
                        game_state: GameState) -> List[bool]:
        """验证状态变更列表"""
        pass
    
    @abstractmethod
    def get_validation_errors(self) -> List[str]:
        """获取验证错误信息"""
        pass


class StateEventListener(ABC):
    """
    状态事件监听器接口
    
    监听状态变更事件，支持响应式编程。
    """
    
    @abstractmethod
    def on_state_changed(self, change: StateChange, game_state: GameState) -> None:
        """状态变更时的回调"""
        pass
    
    @abstractmethod
    def on_player_hp_changed(self, old_hp: int, new_hp: int) -> None:
        """玩家HP变更时的回调"""
        pass
    
    @abstractmethod
    def on_location_changed(self, old_location: str, new_location: str) -> None:
        """位置变更时的回调"""
        pass
    
    @abstractmethod
    def on_concept_created(self, concept: Concept) -> None:
        """概念创建时的回调"""
        pass