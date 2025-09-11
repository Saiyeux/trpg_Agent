"""
动态内容生成器

使用AI生成游戏内容并自动管理概念注册表，实现真正的动态TRPG体验。
不再依赖写死的内容列表，而是让AI创造和管理游戏世界。
"""

import json
import random
from typing import Dict, Any, List, Optional
from ..interfaces.state_interfaces import GameState, ConceptRegistry
from ..interfaces.data_structures import Concept
from ..client.model_client import ModelClient


class DynamicContentGenerator:
    """动态内容生成器"""
    
    def __init__(self, model_client: ModelClient, game_state: GameState):
        self.model_client = model_client
        self.game_state = game_state
        
    def generate_search_result(self, location: str, search_context: str = "") -> Dict[str, Any]:
        """
        使用AI生成搜索结果
        
        Args:
            location: 搜索地点
            search_context: 搜索上下文信息
            
        Returns:
            包含是否成功和发现内容的字典
        """
        
        # 获取当前已知的概念避免重复
        existing_items = [concept.name for concept in self.game_state.concepts.get_concepts_by_type("item")]
        existing_items_text = "、".join(existing_items[:5]) if existing_items else "无"
        
        prompt = f"""你是专业的TRPG城主，负责为玩家的搜索行动生成合理的结果。

## 搜索环境
- 地点：{location}
- 上下文：{search_context}
- 已知物品：{existing_items_text}

## 生成要求
请创造一个合理的搜索结果。你可以：
1. 让玩家发现新的有趣物品
2. 发现线索或信息
3. 遭遇意外情况
4. 什么都没找到

## 重要原则
- 创造性：每次都要生成新颖的内容，避免重复已知物品
- 合理性：物品要符合当前环境和背景
- 游戏性：物品应该对游戏有意义，不要太普通
- 具体性：必须提供物品的详细属性

## 输出格式
请返回纯JSON格式：
{{
    "success": true/false,
    "discovery_type": "item|clue|event|nothing",
    "content": {{
        "name": "物品/线索名称",
        "type": "物品类型或事件类型", 
        "description": "详细描述",
        "properties": {{
            "rarity": "common|uncommon|rare|epic",
            "value": 数值,
            "special_effect": "特殊效果描述（可选）"
        }}
    }},
    "narrative": "给玩家的描述文本"
}}

注意：如果success为false，content可以为空，但narrative必须说明为什么没找到。"""

        try:
            response = self.model_client._make_request(prompt, "搜索结果生成")
            result = json.loads(response.strip())
            
            # 如果生成了新物品，注册到概念表
            if result.get("success") and result.get("discovery_type") == "item":
                self._register_discovered_item(result["content"])
            
            return result
            
        except (json.JSONDecodeError, KeyError) as e:
            # AI响应解析失败的fallback
            return {
                "success": False,
                "discovery_type": "nothing", 
                "content": {},
                "narrative": f"你仔细搜索了{location}，但没有发现任何特别的东西。"
            }
    
    def _register_discovered_item(self, item_data: Dict[str, Any]) -> None:
        """将AI生成的物品注册到概念表"""
        try:
            concept = self.game_state.concepts.create_concept(
                concept_type="item",
                name=item_data["name"],
                description=item_data["description"],
                properties={
                    "type": item_data.get("type", "misc"),
                    "rarity": item_data.get("properties", {}).get("rarity", "common"),
                    "value": item_data.get("properties", {}).get("value", 1),
                    "special_effect": item_data.get("properties", {}).get("special_effect", ""),
                    "discovered_at": self.game_state.world.current_location,
                    "turn_discovered": self.game_state.get_turn_count()
                }
            )
            
            # 记录到游戏历史
            self.game_state.add_to_history(
                event_type="item_discovery",
                content=f"发现新物品：{item_data['name']}",
                metadata={
                    "item_name": item_data["name"],
                    "location": self.game_state.world.current_location,
                    "rarity": item_data.get("properties", {}).get("rarity", "common")
                }
            )
            
        except Exception as e:
            print(f"注册物品到概念表失败: {e}")
    
    def generate_npc_dialogue(self, npc_name: str, context: str) -> str:
        """
        生成NPC对话内容
        
        Args:
            npc_name: NPC名称
            context: 对话上下文
            
        Returns:
            NPC的回应
        """
        
        # 获取NPC信息
        npc = self.game_state.world.get_npc(npc_name)
        if not npc:
            return f"{npc_name}似乎不想与你交谈。"
        
        prompt = f"""你是专业的TRPG城主，为NPC生成对话内容。

## NPC信息
- 姓名：{npc.name}
- 类型：{npc.type}
- 当前血量：{npc.hp}/{npc.max_hp}
- 状态：{'存活' if npc.alive else '死亡'}

## 对话上下文
{context}

## 要求
1. 根据NPC类型和状态生成合适的对话
2. 如果是敌对NPC且受伤，应该表现出敌意或求饶
3. 如果是友好NPC，应该提供有用信息或服务
4. 对话要有个性，符合角色设定
5. 控制在50-150字内

请直接返回NPC的对话内容，不要JSON格式："""

        try:
            return self.model_client._make_request(prompt, "NPC对话生成")
        except Exception as e:
            return f"{npc_name}看着你，但似乎不知道该说什么。"
    
    def enhance_action_description(self, action_result: str, context: Dict[str, Any]) -> str:
        """
        增强动作描述的细节和沉浸感
        
        Args:
            action_result: 基础的动作结果
            context: 上下文信息
            
        Returns:
            增强后的描述
        """
        
        prompt = f"""你是专业的TRPG城主，负责增强动作描述的沉浸感。

## 基础动作结果
{action_result}

## 当前环境
- 地点：{context.get('location', '未知')}
- 时间：{context.get('time', '未知')}
- 氛围：{context.get('atmosphere', '普通')}

## 要求
1. 保持原有的具体数值和结果不变
2. 增加环境细节和感官描述
3. 添加动作的视觉和听觉效果
4. 保持简洁，控制在100-200字
5. 使用第二人称"你"

请返回增强后的描述："""

        try:
            return self.model_client._make_request(prompt, "动作描述增强")
        except Exception as e:
            return action_result  # 失败时返回原描述


class ConceptMatcher:
    """概念匹配器 - 从AI文本中识别和提取概念"""
    
    def __init__(self, concept_registry: ConceptRegistry):
        self.concept_registry = concept_registry
    
    def extract_items_from_text(self, text: str) -> List[str]:
        """从文本中提取可能的物品名称"""
        # 简单实现：查找常见物品关键词
        item_keywords = ["剑", "匕首", "药水", "金币", "戒指", "卷轴", "宝石", "盾牌", "弓", "箭"]
        found_items = []
        
        for keyword in item_keywords:
            if keyword in text:
                found_items.append(keyword)
        
        return found_items
    
    def create_concept_from_description(self, description: str, concept_type: str = "item") -> Optional[Concept]:
        """根据描述创建新概念"""
        # 这里可以使用更复杂的NLP技术来解析描述
        # 暂时使用简单实现
        pass