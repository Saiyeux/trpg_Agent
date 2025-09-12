"""
可填充的状态管理器实现

基于状态管理接口的具体实现，集成角色属性、消耗品和地图数据。
提供完整的状态变更逻辑，支持扩展填充。
"""

from typing import Dict, List, Any, Optional
from ..interfaces.state_management_interfaces import (
    StateManager, PlayerStateManager, NPCStateManager, EnvironmentStateManager,
    StateOperationRequest, StateChange, StateValidationResult, StateOperationType
)
from ..interfaces.data_structures import StateChange as CoreStateChange
from ..data import (
    CharacterAttributes, PlayerInventory, ConsumableRegistry, GameMap,
    create_character, create_starter_map, AttributeType, ConsumableType
)


class FillablePlayerStateManager(PlayerStateManager):
    """可填充的玩家状态管理器"""
    
    def __init__(self, character_template: str = "战士"):
        self.character = create_character(character_template)
        self.inventory = PlayerInventory(max_slots=30)
        self.current_location = "village_center"
        self.quest_progress: Dict[str, Any] = {}
        self.status_effects: List[Dict[str, Any]] = []
    
    def supports_target(self, target: str) -> bool:
        """检查是否支持指定目标"""
        return target.lower() in ["player", "玩家", "自己"]
    
    def can_perform_operation(self, request: StateOperationRequest) -> StateValidationResult:
        """检查是否可以执行状态操作"""
        
        # 解析属性路径
        parts = request.property_path.split('.')
        base_property = parts[0]
        
        # 检查属性是否存在
        if base_property in ["hp", "current_hp"]:
            if request.operation == StateOperationType.SUBTRACT:
                current_hp = self.character.get_attribute("current_hp")
                if current_hp - request.value <= 0:
                    return StateValidationResult(
                        valid=True,  # 允许执行，但会产生死亡副作用
                        reason="生命值将降至0或以下",
                        side_effects=[
                            StateOperationRequest("player", "alive", StateOperationType.SET, False, reason="生命值耗尽")
                        ]
                    )
            return StateValidationResult(valid=True)
        
        elif base_property in ["mp", "current_mp"]:
            if request.operation == StateOperationType.SUBTRACT:
                current_mp = self.character.get_attribute("current_mp")
                if current_mp < request.value:
                    return StateValidationResult(valid=False, reason="魔法值不足")
            return StateValidationResult(valid=True)
        
        elif base_property == "location":
            # 位置变更需要地图验证 (这里简化处理)
            return StateValidationResult(valid=True)
        
        elif base_property == "inventory":
            if request.operation in [StateOperationType.APPEND, StateOperationType.ADD]:
                # 检查背包空间
                if len([s for s in self.inventory.slots if s is not None]) >= self.inventory.max_slots:
                    return StateValidationResult(valid=False, reason="背包已满")
            return StateValidationResult(valid=True)
        
        else:
            # 其他属性检查
            if base_property in self.character.attribute_definitions:
                return StateValidationResult(valid=True)
            else:
                return StateValidationResult(valid=False, reason=f"未知属性: {base_property}")
    
    def apply_operation(self, request: StateOperationRequest) -> StateChange:
        """应用状态操作"""
        parts = request.property_path.split('.')
        base_property = parts[0]
        
        old_value = None
        new_value = None
        
        try:
            if base_property in ["hp", "current_hp"]:
                old_value = self.character.get_attribute("current_hp")
                
                if request.operation == StateOperationType.SET:
                    self.character.set_attribute("current_hp", request.value)
                elif request.operation == StateOperationType.ADD:
                    self.character.modify_attribute("current_hp", request.value)
                elif request.operation == StateOperationType.SUBTRACT:
                    self.character.modify_attribute("current_hp", -request.value)
                
                new_value = self.character.get_attribute("current_hp")
            
            elif base_property in ["mp", "current_mp"]:
                old_value = self.character.get_attribute("current_mp")
                
                if request.operation == StateOperationType.SET:
                    self.character.set_attribute("current_mp", request.value)
                elif request.operation == StateOperationType.ADD:
                    self.character.modify_attribute("current_mp", request.value)
                elif request.operation == StateOperationType.SUBTRACT:
                    self.character.modify_attribute("current_mp", -request.value)
                
                new_value = self.character.get_attribute("current_mp")
            
            elif base_property == "location":
                old_value = self.current_location
                self.current_location = str(request.value)
                new_value = self.current_location
            
            elif base_property == "inventory":
                if request.operation == StateOperationType.APPEND:
                    if isinstance(request.value, dict):
                        item_id = request.value.get("item", "")
                        quantity = request.value.get("quantity", 1)
                        old_value = self.inventory.get_item_count(item_id)
                        self.inventory.add_item(item_id, quantity)
                        new_value = self.inventory.get_item_count(item_id)
                
                elif request.operation == StateOperationType.REMOVE:
                    if isinstance(request.value, dict):
                        item_id = request.value.get("item", "")
                        quantity = request.value.get("quantity", 1)
                        old_value = self.inventory.get_item_count(item_id)
                        self.inventory.remove_item(item_id, quantity)
                        new_value = self.inventory.get_item_count(item_id)
            
            else:
                # 通用属性处理
                if base_property in self.character.attribute_definitions:
                    old_value = self.character.get_attribute(base_property)
                    
                    if request.operation == StateOperationType.SET:
                        self.character.set_attribute(base_property, request.value)
                    elif request.operation == StateOperationType.ADD:
                        self.character.modify_attribute(base_property, request.value)
                    elif request.operation == StateOperationType.SUBTRACT:
                        self.character.modify_attribute(base_property, -request.value)
                    
                    new_value = self.character.get_attribute(base_property)
            
            return CoreStateChange(
                target=request.target,
                property_name=request.property_path,
                old_value=old_value,
                new_value=new_value,
                change_reason=request.reason
            )
        
        except Exception as e:
            return CoreStateChange(
                target=request.target,
                property_name=request.property_path,
                old_value=old_value,
                new_value=old_value,  # 操作失败，值不变
                change_reason=f"操作失败: {str(e)}"
            )
    
    def get_current_value(self, target: str, property_path: str) -> Any:
        """获取当前状态值"""
        if not self.supports_target(target):
            return None
        
        parts = property_path.split('.')
        base_property = parts[0]
        
        if base_property == "location":
            return self.current_location
        elif base_property == "inventory":
            return self.inventory.to_dict()
        else:
            return self.character.get_attribute(base_property)
    
    # PlayerStateManager 接口实现
    
    def get_player_attribute(self, attribute: str) -> Any:
        """获取玩家属性"""
        return self.character.get_attribute(attribute)
    
    def modify_resource(self, resource: str, amount: int, reason: str) -> StateChange:
        """修改玩家资源"""
        request = StateOperationRequest(
            target="player",
            property_path=resource,
            operation=StateOperationType.ADD if amount >= 0 else StateOperationType.SUBTRACT,
            value=abs(amount),
            reason=reason
        )
        return self.apply_operation(request)
    
    def update_location(self, new_location: str, reason: str) -> StateChange:
        """更新玩家位置"""
        request = StateOperationRequest(
            target="player",
            property_path="location",
            operation=StateOperationType.SET,
            value=new_location,
            reason=reason
        )
        return self.apply_operation(request)
    
    def manage_inventory(self, action: str, item: str, quantity: int = 1) -> StateChange:
        """管理玩家背包"""
        operation = StateOperationType.APPEND if action == "add" else StateOperationType.REMOVE
        request = StateOperationRequest(
            target="player",
            property_path="inventory.items",
            operation=operation,
            value={"item": item, "quantity": quantity},
            reason=f"{action} {quantity} {item}"
        )
        return self.apply_operation(request)


