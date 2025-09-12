"""
响应解析模块

解析AI生成的文本内容，提取隐含的状态变更和动态内容生成请求。
支持地图添加、物品获取、NPC生成等动态内容创建。
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..interfaces.state_management_interfaces import StateOperationRequest, StateOperationType


class ContentType(Enum):
    """动态内容类型"""
    LOCATION = "location"     # 新地点
    ITEM = "item"            # 新物品
    NPC = "npc"              # 新NPC
    OBJECT = "object"        # 新交互对象
    SKILL = "skill"          # 新技能
    QUEST = "quest"          # 新任务


@dataclass
class StateChangeIntent:
    """状态变更意图"""
    target: str                    # 目标对象
    property_path: str             # 属性路径
    operation: StateOperationType  # 操作类型
    value: Any                     # 变更值
    confidence: float              # 置信度 0-1
    reason: str                    # 变更原因
    source_text: str               # 来源文本片段


@dataclass
class ContentGenerationRequest:
    """内容生成请求"""
    content_type: ContentType      # 内容类型
    name: str                      # 内容名称
    description: str               # 内容描述
    properties: Dict[str, Any]     # 属性参数
    confidence: float              # 置信度 0-1
    source_text: str               # 来源文本片段


class ResponseParser:
    """响应解析器"""
    
    def __init__(self):
        # 编译正则表达式模式
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        
        # 明确标记的新内容模式
        self.explicit_content_pattern = re.compile(r'【新增内容：(.+?)】', re.IGNORECASE)
        
        # 物品获得模式
        self.item_gain_patterns = [
            re.compile(r'(?:获得了|得到了|找到了|发现了|拿到了)\s*(.+?)(?:[，。！]|$)', re.IGNORECASE),
            re.compile(r'(?:你的背包中|背包里)\s*(?:多了|增加了|出现了)\s*(.+?)(?:[，。！]|$)', re.IGNORECASE),
            re.compile(r'(?:获取|收获)\s*(?:了)?\s*(.+?)(?:[，。！]|$)', re.IGNORECASE),
        ]
        
        # 位置变化模式
        self.location_patterns = [
            re.compile(r'(?:来到了|到达了|进入了|抵达了|走进了)\s*(.+?)(?:[，。！]|$)', re.IGNORECASE),
            re.compile(r'(?:你现在在|你正处于|你身处)\s*(.+?)(?:[，。！]|$)', re.IGNORECASE),
        ]
        
        # 新地点发现模式
        self.new_location_patterns = [
            re.compile(r'(?:发现了|看到了|找到了)\s*一(?:座|个|处|间)\s*(.+?)(?:[，。！]|$)', re.IGNORECASE),
            re.compile(r'(?:眼前出现了|前方出现了)\s*(.+?)(?:[，。！]|$)', re.IGNORECASE),
        ]
        
        # NPC遇见模式
        self.npc_patterns = [
            re.compile(r'(?:遇见了|见到了|碰到了|遇到了)\s*(?:一个|一位)?\s*(.+?)(?:[，。！]|$)', re.IGNORECASE),
            re.compile(r'(?:一个|一位)\s*(.+?)\s*(?:向你|朝你|对你)', re.IGNORECASE),
        ]
        
        # 数值变化模式
        self.stat_change_patterns = [
            re.compile(r'(?:生命值|血量|HP)\s*(?:减少了|降低了|下降了)\s*(\d+)', re.IGNORECASE),
            re.compile(r'(?:魔法值|法力值|MP)\s*(?:消耗了|减少了|降低了)\s*(\d+)', re.IGNORECASE),
            re.compile(r'(?:体力|精力)\s*(?:恢复了|增加了|提升了)\s*(\d+)', re.IGNORECASE),
        ]
    
    def parse_response(self, text: str) -> Tuple[List[StateChangeIntent], List[ContentGenerationRequest]]:
        """
        解析AI响应文本
        
        Returns:
            (状态变更意图列表, 内容生成请求列表)
        """
        state_changes = []
        content_requests = []
        
        # 解析明确标记的内容
        explicit_content = self._parse_explicit_content(text)
        content_requests.extend(explicit_content)
        
        # 解析隐含的状态变更
        implicit_changes = self._parse_implicit_changes(text)
        state_changes.extend(implicit_changes)
        
        # 解析隐含的内容生成
        implicit_content = self._parse_implicit_content(text)
        content_requests.extend(implicit_content)
        
        return state_changes, content_requests
    
    def _parse_explicit_content(self, text: str) -> List[ContentGenerationRequest]:
        """解析明确标记的新内容"""
        requests = []
        
        matches = self.explicit_content_pattern.findall(text)
        for match in matches:
            content_desc = match.strip()
            
            # 分析内容类型
            content_type = self._classify_content_type(content_desc)
            
            requests.append(ContentGenerationRequest(
                content_type=content_type,
                name=content_desc,
                description=f"从文本生成：{content_desc}",
                properties=self._extract_properties_from_desc(content_desc, content_type),
                confidence=0.9,  # 明确标记的内容置信度很高
                source_text=f"【新增内容：{content_desc}】"
            ))
        
        return requests
    
    def _parse_implicit_changes(self, text: str) -> List[StateChangeIntent]:
        """解析隐含的状态变更"""
        changes = []
        
        # 解析物品获得
        item_changes = self._parse_item_gains(text)
        changes.extend(item_changes)
        
        # 解析位置变化
        location_changes = self._parse_location_changes(text)
        changes.extend(location_changes)
        
        # 解析数值变化
        stat_changes = self._parse_stat_changes(text)
        changes.extend(stat_changes)
        
        return changes
    
    def _parse_implicit_content(self, text: str) -> List[ContentGenerationRequest]:
        """解析隐含的内容生成请求"""
        requests = []
        
        # 解析新地点
        location_requests = self._parse_new_locations(text)
        requests.extend(location_requests)
        
        # 解析新NPC
        npc_requests = self._parse_new_npcs(text)
        requests.extend(npc_requests)
        
        return requests
    
    def _parse_item_gains(self, text: str) -> List[StateChangeIntent]:
        """解析物品获得"""
        changes = []
        
        for pattern in self.item_gain_patterns:
            matches = pattern.findall(text)
            for match in matches:
                item_name = match.strip()
                
                # 清理物品名称
                item_name = self._clean_item_name(item_name)
                
                if item_name and len(item_name) > 1:
                    changes.append(StateChangeIntent(
                        target="player",
                        property_path="inventory.items",
                        operation=StateOperationType.APPEND,
                        value={"item": item_name, "quantity": 1},
                        confidence=0.7,
                        reason=f"从文本中检测到物品获得: {item_name}",
                        source_text=match
                    ))
        
        return changes
    
    def _parse_location_changes(self, text: str) -> List[StateChangeIntent]:
        """解析位置变化"""
        changes = []
        
        for pattern in self.location_patterns:
            matches = pattern.findall(text)
            for match in matches:
                location_name = match.strip()
                
                # 清理位置名称
                location_name = self._clean_location_name(location_name)
                
                if location_name and len(location_name) > 1:
                    changes.append(StateChangeIntent(
                        target="player",
                        property_path="location",
                        operation=StateOperationType.SET,
                        value=location_name,
                        confidence=0.8,
                        reason=f"从文本中检测到位置变化: {location_name}",
                        source_text=match
                    ))
        
        return changes
    
    def _parse_stat_changes(self, text: str) -> List[StateChangeIntent]:
        """解析数值变化"""
        changes = []
        
        for pattern in self.stat_change_patterns:
            matches = pattern.findall(text)
            for match in matches:
                try:
                    value = int(match.strip())
                    
                    # 根据模式确定属性和操作
                    if "生命值" in pattern.pattern or "血量" in pattern.pattern or "HP" in pattern.pattern:
                        if "减少" in pattern.pattern or "降低" in pattern.pattern:
                            changes.append(StateChangeIntent(
                                target="player",
                                property_path="current_hp",
                                operation=StateOperationType.SUBTRACT,
                                value=value,
                                confidence=0.8,
                                reason="从文本中检测到生命值变化",
                                source_text=match
                            ))
                    
                    elif "魔法值" in pattern.pattern or "法力值" in pattern.pattern or "MP" in pattern.pattern:
                        if "消耗" in pattern.pattern or "减少" in pattern.pattern:
                            changes.append(StateChangeIntent(
                                target="player",
                                property_path="current_mp", 
                                operation=StateOperationType.SUBTRACT,
                                value=value,
                                confidence=0.8,
                                reason="从文本中检测到魔法值变化",
                                source_text=match
                            ))
                    
                    elif "体力" in pattern.pattern or "精力" in pattern.pattern:
                        if "恢复" in pattern.pattern or "增加" in pattern.pattern:
                            changes.append(StateChangeIntent(
                                target="player",
                                property_path="stamina",
                                operation=StateOperationType.ADD,
                                value=value,
                                confidence=0.8,
                                reason="从文本中检测到体力变化",
                                source_text=match
                            ))
                
                except ValueError:
                    continue
        
        return changes
    
    def _parse_new_locations(self, text: str) -> List[ContentGenerationRequest]:
        """解析新地点生成请求"""
        requests = []
        
        for pattern in self.new_location_patterns:
            matches = pattern.findall(text)
            for match in matches:
                location_desc = match.strip()
                
                # 清理和验证
                location_desc = self._clean_location_name(location_desc)
                
                if location_desc and len(location_desc) > 2:
                    requests.append(ContentGenerationRequest(
                        content_type=ContentType.LOCATION,
                        name=location_desc,
                        description=f"AI在叙述中提到的新地点: {location_desc}",
                        properties={
                            "location_type": self._guess_location_type(location_desc),
                            "description": f"一个名为{location_desc}的地方",
                            "auto_generated": True
                        },
                        confidence=0.6,
                        source_text=match
                    ))
        
        return requests
    
    def _parse_new_npcs(self, text: str) -> List[ContentGenerationRequest]:
        """解析新NPC生成请求"""
        requests = []
        
        for pattern in self.npc_patterns:
            matches = pattern.findall(text)
            for match in matches:
                npc_desc = match.strip()
                
                # 清理NPC描述
                npc_desc = self._clean_npc_name(npc_desc)
                
                if npc_desc and len(npc_desc) > 1:
                    requests.append(ContentGenerationRequest(
                        content_type=ContentType.NPC,
                        name=npc_desc,
                        description=f"AI在叙述中提到的NPC: {npc_desc}",
                        properties={
                            "personality": "friendly",  # 默认友好
                            "location": "current",      # 当前位置
                            "auto_generated": True
                        },
                        confidence=0.5,
                        source_text=match
                    ))
        
        return requests
    
    def _classify_content_type(self, content_desc: str) -> ContentType:
        """分类内容类型"""
        content_lower = content_desc.lower()
        
        location_keywords = ["城市", "村庄", "城镇", "森林", "山脉", "洞穴", "地牢", "房间", "建筑"]
        item_keywords = ["武器", "装备", "药剂", "物品", "宝物", "道具", "卷轴"]
        npc_keywords = ["商人", "守卫", "村民", "法师", "战士", "盗贼", "老人", "少女"]
        
        for keyword in location_keywords:
            if keyword in content_lower:
                return ContentType.LOCATION
                
        for keyword in item_keywords:
            if keyword in content_lower:
                return ContentType.ITEM
                
        for keyword in npc_keywords:
            if keyword in content_lower:
                return ContentType.NPC
        
        return ContentType.OBJECT  # 默认为对象
    
    def _extract_properties_from_desc(self, desc: str, content_type: ContentType) -> Dict[str, Any]:
        """从描述中提取属性"""
        properties = {"auto_generated": True}
        
        if content_type == ContentType.LOCATION:
            properties["location_type"] = self._guess_location_type(desc)
        elif content_type == ContentType.ITEM:
            properties["item_type"] = self._guess_item_type(desc)
        elif content_type == ContentType.NPC:
            properties["personality"] = "neutral"
        
        return properties
    
    def _clean_item_name(self, name: str) -> str:
        """清理物品名称"""
        # 移除常见的修饰词
        name = re.sub(r'[一二三四五六七八九十]+(?:个|件|把|支|瓶|张|本)', '', name)
        name = re.sub(r'(?:一些|若干|大量|少量)', '', name)
        name = name.strip()
        return name
    
    def _clean_location_name(self, name: str) -> str:
        """清理位置名称"""
        # 移除常见的修饰词
        name = re.sub(r'(?:一座|一个|一处|一间)', '', name)
        name = name.strip()
        return name
    
    def _clean_npc_name(self, name: str) -> str:
        """清理NPC名称"""
        # 移除常见的修饰词
        name = re.sub(r'(?:一个|一位|那个|这个)', '', name)
        name = name.strip()
        return name
    
    def _guess_location_type(self, desc: str) -> str:
        """推测位置类型"""
        desc_lower = desc.lower()
        
        if any(keyword in desc_lower for keyword in ["城市", "城镇", "镇"]):
            return "town"
        elif any(keyword in desc_lower for keyword in ["村庄", "村"]):
            return "town"
        elif any(keyword in desc_lower for keyword in ["森林", "树林"]):
            return "forest"
        elif any(keyword in desc_lower for keyword in ["山", "山脉", "山峰"]):
            return "mountain"
        elif any(keyword in desc_lower for keyword in ["洞穴", "洞", "洞窟"]):
            return "cave"
        elif any(keyword in desc_lower for keyword in ["地牢", "监牢"]):
            return "dungeon"
        else:
            return "wilderness"
    
    def _guess_item_type(self, desc: str) -> str:
        """推测物品类型"""
        desc_lower = desc.lower()
        
        if any(keyword in desc_lower for keyword in ["剑", "刀", "武器"]):
            return "weapon"
        elif any(keyword in desc_lower for keyword in ["药剂", "药水", "药"]):
            return "potion"
        elif any(keyword in desc_lower for keyword in ["食物", "面包", "肉"]):
            return "food"
        elif any(keyword in desc_lower for keyword in ["卷轴", "书"]):
            return "scroll"
        else:
            return "misc"
    
    def get_high_confidence_changes(self, changes: List[StateChangeIntent], 
                                  threshold: float = 0.7) -> List[StateChangeIntent]:
        """获取高置信度的状态变更"""
        return [change for change in changes if change.confidence >= threshold]
    
    def get_high_confidence_requests(self, requests: List[ContentGenerationRequest],
                                   threshold: float = 0.7) -> List[ContentGenerationRequest]:
        """获取高置信度的内容生成请求"""
        return [request for request in requests if request.confidence >= threshold]


# 便利函数
def parse_ai_response(text: str) -> Tuple[List[StateChangeIntent], List[ContentGenerationRequest]]:
    """便利函数：解析AI响应"""
    parser = ResponseParser()
    return parser.parse_response(text)