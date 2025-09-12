"""
动态内容生成函数实现

基于AI响应解析结果，动态生成并添加新的游戏内容。
包括位置、NPC、物品和交互对象的生成。
"""

import time
import random
from typing import Dict, Any, List, Optional
from ..interfaces.execution_interfaces import GameFunction, StateTransaction
from ..interfaces.data_structures import Intent, ExecutionResult, StateChange, DiceRoll
from ..interfaces.state_interfaces import GameState
from ..ai.response_parser import ContentGenerationRequest, ContentType
from ..data import (
    MapLocation, LocationType, InteractableObject, Direction, LocationConnection,
    ConsumableItem, ConsumableType, EffectType, ItemEffect
)


class ContentGenerationFunction(GameFunction):
    """动态内容生成基类"""
    
    def __init__(self):
        self.name = "content_generation"
        self.description = "根据AI响应动态生成游戏内容"
        self.metadata = {
            'category': '其他',
            'requires_target': False,
            'can_fail': False,
            'system_function': True  # 标记为系统函数
        }
    
    def can_execute(self, intent: Intent, game_state: GameState) -> bool:
        """检查是否可以执行内容生成"""
        # 系统函数，只能通过特定方式调用
        return hasattr(intent, 'system_trigger') and intent.system_trigger
    
    def execute(self, intent: Intent, game_state: GameState, 
                transaction: StateTransaction) -> ExecutionResult:
        """执行内容生成 - 子类实现"""
        raise NotImplementedError("子类必须实现execute方法")
    
    def generate_unique_id(self, content_type: str, name: str) -> str:
        """生成唯一ID"""
        # 移除特殊字符并转换为小写
        clean_name = ''.join(c for c in name if c.isalnum() or c in ['_', '-']).lower()
        timestamp = int(time.time() * 1000) % 100000  # 取后5位作为时间戳
        return f"{content_type}_{clean_name}_{timestamp}"


class LocationGenerationFunction(ContentGenerationFunction):
    """位置生成函数"""
    
    def __init__(self):
        super().__init__()
        self.name = "location_generation"
        self.description = "动态生成新的游戏位置"
    
    def execute(self, intent: Intent, game_state: GameState, 
                transaction: StateTransaction) -> ExecutionResult:
        """执行位置生成"""
        
        # 从intent元数据中获取生成请求
        generation_request: ContentGenerationRequest = intent.metadata.get('generation_request')
        if not generation_request or generation_request.content_type != ContentType.LOCATION:
            return ExecutionResult(
                success=False,
                action_taken="尝试生成位置",
                failure_reason="无效的位置生成请求",
                state_changes=[]
            )
        
        # 生成位置数据
        location_id = self.generate_unique_id("loc", generation_request.name)
        location_type = self._determine_location_type(generation_request)
        
        # 创建新位置
        new_location = MapLocation(
            id=location_id,
            name=generation_request.name,
            location_type=location_type,
            short_description=f"新发现的{generation_request.name}",
            long_description=self._generate_description(generation_request),
            objects=self._generate_objects(generation_request),
            properties={"auto_generated": True, "generation_time": time.time()}
        )
        
        # 尝试连接到现有地图
        self._connect_to_existing_locations(new_location, game_state, generation_request)
        
        # 将新位置添加到游戏世界
        state_change = StateChange(
            target="environment",
            property_name=f"map.locations.{location_id}",
            old_value=None,
            new_value=new_location.to_dict() if hasattr(new_location, 'to_dict') else {
                "id": new_location.id,
                "name": new_location.name,
                "type": location_type.value,
                "description": new_location.long_description
            },
            change_reason=f"AI生成新位置: {generation_request.name}"
        )
        
        return ExecutionResult(
            success=True,
            action_taken=f"生成新位置: {generation_request.name}",
            state_changes=[state_change],
            dice_results=[],
            additional_info={
                "location_id": location_id,
                "location_type": location_type.value,
                "auto_generated": True
            }
        )
    
    def _determine_location_type(self, request: ContentGenerationRequest) -> LocationType:
        """确定位置类型"""
        name_lower = request.name.lower()
        properties = request.properties
        
        # 从属性中获取类型
        if "location_type" in properties:
            type_str = properties["location_type"]
            try:
                return LocationType(type_str)
            except ValueError:
                pass
        
        # 根据名称推测类型
        if any(keyword in name_lower for keyword in ["城市", "城镇", "镇", "都市"]):
            return LocationType.TOWN
        elif any(keyword in name_lower for keyword in ["村庄", "村", "小镇"]):
            return LocationType.TOWN
        elif any(keyword in name_lower for keyword in ["森林", "树林", "丛林"]):
            return LocationType.FOREST
        elif any(keyword in name_lower for keyword in ["山", "山脉", "山峰", "高峰"]):
            return LocationType.MOUNTAIN
        elif any(keyword in name_lower for keyword in ["洞穴", "洞", "洞窟", "石洞"]):
            return LocationType.CAVE
        elif any(keyword in name_lower for keyword in ["地牢", "监牢", "牢房"]):
            return LocationType.DUNGEON
        elif any(keyword in name_lower for keyword in ["房间", "房", "屋", "室"]):
            return LocationType.ROOM
        elif any(keyword in name_lower for keyword in ["商店", "店铺", "商铺"]):
            return LocationType.SHOP
        elif any(keyword in name_lower for keyword in ["酒馆", "客栈", "旅店"]):
            return LocationType.TAVERN
        else:
            return LocationType.WILDERNESS
    
    def _generate_description(self, request: ContentGenerationRequest) -> str:
        """生成位置描述"""
        base_desc = request.description
        
        # 根据位置类型添加通用描述元素
        location_type = self._determine_location_type(request)
        
        if location_type == LocationType.TOWN:
            return f"{base_desc}。这里有石板铺成的街道，两旁是各式各样的建筑，偶尔有居民来往穿梭。"
        elif location_type == LocationType.FOREST:
            return f"{base_desc}。高大的树木遮天蔽日，林间小径蜿蜒曲折，空气中弥漫着新鲜的绿叶香气。"
        elif location_type == LocationType.MOUNTAIN:
            return f"{base_desc}。山势巍峨，怪石嶙峋，山风呼啸而过，远处云雾缭绕。"
        elif location_type == LocationType.CAVE:
            return f"{base_desc}。洞内幽暗潮湿，石壁上长满苔藓，偶尔有水滴声回荡。"
        else:
            return f"{base_desc}。这里环境独特，值得仔细探索。"
    
    def _generate_objects(self, request: ContentGenerationRequest) -> List[InteractableObject]:
        """生成交互对象"""
        objects = []
        location_type = self._determine_location_type(request)
        
        # 根据位置类型添加合适的对象
        if location_type == LocationType.TOWN:
            objects.append(InteractableObject(
                id=self.generate_unique_id("obj", "fountain"),
                name="喷泉",
                description="城镇中心的装饰喷泉",
                object_type="fountain",
                properties={"decorative": True}
            ))
        elif location_type == LocationType.FOREST:
            objects.append(InteractableObject(
                id=self.generate_unique_id("obj", "tree"),
                name="古老大树",
                description="一棵年代久远的大树",
                object_type="tree",
                properties={"climbable": True, "hiding_spot": True}
            ))
        elif location_type == LocationType.CAVE:
            objects.append(InteractableObject(
                id=self.generate_unique_id("obj", "chest"),
                name="神秘宝箱",
                description="一个被遗忘在角落的宝箱",
                object_type="chest",
                properties={"locked": True, "contains_treasure": True}
            ))
        
        return objects
    
    def _connect_to_existing_locations(self, new_location: MapLocation, 
                                     game_state: GameState, 
                                     request: ContentGenerationRequest):
        """连接到现有位置"""
        # 简化实现：暂时不自动连接，交给后续的地图管理逻辑处理
        pass


