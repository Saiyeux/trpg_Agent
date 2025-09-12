"""
消耗品数据框架

可填充的消耗品系统，支持各种药剂、食物、卷轴等物品。
包含物品效果、使用条件和堆叠规则。
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class ConsumableType(Enum):
    """消耗品类型"""
    POTION = "potion"         # 药剂
    FOOD = "food"             # 食物
    SCROLL = "scroll"         # 卷轴
    TOOL = "tool"             # 工具 (一次性)
    REAGENT = "reagent"       # 试剂/材料


class EffectType(Enum):
    """效果类型"""
    INSTANT = "instant"       # 即时效果
    OVER_TIME = "over_time"   # 持续效果
    BUFF = "buff"             # 增益效果
    DEBUFF = "debuff"         # 减益效果


@dataclass
class ItemEffect:
    """物品效果"""
    effect_type: EffectType
    target_attribute: str     # 目标属性
    value: int               # 效果数值
    duration: int = 0        # 持续时间 (秒，0表示即时)
    description: str = ""    # 效果描述


@dataclass
class ConsumableItem:
    """消耗品定义"""
    id: str                          # 物品ID
    name: str                        # 物品名称
    item_type: ConsumableType        # 物品类型
    description: str                 # 物品描述
    effects: List[ItemEffect]        # 物品效果列表
    max_stack: int = 99             # 最大堆叠数量
    use_conditions: Dict[str, Any] = None  # 使用条件
    rarity: str = "common"          # 稀有度
    value: int = 1                  # 物品价值
    weight: float = 0.1             # 物品重量


class ConsumableRegistry:
    """消耗品注册表"""
    
    def __init__(self):
        self.items: Dict[str, ConsumableItem] = {}
        self._init_default_items()
    
    def _init_default_items(self):
        """初始化默认消耗品 - 可填充扩展"""
        
        # === 药剂类 ===
        
        # 生命药剂
        self.register_item(ConsumableItem(
            id="health_potion_small",
            name="小型生命药剂",
            item_type=ConsumableType.POTION,
            description="恢复少量生命值的红色药剂",
            effects=[
                ItemEffect(EffectType.INSTANT, "current_hp", 50, 0, "立即恢复50点生命值")
            ],
            max_stack=10,
            rarity="common",
            value=25
        ))
        
        self.register_item(ConsumableItem(
            id="health_potion_medium",
            name="中型生命药剂",
            item_type=ConsumableType.POTION,
            description="恢复中等生命值的红色药剂",
            effects=[
                ItemEffect(EffectType.INSTANT, "current_hp", 150, 0, "立即恢复150点生命值")
            ],
            max_stack=5,
            rarity="uncommon",
            value=75
        ))
        
        # 魔法药剂
        self.register_item(ConsumableItem(
            id="mana_potion_small",
            name="小型魔法药剂",
            item_type=ConsumableType.POTION,
            description="恢复魔法值的蓝色药剂",
            effects=[
                ItemEffect(EffectType.INSTANT, "current_mp", 30, 0, "立即恢复30点魔法值")
            ],
            max_stack=10,
            rarity="common",
            value=20
        ))
        
        # 体力药剂
        self.register_item(ConsumableItem(
            id="stamina_potion",
            name="体力药剂",
            item_type=ConsumableType.POTION,
            description="恢复体力的黄色药剂",
            effects=[
                ItemEffect(EffectType.INSTANT, "stamina", 100, 0, "完全恢复体力值")
            ],
            max_stack=8,
            rarity="common",
            value=15
        ))
        
        # === 食物类 ===
        
        self.register_item(ConsumableItem(
            id="bread",
            name="面包",
            item_type=ConsumableType.FOOD,
            description="普通的面包，能恢复少量生命值",
            effects=[
                ItemEffect(EffectType.INSTANT, "current_hp", 20, 0, "恢复20点生命值")
            ],
            max_stack=20,
            rarity="common",
            value=5
        ))
        
        self.register_item(ConsumableItem(
            id="roasted_meat",
            name="烤肉",
            item_type=ConsumableType.FOOD,
            description="香喷喷的烤肉，提供持续恢复效果",
            effects=[
                ItemEffect(EffectType.OVER_TIME, "current_hp", 5, 60, "60秒内每秒恢复5点生命值")
            ],
            max_stack=10,
            rarity="common",
            value=12
        ))
        
        # === 卷轴类 ===
        
        self.register_item(ConsumableItem(
            id="fireball_scroll",
            name="火球术卷轴",
            item_type=ConsumableType.SCROLL,
            description="记录火球术的魔法卷轴",
            effects=[
                ItemEffect(EffectType.INSTANT, "spell_fireball", 1, 0, "释放一次火球术")
            ],
            max_stack=5,
            use_conditions={"min_intelligence": 8},
            rarity="uncommon",
            value=50
        ))
        
        self.register_item(ConsumableItem(
            id="healing_scroll",
            name="治疗卷轴",
            item_type=ConsumableType.SCROLL,
            description="记录治疗术的魔法卷轴",
            effects=[
                ItemEffect(EffectType.INSTANT, "current_hp", 100, 0, "立即恢复100点生命值")
            ],
            max_stack=3,
            rarity="uncommon",
            value=40
        ))
        
        # === 工具类 ===
        
        self.register_item(ConsumableItem(
            id="lockpick",
            name="开锁工具",
            item_type=ConsumableType.TOOL,
            description="用于开锁的精密工具",
            effects=[
                ItemEffect(EffectType.BUFF, "lockpick_skill", 10, 0, "开锁时技能+10")
            ],
            max_stack=20,
            rarity="common",
            value=8
        ))
        
        self.register_item(ConsumableItem(
            id="strength_elixir",
            name="力量药剂",
            item_type=ConsumableType.POTION,
            description="临时增强力量的珍贵药剂",
            effects=[
                ItemEffect(EffectType.BUFF, "strength", 5, 300, "5分钟内力量+5")
            ],
            max_stack=3,
            rarity="rare",
            value=100
        ))
        
        # === 试剂材料类 ===
        
        self.register_item(ConsumableItem(
            id="magic_dust",
            name="魔法粉尘",
            item_type=ConsumableType.REAGENT,
            description="制作魔法物品的基础材料",
            effects=[],  # 材料本身无效果，用于合成
            max_stack=50,
            rarity="common",
            value=3
        ))
    
    def register_item(self, item: ConsumableItem):
        """注册物品"""
        self.items[item.id] = item
    
    def get_item(self, item_id: str) -> Optional[ConsumableItem]:
        """获取物品定义"""
        return self.items.get(item_id)
    
    def get_items_by_type(self, item_type: ConsumableType) -> List[ConsumableItem]:
        """按类型获取物品"""
        return [item for item in self.items.values() if item.item_type == item_type]
    
    def get_items_by_rarity(self, rarity: str) -> List[ConsumableItem]:
        """按稀有度获取物品"""
        return [item for item in self.items.values() if item.rarity == rarity]
    
    def search_items(self, name_pattern: str) -> List[ConsumableItem]:
        """搜索物品"""
        return [item for item in self.items.values() 
                if name_pattern.lower() in item.name.lower()]


class InventorySlot:
    """背包槽位"""
    
    def __init__(self, item_id: str, quantity: int = 1):
        self.item_id = item_id
        self.quantity = quantity
    
    def can_stack_with(self, other_item_id: str, registry: ConsumableRegistry) -> bool:
        """检查是否可以堆叠"""
        if self.item_id != other_item_id:
            return False
        
        item_def = registry.get_item(self.item_id)
        return item_def and self.quantity < item_def.max_stack
    
    def add_quantity(self, amount: int, registry: ConsumableRegistry) -> int:
        """添加数量，返回溢出数量"""
        item_def = registry.get_item(self.item_id)
        if not item_def:
            return amount
        
        can_add = min(amount, item_def.max_stack - self.quantity)
        self.quantity += can_add
        return amount - can_add


class PlayerInventory:
    """玩家背包系统"""
    
    def __init__(self, max_slots: int = 30):
        self.max_slots = max_slots
        self.slots: List[Optional[InventorySlot]] = [None] * max_slots
        self.registry = ConsumableRegistry()
    
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """添加物品到背包"""
        if not self.registry.get_item(item_id):
            return False
        
        remaining = quantity
        
        # 先尝试堆叠到现有槽位
        for slot in self.slots:
            if slot and slot.can_stack_with(item_id, self.registry) and remaining > 0:
                overflow = slot.add_quantity(remaining, self.registry)
                remaining = overflow
        
        # 如果还有剩余，使用空槽位
        while remaining > 0:
            empty_slot = self._find_empty_slot()
            if empty_slot is None:
                return False  # 背包已满
            
            item_def = self.registry.get_item(item_id)
            take_amount = min(remaining, item_def.max_stack)
            self.slots[empty_slot] = InventorySlot(item_id, take_amount)
            remaining -= take_amount
        
        return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """从背包移除物品"""
        remaining = quantity
        
        for i, slot in enumerate(self.slots):
            if slot and slot.item_id == item_id and remaining > 0:
                take_amount = min(remaining, slot.quantity)
                slot.quantity -= take_amount
                remaining -= take_amount
                
                if slot.quantity <= 0:
                    self.slots[i] = None
        
        return remaining == 0
    
    def get_item_count(self, item_id: str) -> int:
        """获取物品数量"""
        total = 0
        for slot in self.slots:
            if slot and slot.item_id == item_id:
                total += slot.quantity
        return total
    
    def _find_empty_slot(self) -> Optional[int]:
        """查找空槽位"""
        for i, slot in enumerate(self.slots):
            if slot is None:
                return i
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """导出背包数据"""
        items = []
        for slot in self.slots:
            if slot:
                item_def = self.registry.get_item(slot.item_id)
                items.append({
                    "id": slot.item_id,
                    "name": item_def.name if item_def else "未知物品",
                    "quantity": slot.quantity,
                    "type": item_def.item_type.value if item_def else "unknown"
                })
        
        return {
            "max_slots": self.max_slots,
            "used_slots": len([s for s in self.slots if s is not None]),
            "items": items
        }