"""
核心数据结构定义

定义系统中所有核心数据结构，这些是模块间通信的基础契约。
遵循接口优先设计原则，确保数据流的完整性和一致性。
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json


class IntentType(Enum):
    """意图类型枚举"""
    EXECUTION = "执行"      # 执行动作类
    QUERY = "查询"          # 查询类  
    EXPLORATION = "探索"    # 探索对话类
    REASONING = "推理"      # 推理想象类


@dataclass
class Intent:
    """
    意图对象 - Layer 1 意图识别层的输出
    
    这是意图识别AI的标准输出格式，包含玩家行动的完整意图信息。
    """
    type: IntentType                    # 意图类型
    category: str                       # 具体分类(攻击/搜索/移动等)
    action: str                         # 用户行动描述
    target: str                         # 目标对象
    parameters: Dict[str, Any] = field(default_factory=dict)  # 扩展参数
    confidence: float = 1.0             # 识别置信度
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，便于序列化"""
        return {
            'type': self.type.value,
            'category': self.category,
            'action': self.action,
            'target': self.target,
            'parameters': self.parameters,
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Intent':
        """从字典创建Intent对象"""
        return cls(
            type=IntentType(data['type']),
            category=data['category'],
            action=data['action'], 
            target=data['target'],
            parameters=data.get('parameters', {}),
            confidence=data.get('confidence', 1.0)
        )


@dataclass  
class DiceRoll:
    """骰子结果"""
    name: str           # 骰子名称(攻击检定/伤害等)
    dice_type: str      # 骰子类型(d20/d6等)
    result: int         # 骰子结果
    modifier: int = 0   # 修正值
    total: int = field(init=False)  # 总值
    
    def __post_init__(self):
        """计算总值"""
        self.total = self.result + self.modifier


@dataclass
class StateChange:
    """
    状态变更对象
    
    描述游戏状态的具体变更，支持事务化的状态管理。
    """
    target: str         # 变更目标: "player"/"world"/"npc_name"
    action: str         # 操作类型: "add"/"remove"/"modify"/"set"
    property: str       # 属性名: "hp"/"items"/"location"
    value: Any          # 新值或变化量
    old_value: Any = None  # 原始值(用于回滚)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'target': self.target,
            'action': self.action,
            'property': self.property,
            'value': self.value,
            'old_value': self.old_value
        }


@dataclass
class Concept:
    """
    动态概念对象
    
    用于运行时创建的新概念(技能/状态效果/物品等)
    """
    type: str                           # 概念类型: "技能"/"状态效果"/"物品"等
    name: str                           # 概念名称
    description: str                    # 描述
    properties: Dict[str, Any] = field(default_factory=dict)  # 属性
    created_turn: int = 0               # 创建回合
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'type': self.type,
            'name': self.name,
            'description': self.description,
            'properties': self.properties,
            'created_turn': self.created_turn
        }


@dataclass
class ExecutionResult:
    """
    执行结果对象 - Layer 2 执行引擎层的输出
    
    这是解决AI回避具体结果问题的关键数据结构。
    包含行动的完整执行结果，确保场景生成AI能够给出具体回复。
    """
    success: bool                       # 执行是否成功
    action_taken: str                   # 具体执行的行动描述
    state_changes: List[StateChange] = field(default_factory=list)  # 状态变更列表
    dice_results: List[DiceRoll] = field(default_factory=list)      # 骰子结果
    world_changes: List[str] = field(default_factory=list)          # 世界变化描述
    new_concepts: List[Concept] = field(default_factory=list)       # 新创建的概念
    failure_reason: str = ""            # 失败原因(如果失败)
    additional_info: Dict[str, Any] = field(default_factory=dict)   # 额外信息
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，便于传递给场景生成AI"""
        return {
            'success': self.success,
            'action_taken': self.action_taken,
            'state_changes': [sc.to_dict() for sc in self.state_changes],
            'dice_results': [
                {
                    'name': dr.name,
                    'dice_type': dr.dice_type,
                    'result': dr.result,
                    'modifier': dr.modifier,
                    'total': dr.total
                } for dr in self.dice_results
            ],
            'world_changes': self.world_changes,
            'new_concepts': [nc.to_dict() for nc in self.new_concepts],
            'failure_reason': self.failure_reason,
            'additional_info': self.additional_info
        }
    
    def get_summary(self) -> str:
        """获取结果摘要，用于快速展示"""
        if self.success:
            summary = f"成功: {self.action_taken}"
            if self.dice_results:
                dice_info = ", ".join([f"{dr.name}:{dr.total}" for dr in self.dice_results])
                summary += f" ({dice_info})"
            return summary
        else:
            return f"失败: {self.failure_reason}"


# 工厂函数，便于创建常用的对象

def create_attack_intent(target: str, weapon: str = "武器") -> Intent:
    """创建攻击意图"""
    return Intent(
        type=IntentType.EXECUTION,
        category="攻击",
        action=f"使用{weapon}攻击{target}",
        target=target,
        parameters={"weapon": weapon}
    )


def create_search_intent(target: str, location: str = "") -> Intent:
    """创建搜索意图"""
    return Intent(
        type=IntentType.EXECUTION,
        category="搜索",
        action=f"搜索{target}",
        target=target,
        parameters={"location": location}
    )


def create_successful_result(action: str, changes: List[StateChange] = None, 
                           dice_results: List[DiceRoll] = None) -> ExecutionResult:
    """创建成功执行结果"""
    return ExecutionResult(
        success=True,
        action_taken=action,
        state_changes=changes or [],
        dice_results=dice_results or []
    )


def create_failed_result(action: str, reason: str) -> ExecutionResult:
    """创建失败执行结果"""
    return ExecutionResult(
        success=False,
        action_taken=action,
        failure_reason=reason
    )