class NPCGenerationFunction(ContentGenerationFunction):
    """NPC生成函数"""
    
    def __init__(self):
        super().__init__()
        self.name = "npc_generation"
        self.description = "动态生成新的NPC角色"
    
    def execute(self, intent: Intent, game_state: GameState, 
                transaction: StateTransaction) -> ExecutionResult:
        """执行NPC生成"""
        
        generation_request: ContentGenerationRequest = intent.metadata.get('generation_request')
        if not generation_request or generation_request.content_type != ContentType.NPC:
            return ExecutionResult(
                success=False,
                action_taken="尝试生成NPC",
                failure_reason="无效的NPC生成请求",
                state_changes=[]
            )
        
        # 生成NPC数据
        npc_id = self.generate_unique_id("npc", generation_request.name)
        npc_data = self._generate_npc_data(generation_request, npc_id)
        
        # 添加到游戏世界
        state_change = StateChange(
            target="npc_registry",
            property_name=npc_id,
            old_value=None,
            new_value=npc_data,
            change_reason=f"AI生成新NPC: {generation_request.name}"
        )
        
        return ExecutionResult(
            success=True,
            action_taken=f"生成新NPC: {generation_request.name}",
            state_changes=[state_change],
            dice_results=[],
            additional_info={
                "npc_id": npc_id,
                "npc_name": generation_request.name,
                "auto_generated": True
            }
        )
    
    def _generate_npc_data(self, request: ContentGenerationRequest, npc_id: str) -> Dict[str, Any]:
        """生成NPC数据"""
        properties = request.properties
        
        return {
            "id": npc_id,
            "name": request.name,
            "description": request.description,
            "hp": random.randint(20, 100),
            "max_hp": random.randint(20, 100),
            "alive": True,
            "relationship": 0,
            "personality": properties.get("personality", "neutral"),
            "location": properties.get("location", "unknown"),
            "dialogue_state": "greeting",
            "auto_generated": True,
            "generation_time": time.time()
        }


