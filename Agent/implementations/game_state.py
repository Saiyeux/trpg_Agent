"""
真实的GameState实现

替换MockGameState，提供完整的游戏状态管理。
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

from ..interfaces.state_interfaces import (
    GameState, PlayerState, WorldState, ConceptRegistry,
    Item, StatusEffect, Location, NPC
)
from ..interfaces.data_structures import StateChange, Concept


class RealConcept(Concept):
    """真实的概念实现"""
    
    def __init__(self, type: str, name: str, description: str, 
                 properties: Dict[str, Any] = None, created_turn: int = 0):
        self.type = type
        self.name = name
        self.description = description
        self.properties = properties or {}
        self.created_turn = created_turn


class RealItem(Item):
    """真实的物品实现"""
    
    def __init__(self, name: str, type: str, description: str = "", 
                 quantity: int = 1, consumable: bool = False, properties: Dict[str, Any] = None):
        self.name = name
        self.type = type
        self.description = description
        self.quantity = quantity
        self.consumable = consumable
        self.properties = properties or {}
    
    def use(self, target: Any = None) -> bool:
        """使用物品"""
        if not self.consumable:
            return False
        if self.quantity <= 0:
            return False
        self.quantity -= 1
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'quantity': self.quantity,
            'consumable': self.consumable,
            'properties': self.properties
        }


class RealStatusEffect(StatusEffect):
    """真实的状态效果实现"""
    
    def __init__(self, name: str, type: str, duration: int = -1, 
                 stacks: int = 1, properties: Dict[str, Any] = None):
        self.name = name
        self.type = type
        self.duration = duration  # -1 表示永久
        self.stacks = stacks
        self.properties = properties or {}
    
    def tick(self) -> bool:
        """状态效果每回合触发，返回是否仍然有效"""
        if self.duration > 0:
            self.duration -= 1
        return self.duration != 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.type,
            'duration': self.duration,
            'stacks': self.stacks,
            'properties': self.properties
        }


class RealLocation(Location):
    """真实的地点实现"""
    
    def __init__(self, name: str, description: str, connections: List[str] = None,
                 items: List[Item] = None, properties: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.connections = connections or []
        self.items = items or []
        self.properties = properties or {}
    
    def add_item(self, item: Item) -> None:
        """添加物品到地点"""
        # 检查是否已有同类物品
        for existing_item in self.items:
            if existing_item.name == item.name:
                existing_item.quantity += item.quantity
                return
        self.items.append(item)
    
    def remove_item(self, item_name: str, quantity: int = 1) -> Optional[Item]:
        """从地点移除物品"""
        for item in self.items:
            if item.name == item_name:
                if item.quantity <= quantity:
                    self.items.remove(item)
                    return item
                else:
                    item.quantity -= quantity
                    # 创建新的物品实例返回
                    return RealItem(item.name, item.type, item.description, 
                                  quantity, item.consumable, item.properties.copy())
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'connections': self.connections,
            'items': [item.to_dict() for item in self.items],
            'properties': self.properties
        }


class RealNPC(NPC):
    """真实的NPC实现"""
    
    def __init__(self, name: str, type: str, hp: int = 100, max_hp: int = 100,
                 ac: int = 10, inventory: List[Item] = None, properties: Dict[str, Any] = None):
        self.name = name
        self.type = type
        self.hp = hp
        self.max_hp = max_hp
        self.ac = ac  # 护甲值
        self.alive = hp > 0
        self.inventory = inventory or []
        self.properties = properties or {}
    
    def take_damage(self, damage: int) -> bool:
        """受到伤害，返回是否死亡"""
        self.hp = max(0, self.hp - damage)
        self.alive = self.hp > 0
        return not self.alive
    
    def heal(self, amount: int) -> None:
        """治疗"""
        self.hp = min(self.max_hp, self.hp + amount)
        if self.hp > 0:
            self.alive = True
    
    def add_item(self, item: Item) -> None:
        """添加物品到背包"""
        # 检查是否已有同类物品
        for existing_item in self.inventory:
            if existing_item.name == item.name:
                existing_item.quantity += item.quantity
                return
        self.inventory.append(item)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.type,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'ac': self.ac,
            'alive': self.alive,
            'inventory': [item.to_dict() for item in self.inventory],
            'properties': self.properties
        }


class RealPlayerState(PlayerState):
    """真实的玩家状态实现"""
    
    def __init__(self):
        self.attributes = {
            "力量": 10, "敏捷": 10, "体质": 10,
            "智力": 10, "感知": 10, "魅力": 10
        }
        self.hp = 100
        self.max_hp = 100
        self.mp = 50
        self.max_mp = 50
        self.location = "起始村庄"
        self.inventory: List[Item] = []
        self.status_effects: List[StatusEffect] = []
        
        # 游戏统计
        self.level = 1
        self.experience = 0
        self.gold = 100
    
    def get_attribute(self, name: str) -> int:
        return self.attributes.get(name, 10)
    
    def set_attribute(self, name: str, value: int) -> None:
        self.attributes[name] = max(1, min(30, value))  # 限制属性范围 1-30
    
    def get_hp(self) -> Tuple[int, int]:
        return self.hp, self.max_hp
    
    def set_hp(self, hp: int) -> None:
        self.hp = max(0, min(hp, self.max_hp))
    
    def get_mp(self) -> Tuple[int, int]:
        return self.mp, self.max_mp
    
    def set_mp(self, mp: int) -> None:
        self.mp = max(0, min(mp, self.max_mp))
    
    def add_item(self, item: Item) -> bool:
        """添加物品到背包"""
        # 简单实现：无背包限制
        for existing_item in self.inventory:
            if existing_item.name == item.name:
                existing_item.quantity += item.quantity
                return True
        self.inventory.append(item)
        return True
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """从背包移除物品"""
        for item in self.inventory:
            if item.name == item_name:
                if item.quantity <= quantity:
                    self.inventory.remove(item)
                    return True
                else:
                    item.quantity -= quantity
                    return True
        return False
    
    def has_item(self, item_name: str) -> bool:
        return any(item.name == item_name for item in self.inventory)
    
    def get_inventory(self) -> List[Item]:
        """获取背包物品列表"""
        return self.inventory.copy()
    
    def add_status_effect(self, effect: StatusEffect) -> None:
        # 检查是否已有相同效果
        for existing_effect in self.status_effects:
            if existing_effect.name == effect.name:
                existing_effect.stacks += effect.stacks
                existing_effect.duration = max(existing_effect.duration, effect.duration)
                return
        self.status_effects.append(effect)
    
    def remove_status_effect(self, effect_name: str) -> bool:
        for effect in self.status_effects:
            if effect.name == effect_name:
                self.status_effects.remove(effect)
                return True
        return False
    
    def has_status_effect(self, effect_name: str) -> bool:
        return any(effect.name == effect_name for effect in self.status_effects)
    
    def get_status_effects(self) -> List[StatusEffect]:
        return self.status_effects.copy()
    
    def get_location(self) -> str:
        return self.location
    
    def set_location(self, location: str) -> None:
        self.location = location
    
    def tick_status_effects(self) -> None:
        """处理状态效果的持续时间"""
        self.status_effects = [effect for effect in self.status_effects if effect.tick()]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'attributes': self.attributes,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'mp': self.mp,
            'max_mp': self.max_mp,
            'location': self.location,
            'level': self.level,
            'experience': self.experience,
            'gold': self.gold,
            'inventory': [item.to_dict() for item in self.inventory],
            'status_effects': [effect.to_dict() for effect in self.status_effects]
        }


class RealWorldState(WorldState):
    """真实的世界状态实现"""
    
    def __init__(self):
        self.current_location = "起始村庄"
        self.locations: Dict[str, Location] = {}
        self.npcs: Dict[str, NPC] = {}
        self.global_flags: Dict[str, bool] = {}
        self.global_variables: Dict[str, Any] = {}
        
        # 游戏时间
        self.game_time = {"day": 1, "hour": 12, "minute": 0}
        
        self._initialize_default_world()
    
    def _initialize_default_world(self):
        """初始化默认的世界状态"""
        # 创建默认地点
        village = RealLocation(
            name="起始村庄",
            description="一个宁静的小村庄，这里是你冒险的起点。村庄中央有一口井，周围散布着几座小屋。",
            connections=["森林", "商店", "酒馆"],
            items=[
                RealItem("木棍", "武器", "一根普通的木棍，可以用作简单武器", 1),
                RealItem("面包", "食物", "新鲜的面包，可以恢复少量生命值", 2, True)
            ]
        )
        self.add_location(village)
        
        forest = RealLocation(
            name="森林",
            description="阴暗的森林，树木茂密，偶尔能听到野兽的吼声。",
            connections=["起始村庄", "森林深处"],
            items=[
                RealItem("草药", "药品", "常见的治疗草药", 3, True),
                RealItem("树枝", "材料", "干燥的树枝，可以用来制作工具", 5)
            ]
        )
        self.add_location(forest)
        
        # 创建默认NPC
        goblin = RealNPC(
            name="哥布林",
            type="敌人",
            hp=15,
            max_hp=15,
            ac=12,
            inventory=[RealItem("破旧匕首", "武器", "一把生锈的匕首", 1)]
        )
        self.add_npc(goblin)
        
        merchant = RealNPC(
            name="商人老约翰",
            type="友好",
            hp=50,
            max_hp=50,
            ac=10,
            inventory=[
                RealItem("治疗药水", "药品", "恢复30点生命值", 5, True),
                RealItem("铁剑", "武器", "锋利的铁制长剑", 1)
            ]
        )
        self.add_npc(merchant)
    
    def get_location(self, name: str) -> Optional[Location]:
        return self.locations.get(name)
    
    def add_location(self, location: Location) -> None:
        self.locations[location.name] = location
    
    def get_all_locations(self) -> Dict[str, Location]:
        return self.locations.copy()
    
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
        return self.npcs.copy()
    
    def set_flag(self, flag_name: str, value: bool) -> None:
        self.global_flags[flag_name] = value
    
    def get_flag(self, flag_name: str) -> bool:
        return self.global_flags.get(flag_name, False)
    
    def set_variable(self, var_name: str, value: Any) -> None:
        self.global_variables[var_name] = value
    
    def get_variable(self, var_name: str, default: Any = None) -> Any:
        return self.global_variables.get(var_name, default)
    
    def get_global_flag(self, flag_name: str) -> bool:
        """获取全局标志"""
        return self.get_flag(flag_name)
    
    def set_global_flag(self, flag_name: str, value: bool) -> None:
        """设置全局标志"""
        self.set_flag(flag_name, value)
    
    def get_items_at_location(self, location_name: str) -> List[Item]:
        """获取指定地点的物品"""
        location = self.get_location(location_name)
        return location.items.copy() if location else []
    
    def add_item_at_location(self, location_name: str, item: Item) -> bool:
        """在指定地点添加物品"""
        location = self.get_location(location_name)
        if location:
            location.add_item(item)
            return True
        return False
    
    def remove_item_at_location(self, location_name: str, item_name: str, quantity: int = 1) -> Optional[Item]:
        """从指定地点移除物品"""
        location = self.get_location(location_name)
        if location:
            return location.remove_item(item_name, quantity)
        return None
    
    def advance_time(self, minutes: int = 30) -> None:
        """推进游戏时间"""
        self.game_time["minute"] += minutes
        while self.game_time["minute"] >= 60:
            self.game_time["minute"] -= 60
            self.game_time["hour"] += 1
        while self.game_time["hour"] >= 24:
            self.game_time["hour"] -= 24
            self.game_time["day"] += 1
    
    def get_time_string(self) -> str:
        """获取格式化的时间字符串"""
        return f"第{self.game_time['day']}天 {self.game_time['hour']:02d}:{self.game_time['minute']:02d}"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'current_location': self.current_location,
            'locations': {name: loc.to_dict() for name, loc in self.locations.items()},
            'npcs': {name: npc.to_dict() for name, npc in self.npcs.items()},
            'global_flags': self.global_flags,
            'global_variables': self.global_variables,
            'game_time': self.game_time
        }


class RealConceptRegistry(ConceptRegistry):
    """真实的概念注册表实现"""
    
    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.turn_counter = 0
    
    def create_concept(self, concept_type: str, name: str, 
                      description: str, properties: Dict[str, Any] = None) -> Concept:
        """创建新概念"""
        if properties is None:
            properties = {}
        
        concept = RealConcept(
            type=concept_type,
            name=name,
            description=description,
            properties=properties,
            created_turn=self.turn_counter
        )
        
        self.register_concept(concept)
        return concept
    
    def register_concept(self, concept: Concept) -> None:
        concept.created_turn = self.turn_counter
        self.concepts[concept.name] = concept
    
    def get_concept(self, name: str) -> Optional[Concept]:
        return self.concepts.get(name)
    
    def get_concepts_by_type(self, concept_type: str) -> List[Concept]:
        return [concept for concept in self.concepts.values() if concept.type == concept_type]
    
    def delete_concept(self, name: str) -> bool:
        """删除概念"""
        return self.remove_concept(name)
    
    def remove_concept(self, name: str) -> bool:
        if name in self.concepts:
            del self.concepts[name]
            return True
        return False
    
    def update_concept(self, name: str, properties: Dict[str, Any]) -> bool:
        """更新概念属性"""
        if name in self.concepts:
            self.concepts[name].properties.update(properties)
            return True
        return False
    
    def search_concepts(self, query: str) -> List[Concept]:
        """搜索概念"""
        results = []
        query_lower = query.lower()
        for concept in self.concepts.values():
            if (query_lower in concept.name.lower() or 
                query_lower in concept.description.lower() or
                query_lower in concept.type.lower()):
                results.append(concept)
        return results
    
    def get_all_concepts(self) -> Dict[str, Concept]:
        return self.concepts.copy()
    
    def cleanup_old_concepts(self, max_age: int = 100) -> None:
        """清理过期的概念"""
        current_turn = self.turn_counter
        to_remove = []
        for name, concept in self.concepts.items():
            if current_turn - concept.created_turn > max_age:
                to_remove.append(name)
        for name in to_remove:
            del self.concepts[name]


class RealGameState(GameState):
    """真实的游戏状态实现"""
    
    def __init__(self):
        self._player = RealPlayerState()
        self._world = RealWorldState()
        self._concepts = RealConceptRegistry()
        self.turn_count = 0
        self.history: List[Dict[str, Any]] = []
        self.session_id = str(int(time.time()))
        
        # 游戏元数据
        self.created_at = time.time()
        self.last_save = time.time()
        self.game_version = "1.0.0"
    
    @property
    def player(self) -> PlayerState:
        return self._player
    
    @property
    def player_state(self) -> PlayerState:
        """兼容属性"""
        return self._player
    
    @property
    def world(self) -> WorldState:
        return self._world
    
    @property
    def world_state(self) -> WorldState:
        """兼容属性"""
        return self._world
    
    @property
    def concepts(self) -> ConceptRegistry:
        return self._concepts
    
    def get_turn_count(self) -> int:
        return self.turn_count
    
    def next_turn(self) -> None:
        """进入下一回合"""
        self.turn_count += 1
        self._concepts.turn_counter = self.turn_count
        
        # 处理玩家状态效果
        self._player.tick_status_effects()
        
        # 推进游戏时间
        self._world.advance_time(30)  # 每回合30分钟
        
        # 记录回合信息
        self.add_history_entry("system", f"回合 {self.turn_count} 开始 - {self._world.get_time_string()}")
    
    def apply_changes(self, changes: List[StateChange]) -> bool:
        """应用状态变更列表"""
        success_count = 0
        for change in changes:
            if self.apply_change(change):
                success_count += 1
        return success_count == len(changes)
    
    def apply_change(self, change: StateChange) -> bool:
        """应用单个状态变更"""
        return self.apply_state_change(change)
    
    def apply_state_change(self, change: StateChange) -> bool:
        """应用状态变更"""
        try:
            if change.target == "player":
                if change.property == "hp":
                    self._player.set_hp(change.value)
                elif change.property == "mp":
                    self._player.set_mp(change.value)
                elif change.property == "location":
                    self._player.set_location(change.value)
                elif change.property == "gold":
                    self._player.gold = max(0, change.value)
                else:
                    return False
            else:
                # 假设是NPC
                npc = self._world.get_npc(change.target)
                if npc:
                    if change.property == "hp":
                        npc.hp = max(0, change.value)
                        npc.alive = npc.hp > 0
                    else:
                        return False
                else:
                    return False
            
            # 记录变更历史
            self.add_history_entry("state_change", f"{change.target}的{change.property}从{change.old_value}变为{change.value}")
            return True
        except Exception:
            return False
    
    def add_to_history(self, event_type: str, content: str, metadata: Dict[str, Any] = None) -> None:
        """添加历史记录"""
        self.add_history_entry(event_type, content, metadata)
    
    def add_history_entry(self, entry_type: str, content: str, metadata: Dict[str, Any] = None) -> None:
        """添加历史记录"""
        entry = {
            'turn': self.turn_count,
            'timestamp': time.time(),
            'type': entry_type,
            'content': content,
            'metadata': metadata or {}
        }
        self.history.append(entry)
        
        # 限制历史记录长度
        if len(self.history) > 1000:
            self.history = self.history[-500:]  # 保留最近500条
    
    def get_current_context(self) -> Dict[str, Any]:
        """获取当前上下文信息"""
        return {
            'turn_count': self.turn_count,
            'player_location': self._player.get_location(),
            'player_hp': self._player.get_hp(),
            'current_world_location': self._world.current_location,
            'game_time': self._world.get_time_string(),
            'recent_history': self.get_recent_history(3)
        }
    
    def save_state(self, filepath: str = None) -> bool:
        """保存状态到文件"""
        if filepath is None:
            timestamp = int(time.time())
            filepath = f"game_save_{timestamp}.json"
        return self.save_to_file(filepath)
    
    def load_state(self, filepath: str) -> bool:
        """从文件加载状态"""
        return self.load_from_file(filepath)
    
    def get_recent_history(self, n: int = 5) -> List[Dict[str, Any]]:
        """获取最近的历史记录"""
        return self.history[-n:] if self.history else []
    
    def create_snapshot(self) -> Dict[str, Any]:
        """创建游戏状态快照"""
        return {
            'session_id': self.session_id,
            'turn_count': self.turn_count,
            'player': self._player.to_dict(),
            'world': self._world.to_dict(),
            'concepts': self._concepts.get_all_concepts(),
            'history': self.history[-50:],  # 只保存最近50条历史
            'metadata': {
                'created_at': self.created_at,
                'last_save': self.last_save,
                'game_version': self.game_version
            }
        }
    
    def restore_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """从快照恢复游戏状态"""
        try:
            # 这里应该实现完整的状态恢复逻辑
            # 简化实现：只恢复基本信息
            self.session_id = snapshot.get('session_id', self.session_id)
            self.turn_count = snapshot.get('turn_count', 0)
            self.history = snapshot.get('history', [])
            self.last_save = time.time()
            return True
        except Exception:
            return False
    
    def save_to_file(self, filepath: str) -> bool:
        """保存游戏到文件"""
        try:
            snapshot = self.create_snapshot()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)
            self.last_save = time.time()
            return True
        except Exception:
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """从文件加载游戏"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)
            return self.restore_snapshot(snapshot)
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.create_snapshot()