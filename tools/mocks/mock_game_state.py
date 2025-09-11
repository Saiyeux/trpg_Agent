"""
游戏状态Mock实现

提供GameState、PlayerState、WorldState的Mock实现，
支持可预测的测试和独立开发。
"""

from typing import Dict, List, Any, Optional, Tuple
import copy

from Agent.interfaces.state_interfaces import (
    GameState, PlayerState, WorldState, ConceptRegistry,
    Item, StatusEffect, Location, NPC
)
from Agent.interfaces.data_structures import StateChange, Concept


class MockPlayerState(PlayerState):
    """玩家状态Mock实现"""
    
    def __init__(self):
        self.attributes = {
            "力量": 10, "敏捷": 10, "体质": 10,
            "智力": 10, "感知": 10, "魅力": 10
        }
        self.hp = 20
        self.max_hp = 20
        self.mp = 10
        self.max_mp = 10
        self.location = "起始村庄"
        self.inventory: List[Item] = []
        self.status_effects: List[StatusEffect] = []
    
    def get_attribute(self, name: str) -> int:
        return self.attributes.get(name, 10)
    
    def set_attribute(self, name: str, value: int) -> None:
        self.attributes[name] = value
    
    def get_hp(self) -> Tuple[int, int]:
        return self.hp, self.max_hp
    
    def set_hp(self, hp: int) -> None:
        self.hp = max(0, min(hp, self.max_hp))
    
    def get_mp(self) -> Tuple[int, int]:
        return self.mp, self.max_mp
    
    def set_mp(self, mp: int) -> None:
        self.mp = max(0, min(mp, self.max_mp))
    
    def add_item(self, item: Item) -> bool:
        # 检查是否已有相同物品
        for inv_item in self.inventory:
            if inv_item.name == item.name:
                inv_item.quantity += item.quantity
                return True
        # 添加新物品
        self.inventory.append(item)
        return True
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        for i, item in enumerate(self.inventory):
            if item.name == item_name:
                if item.quantity >= quantity:
                    item.quantity -= quantity
                    if item.quantity == 0:
                        self.inventory.pop(i)
                    return True
                else:
                    return False
        return False
    
    def has_item(self, item_name: str, quantity: int = 1) -> bool:
        for item in self.inventory:
            if item.name == item_name and item.quantity >= quantity:
                return True
        return False
    
    def get_inventory(self) -> List[Item]:
        return copy.deepcopy(self.inventory)
    
    def add_status_effect(self, effect: StatusEffect) -> None:
        # 检查是否已有相同效果
        for i, existing_effect in enumerate(self.status_effects):
            if existing_effect.name == effect.name:
                # 更新现有效果
                if effect.stacks > 0:
                    existing_effect.stacks = min(existing_effect.stacks + effect.stacks, 10)
                existing_effect.duration = max(existing_effect.duration, effect.duration)
                return
        # 添加新效果
        self.status_effects.append(effect)
    
    def remove_status_effect(self, effect_name: str) -> bool:
        for i, effect in enumerate(self.status_effects):
            if effect.name == effect_name:
                self.status_effects.pop(i)
                return True
        return False
    
    def has_status_effect(self, effect_name: str) -> bool:
        return any(effect.name == effect_name for effect in self.status_effects)
    
    def get_status_effects(self) -> List[StatusEffect]:
        return copy.deepcopy(self.status_effects)
    
    def get_location(self) -> str:
        return self.location
    
    def set_location(self, location: str) -> None:
        self.location = location
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'attributes': self.attributes,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'mp': self.mp,
            'max_mp': self.max_mp,
            'location': self.location,
            'inventory': [
                {
                    'name': item.name,
                    'type': item.type,
                    'quantity': item.quantity,
                    'description': item.description
                } for item in self.inventory
            ],
            'status_effects': [
                {
                    'name': effect.name,
                    'type': effect.type,
                    'duration': effect.duration,
                    'stacks': effect.stacks
                } for effect in self.status_effects
            ]
        }