class ItemGenerationFunction(ContentGenerationFunction):
    """物品生成函数"""
    
    def __init__(self):
        super().__init__()
        self.name = "item_generation"  
        self.description = "动态生成新的游戏物品"
    
    def execute(self, intent: Intent, game_state: GameState, 
                transaction: StateTransaction) -> ExecutionResult:
        """执行物品生成"""
        
        generation_request: ContentGenerationRequest = intent.metadata.get('generation_request')
        if not generation_request or generation_request.content_type != ContentType.ITEM:
            return ExecutionResult(
                success=False,
                action_taken="尝试生成物品",
                failure_reason="无效的物品生成请求",
                state_changes=[]
            )
        
        # 生成物品数据
        item_id = self.generate_unique_id("item", generation_request.name)
        item_data = self._generate_item_data(generation_request, item_id)
        
        # 添加到物品注册表
        state_change = StateChange(
            target="item_registry",
            property_name=item_id,
            old_value=None,
            new_value=item_data,
            change_reason=f"AI生成新物品: {generation_request.name}"
        )
        
        return ExecutionResult(
            success=True,
            action_taken=f"生成新物品: {generation_request.name}",
            state_changes=[state_change],
            dice_results=[],
            additional_info={
                "item_id": item_id,
                "item_name": generation_request.name,
                "auto_generated": True
            }
        )
    
    def _generate_item_data(self, request: ContentGenerationRequest, item_id: str) -> Dict[str, Any]:
        """生成物品数据"""
        properties = request.properties
        
        # 确定物品类型
        item_type = self._determine_item_type(request)
        
        # 生成基础效果
        effects = self._generate_item_effects(request, item_type)
        
        return {
            "id": item_id,
            "name": request.name,
            "description": request.description,
            "item_type": item_type.value,
            "effects": effects,
            "max_stack": properties.get("max_stack", 10),
            "rarity": properties.get("rarity", "common"),
            "value": random.randint(5, 50),
            "weight": random.uniform(0.1, 2.0),
            "auto_generated": True,
            "generation_time": time.time()
        }
    
    def _determine_item_type(self, request: ContentGenerationRequest) -> ConsumableType:
        """确定物品类型"""
        name_lower = request.name.lower()
        properties = request.properties
        
        # 从属性中获取类型
        if "item_type" in properties:
            type_str = properties["item_type"]
            try:
                return ConsumableType(type_str)
            except ValueError:
                pass
        
        # 根据名称推测类型
        if any(keyword in name_lower for keyword in ["药剂", "药水", "药", "饮料"]):
            return ConsumableType.POTION
        elif any(keyword in name_lower for keyword in ["食物", "面包", "肉", "水果"]):
            return ConsumableType.FOOD
        elif any(keyword in name_lower for keyword in ["卷轴", "书", "典籍"]):
            return ConsumableType.SCROLL
        elif any(keyword in name_lower for keyword in ["工具", "道具"]):
            return ConsumableType.TOOL
        else:
            return ConsumableType.REAGENT
    
    def _generate_item_effects(self, request: ContentGenerationRequest, 
                             item_type: ConsumableType) -> List[Dict[str, Any]]:
        """生成物品效果"""
        effects = []
        
        if item_type == ConsumableType.POTION:
            # 药剂通常恢复属性
            effects.append({
                "effect_type": "instant",
                "target_attribute": "current_hp",
                "value": random.randint(10, 50),
                "description": f"恢复生命值"
            })
        elif item_type == ConsumableType.FOOD:
            # 食物恢复少量生命值
            effects.append({
                "effect_type": "instant",
                "target_attribute": "current_hp", 
                "value": random.randint(5, 20),
                "description": "恢复少量生命值"
            })
        elif item_type == ConsumableType.SCROLL:
            # 卷轴通常是一次性技能
            effects.append({
                "effect_type": "instant",
                "target_attribute": "spell_cast",
                "value": 1,
                "description": "释放魔法效果"
            })
        
        return effects


class DynamicContentOrchestrator:
    """动态内容协调器"""
    
    def __init__(self):
        self.generators = {
            ContentType.LOCATION: LocationGenerationFunction(),
            ContentType.NPC: NPCGenerationFunction(), 
            ContentType.ITEM: ItemGenerationFunction()
        }
    
    def process_generation_requests(self, requests: List[ContentGenerationRequest],
                                  game_state: GameState) -> List[ExecutionResult]:
        """处理内容生成请求列表"""
        results = []
        
        for request in requests:
            if request.content_type in self.generators:
                generator = self.generators[request.content_type]
                
                # 创建系统意图
                system_intent = Intent(
                    category="其他",
                    action=f"generate_{request.content_type.value}",
                    target=request.name,
                    metadata={
                        "generation_request": request,
                        "system_trigger": True
                    }
                )
                
                # 执行生成
                # 注意：这里需要创建一个临时事务
                from .execution_engine import RealStateTransaction
                with RealStateTransaction(game_state) as transaction:
                    result = generator.execute(system_intent, game_state, transaction)
                    if result.success:
                        transaction.commit()
                    results.append(result)
            else:
                # 不支持的内容类型
                results.append(ExecutionResult(
                    success=False,
                    action_taken=f"生成{request.content_type.value}内容",
                    failure_reason=f"不支持的内容类型: {request.content_type.value}",
                    state_changes=[]
                ))
        
        return results


# 便利函数
def create_content_orchestrator() -> DynamicContentOrchestrator:
    """创建动态内容协调器"""
    return DynamicContentOrchestrator()