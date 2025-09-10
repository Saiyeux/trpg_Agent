"""
行动分发器

根据玩家意图分类，调用对应的行动处理函数。
支持动态扩展新的行动类型和处理逻辑。

主要功能:
- 意图到函数的映射
- 行动处理函数调用
- 扩展性支持
- 未知行动的默认处理
"""

from typing import Dict, Any, Callable, Optional
from ..core.game_state import GameState


class ActionDispatcher:
    """
    玩家行动分发器
    
    根据AI识别的玩家意图分类，调用相应的处理函数。
    支持动态注册新的行动类型处理器。
    """
    
    def __init__(self):
        """初始化行动分发器"""
        # 预定义的行动处理器映射
        self.action_handlers: Dict[str, Callable] = {
            '探索': self._handle_exploration,
            '对话': self._handle_dialogue,
            '调查': self._handle_investigation,
            '战斗': self._handle_combat,
            '购买': self._handle_purchase,
            '使用': self._handle_use_item,
            '移动': self._handle_movement,
            '休息': self._handle_rest,
            '学习': self._handle_learning,
            '制作': self._handle_crafting,
            '社交': self._handle_social,
            '交易': self._handle_trading
        }
        
    def dispatch_action(self, category: str, intent_data: Dict[str, Any], 
                       game_state: GameState) -> Optional[str]:
        """
        分发并执行玩家行动
        
        Args:
            category: 意图分类
            intent_data: 完整的意图数据
            game_state: 当前游戏状态
            
        Returns:
            行动执行结果描述，如果没有匹配的处理器则返回None
            
        调用时机: AI完成意图分析后
        """
        # 尝试找到匹配的处理器
        handler = self._find_handler(category)
        
        if handler:
            return handler(intent_data, game_state)
        else:
            return None  # 返回None表示使用默认的"生成回复"模式
            
    def register_handler(self, category: str, handler: Callable) -> None:
        """
        注册新的行动处理器
        
        Args:
            category: 意图分类名
            handler: 处理函数
            
        调用时机: 扩展新的行动类型时
        """
        self.action_handlers[category] = handler
        
    def unregister_handler(self, category: str) -> bool:
        """
        注销行动处理器
        
        Args:
            category: 意图分类名
            
        Returns:
            是否成功注销
        """
        if category in self.action_handlers:
            del self.action_handlers[category]
            return True
        return False
        
    def get_supported_categories(self) -> list[str]:
        """
        获取所有支持的行动分类
        
        Returns:
            支持的分类列表
            
        调用时机: 查看系统能力或调试时
        """
        return list(self.action_handlers.keys())
        
    def _find_handler(self, category: str) -> Optional[Callable]:
        """查找匹配的处理器，支持模糊匹配"""
        # 精确匹配
        if category in self.action_handlers:
            return self.action_handlers[category]
            
        # 模糊匹配（包含关系）
        category_lower = category.lower()
        for registered_category, handler in self.action_handlers.items():
            if (category_lower in registered_category.lower() or 
                registered_category.lower() in category_lower):
                return handler
                
        return None
        
    # ===== 预定义的行动处理器 =====
    
    def _handle_exploration(self, intent_data: Dict, game_state: GameState) -> str:
        """处理探索行动"""
        target = intent_data.get('target', '未知区域')
        return f"执行探索行动: 探索{target}"
        
    def _handle_dialogue(self, intent_data: Dict, game_state: GameState) -> str:
        """处理对话行动"""
        target = intent_data.get('target', '未知对象')
        return f"执行对话行动: 与{target}交流"
        
    def _handle_investigation(self, intent_data: Dict, game_state: GameState) -> str:
        """处理调查行动"""
        target = intent_data.get('target', '某物')
        return f"执行调查行动: 仔细调查{target}"
        
    def _handle_combat(self, intent_data: Dict, game_state: GameState) -> str:
        """处理战斗行动"""
        target = intent_data.get('target', '敌人')
        return f"执行战斗行动: 对{target}发起攻击"
        
    def _handle_purchase(self, intent_data: Dict, game_state: GameState) -> str:
        """处理购买行动"""
        target = intent_data.get('target', '物品')
        return f"执行购买行动: 购买{target}"
        
    def _handle_use_item(self, intent_data: Dict, game_state: GameState) -> str:
        """处理使用物品行动"""
        target = intent_data.get('target', '物品')
        return f"执行使用行动: 使用{target}"
        
    def _handle_movement(self, intent_data: Dict, game_state: GameState) -> str:
        """处理移动行动"""
        target = intent_data.get('target', '某处')
        return f"执行移动行动: 前往{target}"
        
    def _handle_rest(self, intent_data: Dict, game_state: GameState) -> str:
        """处理休息行动"""
        intent = intent_data.get('intent', '休息恢复')
        return f"执行休息行动: {intent}"
        
    def _handle_learning(self, intent_data: Dict, game_state: GameState) -> str:
        """处理学习行动"""
        target = intent_data.get('target', '技能')
        return f"执行学习行动: 学习{target}"
        
    def _handle_crafting(self, intent_data: Dict, game_state: GameState) -> str:
        """处理制作行动"""
        target = intent_data.get('target', '物品')
        return f"执行制作行动: 制作{target}"
        
    def _handle_social(self, intent_data: Dict, game_state: GameState) -> str:
        """处理社交行动"""
        target = intent_data.get('target', '角色')
        return f"执行社交行动: 与{target}进行社交互动"
        
    def _handle_trading(self, intent_data: Dict, game_state: GameState) -> str:
        """处理交易行动"""
        target = intent_data.get('target', '商品')
        return f"执行交易行动: 交易{target}"