class FillableNPCStateManager(NPCStateManager):
    """可填充的NPC状态管理器"""
    
    def __init__(self):
        self.npcs: Dict[str, Dict[str, Any]] = {}
        self._init_default_npcs()
    
    def _init_default_npcs(self):
        """初始化默认NPC - 可填充扩展"""
        
        # 酒馆老板
        self.npcs["bartender_joe"] = {
            "name": "酒保乔",
            "location": "village_tavern",
            "hp": 80,
            "max_hp": 80,
            "alive": True,
            "relationship": 0,  # -100到100
            "dialogue_state": "greeting",
            "shop_inventory": ["bread", "roasted_meat", "health_potion_small"],
            "personality": "friendly"
        }
        
        # 铁匠
        self.npcs["blacksmith_tom"] = {
            "name": "铁匠汤姆",
            "location": "village_weapon_shop", 
            "hp": 120,
            "max_hp": 120,
            "alive": True,
            "relationship": 0,
            "dialogue_state": "working",
            "shop_inventory": ["lockpick", "strength_elixir"],
            "personality": "gruff"
        }
        
        # 森林哥布林 (敌对NPC)
        self.npcs["forest_goblin"] = {
            "name": "森林哥布林",
            "location": "dark_forest",
            "hp": 30,
            "max_hp": 30,
            "alive": True,
            "relationship": -50,
            "hostile": True,
            "loot": ["bread", "magic_dust"],
            "personality": "aggressive"
        }
    
    def supports_target(self, target: str) -> bool:
        """检查是否支持指定目标"""
        return target in self.npcs or target.startswith("npc_")
    
    def can_perform_operation(self, request: StateOperationRequest) -> StateValidationResult:
        """检查是否可以执行状态操作"""
        if not self.supports_target(request.target):
            return StateValidationResult(valid=False, reason="NPC不存在")
        
        npc_data = self.npcs.get(request.target)
        if not npc_data:
            return StateValidationResult(valid=False, reason="NPC数据不存在")
        
        # 检查NPC是否存活
        if not npc_data.get("alive", True) and request.property_path != "alive":
            return StateValidationResult(valid=False, reason="NPC已死亡")
        
        return StateValidationResult(valid=True)
    
    def apply_operation(self, request: StateOperationRequest) -> StateChange:
        """应用状态操作"""
        npc_data = self.npcs.get(request.target)
        if not npc_data:
            return CoreStateChange(request.target, request.property_path, None, None, "NPC不存在")
        
        property_name = request.property_path
        old_value = npc_data.get(property_name)
        
        try:
            if request.operation == StateOperationType.SET:
                npc_data[property_name] = request.value
            elif request.operation == StateOperationType.ADD:
                npc_data[property_name] = npc_data.get(property_name, 0) + request.value
            elif request.operation == StateOperationType.SUBTRACT:
                npc_data[property_name] = npc_data.get(property_name, 0) - request.value
                
                # 特殊处理：生命值降至0时死亡
                if property_name == "hp" and npc_data[property_name] <= 0:
                    npc_data["alive"] = False
                    npc_data["hp"] = 0
            
            new_value = npc_data[property_name]
            
            return CoreStateChange(
                target=request.target,
                property_name=property_name,
                old_value=old_value,
                new_value=new_value,
                change_reason=request.reason
            )
        
        except Exception as e:
            return CoreStateChange(request.target, property_name, old_value, old_value, f"操作失败: {str(e)}")
    
    def get_current_value(self, target: str, property_path: str) -> Any:
        """获取当前状态值"""
        npc_data = self.npcs.get(target)
        if not npc_data:
            return None
        return npc_data.get(property_path)
    
    # NPCStateManager 接口实现
    
    def get_npc_by_name(self, name: str) -> Optional[Any]:
        """通过名称获取NPC"""
        for npc_id, npc_data in self.npcs.items():
            if npc_data.get("name") == name:
                return {"id": npc_id, **npc_data}
        return None
    
    def modify_npc_attribute(self, npc_name: str, attribute: str, value: Any, reason: str) -> StateChange:
        """修改NPC属性"""
        request = StateOperationRequest(
            target=npc_name,
            property_path=attribute,
            operation=StateOperationType.SET,
            value=value,
            reason=reason
        )
        return self.apply_operation(request)
    
    def update_relationship(self, npc_name: str, change: int, reason: str) -> StateChange:
        """更新与NPC的关系"""
        request = StateOperationRequest(
            target=npc_name,
            property_path="relationship",
            operation=StateOperationType.ADD,
            value=change,
            reason=reason
        )
        return self.apply_operation(request)