class MockWorldState(WorldState):
    """世界状态Mock实现"""
    
    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.npcs: Dict[str, NPC] = {}
        self.global_flags: Dict[str, bool] = {}
        self._initialize_default_world()
    
    def _initialize_default_world(self):
        """初始化默认的世界状态"""
        # 默认地点
        village = Location(
            name="起始村庄",
            description="一个宁静的小村庄，这里是你冒险的起点。",
            connections=["森林", "商店"],
            items=[
                Item(name="木棍", type="武器", description="一根普通的木棍", quantity=1),
                Item(name="面包", type="食物", description="新鲜的面包", quantity=2, consumable=True)
            ]
        )
        self.add_location(village)
        
        # 默认NPC
        goblin = NPC(
            name="哥布林",
            type="敌人",
            hp=10,
            max_hp=10,
            ac=12,
            inventory=[Item(name="破旧匕首", type="武器", quantity=1)]
        )
        self.add_npc(goblin)
    
    def get_location(self, name: str) -> Optional[Location]:
        return self.locations.get(name)
    
    def add_location(self, location: Location) -> None:
        self.locations[location.name] = location
    
    def get_all_locations(self) -> Dict[str, Location]:
        return copy.deepcopy(self.locations)
    
    def get_npc(self, name: str) -> Optional[NPC]:
        return self.npcs.get(name)
    
    def add_npc(self, npc: NPC) -> None:
        self.npcs[npc.name] = npc
    
    def remove_npc(self, name: str) -> bool:
        if name in self.npcs:
            del self.npcs[name]
            return True
        return False
    
    def get_all_npcs(self) -> Dict[str, NPC]:
        return copy.deepcopy(self.npcs)
    
    def set_global_flag(self, key: str, value: bool) -> None:
        self.global_flags[key] = value
    
    def get_global_flag(self, key: str) -> bool:
        return self.global_flags.get(key, False)
    
    def get_items_at_location(self, location: str) -> List[Item]:
        loc = self.locations.get(location)
        return copy.deepcopy(loc.items) if loc else []
    
    def add_item_at_location(self, location: str, item: Item) -> None:
        if location in self.locations:
            self.locations[location].items.append(item)
    
    def remove_item_at_location(self, location: str, item_name: str) -> bool:
        if location in self.locations:
            items = self.locations[location].items
            for i, item in enumerate(items):
                if item.name == item_name:
                    items.pop(i)
                    return True
        return False


class MockConceptRegistry(ConceptRegistry):
    """概念注册表Mock实现"""
    
    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.turn_counter = 0
    
    def create_concept(self, concept_type: str, name: str, 
                      description: str, properties: Dict[str, Any] = None) -> Concept:
        concept = Concept(
            type=concept_type,
            name=name,
            description=description,
            properties=properties or {},
            created_turn=self.turn_counter
        )
        self.concepts[name] = concept
        return concept
    
    def get_concept(self, name: str) -> Optional[Concept]:
        return self.concepts.get(name)
    
    def update_concept(self, name: str, properties: Dict[str, Any]) -> bool:
        if name in self.concepts:
            self.concepts[name].properties.update(properties)
            return True
        return False
    
    def delete_concept(self, name: str) -> bool:
        if name in self.concepts:
            del self.concepts[name]
            return True
        return False
    
    def get_concepts_by_type(self, concept_type: str) -> List[Concept]:
        return [c for c in self.concepts.values() if c.type == concept_type]
    
    def get_all_concepts(self) -> Dict[str, Concept]:
        return copy.deepcopy(self.concepts)
    
    def search_concepts(self, query: str) -> List[Concept]:
        query_lower = query.lower()
        results = []
        for concept in self.concepts.values():
            if (query_lower in concept.name.lower() or 
                query_lower in concept.description.lower()):
                results.append(concept)
        return results


