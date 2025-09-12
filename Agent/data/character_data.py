"""
角色属性数据框架

可填充的角色属性系统，支持扩展和自定义。
包含基础属性、派生属性和状态管理。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class AttributeType(Enum):
    """属性类型"""
    PRIMARY = "primary"      # 基础属性 (力量、敏捷等)
    DERIVED = "derived"      # 派生属性 (HP、MP等)
    RESOURCE = "resource"    # 资源属性 (当前HP、当前MP等)
    SKILL = "skill"          # 技能属性
    SOCIAL = "social"        # 社交属性 (声望、关系等)


@dataclass
class AttributeDefinition:
    """属性定义"""
    name: str                           # 属性名称
    display_name: str                   # 显示名称
    attribute_type: AttributeType       # 属性类型
    base_value: int = 0                # 基础值
    min_value: int = 0                 # 最小值
    max_value: Optional[int] = None    # 最大值 (None表示无限制)
    description: str = ""              # 描述
    calculation: Optional[str] = None   # 计算公式 (用于派生属性)


class CharacterAttributes:
    """角色属性系统"""
    
    def __init__(self):
        # 基础属性定义 - 可扩展
        self.attribute_definitions: Dict[str, AttributeDefinition] = {}
        self.current_values: Dict[str, int] = {}
        self._init_default_attributes()
    
    def _init_default_attributes(self):
        """初始化默认属性 - 可填充扩展"""
        
        # 基础属性
        self.define_attribute("strength", "力量", AttributeType.PRIMARY, 10, 1, 20, "物理力量和近战伤害")
        self.define_attribute("dexterity", "敏捷", AttributeType.PRIMARY, 10, 1, 20, "行动速度和命中率")
        self.define_attribute("intelligence", "智力", AttributeType.PRIMARY, 10, 1, 20, "魔法威力和学习能力")
        self.define_attribute("constitution", "体质", AttributeType.PRIMARY, 10, 1, 20, "生命值和抗性")
        
        # 派生属性 (根据基础属性计算)
        self.define_attribute("max_hp", "最大生命值", AttributeType.DERIVED, 0, 1, None, "最大生命值", "constitution * 10 + level * 5")
        self.define_attribute("max_mp", "最大魔法值", AttributeType.DERIVED, 0, 0, None, "最大魔法值", "intelligence * 8 + level * 3")
        self.define_attribute("attack_power", "攻击力", AttributeType.DERIVED, 0, 1, None, "物理攻击力", "strength * 2")
        self.define_attribute("magic_power", "魔法威力", AttributeType.DERIVED, 0, 0, None, "魔法攻击力", "intelligence * 1.5")
        
        # 资源属性 (当前值)
        self.define_attribute("current_hp", "当前生命值", AttributeType.RESOURCE, 0, 0, None, "当前生命值")
        self.define_attribute("current_mp", "当前魔法值", AttributeType.RESOURCE, 0, 0, None, "当前魔法值")
        self.define_attribute("stamina", "体力", AttributeType.RESOURCE, 100, 0, 100, "体力值")
        
        # 技能属性
        self.define_attribute("sword_skill", "剑术", AttributeType.SKILL, 0, 0, 100, "剑类武器熟练度")
        self.define_attribute("magic_skill", "魔法学", AttributeType.SKILL, 0, 0, 100, "魔法释放熟练度")
        self.define_attribute("lockpick_skill", "开锁术", AttributeType.SKILL, 0, 0, 100, "开锁技能熟练度")
        
        # 社交属性
        self.define_attribute("reputation", "声望", AttributeType.SOCIAL, 0, -100, 100, "在世界中的名声")
        self.define_attribute("charisma", "魅力", AttributeType.SOCIAL, 10, 1, 20, "社交魅力值")
        
        # 特殊属性
        self.define_attribute("level", "等级", AttributeType.PRIMARY, 1, 1, 99, "角色等级")
        self.define_attribute("experience", "经验值", AttributeType.RESOURCE, 0, 0, None, "当前经验值")
    
    def define_attribute(self, key: str, name: str, attr_type: AttributeType, 
                        base_value: int = 0, min_val: int = 0, max_val: Optional[int] = None,
                        description: str = "", calculation: Optional[str] = None):
        """定义新属性"""
        self.attribute_definitions[key] = AttributeDefinition(
            name=key,
            display_name=name,
            attribute_type=attr_type,
            base_value=base_value,
            min_value=min_val,
            max_value=max_val,
            description=description,
            calculation=calculation
        )
        self.current_values[key] = base_value
    
    def get_attribute(self, key: str) -> int:
        """获取属性值"""
        if key not in self.current_values:
            return 0
        
        # 如果是派生属性，计算当前值
        if key in self.attribute_definitions:
            definition = self.attribute_definitions[key]
            if definition.attribute_type == AttributeType.DERIVED and definition.calculation:
                return self._calculate_derived_value(key, definition.calculation)
        
        return self.current_values[key]
    
    def set_attribute(self, key: str, value: int) -> bool:
        """设置属性值"""
        if key not in self.attribute_definitions:
            return False
        
        definition = self.attribute_definitions[key]
        
        # 检查范围
        if value < definition.min_value:
            value = definition.min_value
        if definition.max_value is not None and value > definition.max_value:
            value = definition.max_value
        
        self.current_values[key] = value
        return True
    
    def modify_attribute(self, key: str, delta: int) -> bool:
        """修改属性值 (相对变化)"""
        current = self.get_attribute(key)
        return self.set_attribute(key, current + delta)
    
    def _calculate_derived_value(self, key: str, formula: str) -> int:
        """计算派生属性值 - 简化版本"""
        # 这里可以实现更复杂的公式解析
        # 目前提供基本示例
        try:
            # 替换公式中的属性名为实际值
            safe_formula = formula
            for attr_key, value in self.current_values.items():
                safe_formula = safe_formula.replace(attr_key, str(value))
            
            # 简单的数学表达式求值
            result = eval(safe_formula)
            return int(result)
        except:
            return self.current_values.get(key, 0)
    
    def get_attributes_by_type(self, attr_type: AttributeType) -> Dict[str, int]:
        """按类型获取属性"""
        result = {}
        for key, definition in self.attribute_definitions.items():
            if definition.attribute_type == attr_type:
                result[key] = self.get_attribute(key)
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """导出为字典"""
        return {
            "attributes": {
                key: {
                    "value": self.get_attribute(key),
                    "definition": {
                        "display_name": definition.display_name,
                        "type": definition.attribute_type.value,
                        "description": definition.description
                    }
                }
                for key, definition in self.attribute_definitions.items()
            }
        }


# 预定义角色模板 - 可扩展填充
CHARACTER_TEMPLATES = {
    "战士": {
        "strength": 15,
        "dexterity": 12,
        "intelligence": 8,
        "constitution": 14,
        "sword_skill": 20,
        "description": "近战专精的勇敢战士"
    },
    
    "法师": {
        "strength": 8,
        "dexterity": 10,
        "intelligence": 16,
        "constitution": 10,
        "magic_skill": 25,
        "description": "掌握神秘魔法的学者"
    },
    
    "盗贼": {
        "strength": 10,
        "dexterity": 16,
        "intelligence": 12,
        "constitution": 10,
        "lockpick_skill": 30,
        "description": "敏捷灵活的潜行专家"
    }
}


def create_character(template_name: str = None) -> CharacterAttributes:
    """创建角色"""
    character = CharacterAttributes()
    
    if template_name and template_name in CHARACTER_TEMPLATES:
        template = CHARACTER_TEMPLATES[template_name]
        
        for attr_key, value in template.items():
            if attr_key != "description":
                character.set_attribute(attr_key, value)
        
        # 初始化资源属性
        character.set_attribute("current_hp", character.get_attribute("max_hp"))
        character.set_attribute("current_mp", character.get_attribute("max_mp"))
    
    return character