class FillableEnvironmentStateManager(EnvironmentStateManager):
    """可填充的环境状态管理器"""
    
    def __init__(self):
        self.game_map = create_starter_map()
        self.global_state: Dict[str, Any] = {
            "time_of_day": "morning",
            "weather": "sunny",
            "season": "spring"
        }
        self.object_states: Dict[str, Dict[str, Any]] = {}
        self._init_object_states()
    
    def _init_object_states(self):
        """初始化环境对象状态"""
        # 为地图中的交互对象初始化状态
        for location in self.game_map.locations.values():
            for obj in location.objects:
                self.object_states[obj.id] = {
                    "location": location.id,
                    "state": "normal",
                    **obj.properties
                }
                
                # 特定对象的初始化
                if obj.object_type == "chest":
                    self.object_states[obj.id].update({
                        "opened": False,
                        "contents": ["health_potion_small", "magic_dust", "bread"]
                    })
                elif obj.object_type == "door":
                    self.object_states[obj.id].update({
                        "locked": obj.properties.get("locked", False),
                        "open": False
                    })
    
    def supports_target(self, target: str) -> bool:
        """检查是否支持指定目标"""
        return (target in self.object_states or 
                target == "environment" or 
                target in self.game_map.locations)
    
    def can_perform_operation(self, request: StateOperationRequest) -> StateValidationResult:
        """检查是否可以执行状态操作"""
        if request.target == "environment":
            return StateValidationResult(valid=True)
        
        if request.target in self.object_states:
            obj_state = self.object_states[request.target]
            
            # 检查对象状态
            if obj_state.get("destroyed", False):
                return StateValidationResult(valid=False, reason="对象已被破坏")
            
            return StateValidationResult(valid=True)
        
        return StateValidationResult(valid=False, reason="环境目标不存在")
    
    def apply_operation(self, request: StateOperationRequest) -> StateChange:
        """应用状态操作"""
        if request.target == "environment":
            old_value = self.global_state.get(request.property_path)
            
            if request.operation == StateOperationType.SET:
                self.global_state[request.property_path] = request.value
            
            new_value = self.global_state.get(request.property_path)
            
            return CoreStateChange(
                target=request.target,
                property_name=request.property_path,
                old_value=old_value,
                new_value=new_value,
                change_reason=request.reason
            )
        
        elif request.target in self.object_states:
            obj_state = self.object_states[request.target]
            old_value = obj_state.get(request.property_path)
            
            try:
                if request.operation == StateOperationType.SET:
                    obj_state[request.property_path] = request.value
                elif request.operation == StateOperationType.ADD:
                    obj_state[request.property_path] = obj_state.get(request.property_path, 0) + request.value
                
                new_value = obj_state[request.property_path]
                
                return CoreStateChange(
                    target=request.target,
                    property_name=request.property_path,
                    old_value=old_value,
                    new_value=new_value,
                    change_reason=request.reason
                )
            
            except Exception as e:
                return CoreStateChange(request.target, request.property_path, old_value, old_value, f"操作失败: {str(e)}")
        
        return CoreStateChange(request.target, request.property_path, None, None, "目标不存在")
    
    def get_current_value(self, target: str, property_path: str) -> Any:
        """获取当前状态值"""
        if target == "environment":
            return self.global_state.get(property_path)
        elif target in self.object_states:
            return self.object_states[target].get(property_path)
        elif target in self.game_map.locations:
            location = self.game_map.get_location(target)
            return getattr(location, property_path, None)
        return None
    
    # EnvironmentStateManager 接口实现
    
    def get_location_info(self, location: str) -> Dict[str, Any]:
        """获取位置信息"""
        loc = self.game_map.get_location(location)
        if loc:
            return {
                "name": loc.name,
                "type": loc.location_type.value,
                "description": loc.long_description,
                "objects": [obj.name for obj in loc.objects],
                "npcs": loc.npcs,
                "connections": [(conn.direction.value, conn.target_location) 
                               for conn in loc.connections]
            }
        return {}
    
    def modify_object_state(self, object_id: str, property_name: str, value: Any, reason: str) -> StateChange:
        """修改环境对象状态"""
        request = StateOperationRequest(
            target=object_id,
            property_path=property_name,
            operation=StateOperationType.SET,
            value=value,
            reason=reason
        )
        return self.apply_operation(request)
    
    def check_accessibility(self, from_location: str, to_location: str) -> bool:
        """检查位置可达性"""
        path = self.game_map.find_path(from_location, to_location)
        return len(path) > 0