class MockGameState(GameState):
    """游戏状态Mock实现"""
    
    def __init__(self):
        self._player = MockPlayerState()
        self._world = MockWorldState()
        self._concepts = MockConceptRegistry()
        self.turn_count = 0
        self.history: List[Dict[str, Any]] = []
        self.recorded_changes: List[StateChange] = []  # 用于测试验证
    
    @property
    def player(self) -> PlayerState:
        return self._player
    
    @property
    def world(self) -> WorldState:
        return self._world
    
    @property
    def concepts(self) -> ConceptRegistry:
        return self._concepts
    
    def get_turn_count(self) -> int:
        return self.turn_count
    
    def next_turn(self) -> None:
        self.turn_count += 1
        self._concepts.turn_counter = self.turn_count
    
    def apply_changes(self, changes: List[StateChange]) -> bool:
        """应用状态变更列表"""
        for change in changes:
            if not self.apply_change(change):
                return False
        return True
    
    def apply_change(self, change: StateChange) -> bool:
        """应用单个状态变更"""
        self.recorded_changes.append(change)  # 记录变更用于测试
        
        try:
            if change.target == "player":
                return self._apply_player_change(change)
            elif change.target == "world":
                return self._apply_world_change(change)
            elif change.target.startswith("npc_"):
                npc_name = change.target[4:]  # 移除"npc_"前缀
                return self._apply_npc_change(npc_name, change)
            else:
                return False
        except Exception:
            return False
    
    def _apply_player_change(self, change: StateChange) -> bool:
        """应用玩家状态变更"""
        if change.property == "hp":
            if change.action == "set":
                self._player.set_hp(change.value)
            elif change.action == "modify":
                current_hp, _ = self._player.get_hp()
                self._player.set_hp(current_hp + change.value)
            return True
        elif change.property == "location":
            self._player.set_location(change.value)
            return True
        elif change.property == "items":
            if change.action == "add":
                return self._player.add_item(change.value)
            elif change.action == "remove":
                return self._player.remove_item(change.value.name, change.value.quantity)
        return False
    
    def _apply_world_change(self, change: StateChange) -> bool:
        """应用世界状态变更"""
        # 简化实现，主要用于测试
        return True
    
    def _apply_npc_change(self, npc_name: str, change: StateChange) -> bool:
        """应用NPC状态变更"""
        npc = self._world.get_npc(npc_name)
        if not npc:
            return False
        
        if change.property == "hp":
            if change.action == "set":
                npc.hp = max(0, min(change.value, npc.max_hp))
            elif change.action == "modify":
                npc.hp = max(0, min(npc.hp + change.value, npc.max_hp))
            if npc.hp == 0:
                npc.alive = False
            return True
        return False
    
    def get_recent_history(self, n: int = 5) -> List[Dict[str, Any]]:
        return self.history[-n:] if len(self.history) > n else self.history
    
    def add_to_history(self, event_type: str, content: str, 
                      metadata: Dict[str, Any] = None) -> None:
        entry = {
            'event_type': event_type,
            'content': content,
            'turn': self.turn_count,
            'metadata': metadata or {}
        }
        self.history.append(entry)
    
    def get_current_context(self) -> Dict[str, Any]:
        return {
            'turn': self.turn_count,
            'player_location': self._player.get_location(),
            'player_hp': self._player.get_hp(),
            'recent_events': self.get_recent_history(3)
        }
    
    def save_state(self, filepath: str = None) -> bool:
        # Mock实现，返回成功
        return True
    
    def load_state(self, filepath: str) -> bool:
        # Mock实现，返回成功
        return True
    
    def create_snapshot(self) -> Dict[str, Any]:
        return {
            'player': self._player.to_dict(),
            'turn_count': self.turn_count,
            'history': copy.deepcopy(self.history)
        }
    
    def restore_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        # Mock实现，返回成功
        return True
    
    # 测试辅助方法
    def setup_enemy(self, name: str, hp: int, ac: int = 10) -> None:
        """测试用方法：设置敌人"""
        enemy = NPC(name=name, type="敌人", hp=hp, max_hp=hp, ac=ac)
        self._world.add_npc(enemy)
    
    def get_recorded_changes(self) -> List[StateChange]:
        """测试用方法：获取记录的状态变更"""
        return self.recorded_changes.copy()
    
    def clear_recorded_changes(self) -> None:
        """测试用方法：清空记录的状态变更"""
        self.recorded_changes.clear()