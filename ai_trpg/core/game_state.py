"""
游戏状态管理模块

负责维护TRPG游戏的所有状态信息，包括玩家信息、历史记录、当前场景等。
提供状态查询、历史管理和上下文提取功能。

主要功能:
- 游戏状态存储和更新
- 历史记录管理  
- 智能上下文提取
- 回合计数和追踪
"""

from typing import List, Dict, Any, Optional


class GameState:
    """
    TRPG游戏状态管理器
    
    管理整个游戏会话的状态，包括玩家信息、历史记录、当前场景等。
    支持动态上下文管理，可根据AI模型的能力调整历史记录的使用量。
    """
    
    def __init__(self):
        """初始化游戏状态"""
        self.current_scene: str = ""          # 当前场景描述
        self.player_name: str = ""            # 玩家角色名
        self.turn_count: int = 0              # 当前回合数
        self.game_history: List[Dict[str, Any]] = []  # 完整游戏历史
        
    def add_to_history(self, entry_type: str, content: str) -> None:
        """
        添加新的历史记录条目
        
        Args:
            entry_type: 条目类型，如'玩家行动'、'场景'、'系统消息'等
            content: 条目内容
        
        调用时机: 每次玩家行动或场景更新后
        """
        self.game_history.append({
            'turn': self.turn_count,
            'type': entry_type,
            'content': content,
            'timestamp': self._get_timestamp()
        })
        
    def get_context(self, last_n: int = 3, context_limit: int = 32000) -> List[Dict[str, Any]]:
        """
        获取用于AI推理的上下文历史
        
        Args:
            last_n: 默认获取的最近条目数量
            context_limit: AI模型的上下文token限制
            
        Returns:
            适合当前AI模型的历史记录列表
            
        调用时机: AI模型生成场景或分析意图前
        
        智能调整规则:
        - 长上下文模型(>=100K): 扩展到最多50条记录
        - 短上下文模型(<100K): 保持默认数量以避免超限
        """
        # 根据模型能力动态调整历史数量
        if context_limit >= 100000:  # 长上下文模型如Hermes 4
            last_n = min(last_n * 10, 50)  # 扩展到50条记录
        
        # 返回最近的N条记录
        return self.game_history[-last_n:] if len(self.game_history) > last_n else self.game_history
        
    def get_full_history(self) -> List[Dict[str, Any]]:
        """
        获取完整的游戏历史记录
        
        Returns:
            完整的历史记录列表
            
        调用时机: 游戏结束后生成总结或导出存档时
        """
        return self.game_history.copy()
        
    def next_turn(self) -> None:
        """
        推进到下一回合
        
        调用时机: 每轮玩家输入处理开始前
        """
        self.turn_count += 1
        
    def get_game_info(self) -> Dict[str, Any]:
        """
        获取当前游戏的基本信息
        
        Returns:
            包含玩家名、回合数、历史条数等信息的字典
            
        调用时机: 显示游戏状态或生成报告时
        """
        return {
            'player_name': self.player_name,
            'turn_count': self.turn_count,
            'current_scene': self.current_scene,
            'history_count': len(self.game_history)
        }
        
    def _get_timestamp(self) -> str:
        """
        获取当前时间戳
        
        Returns:
            格式化的时间字符串
        """
        import datetime
        return datetime.datetime.now().strftime('%H:%M:%S')
        
    def clear_old_history(self, keep_recent: int = 100) -> int:
        """
        清理过旧的历史记录以节省内存
        
        Args:
            keep_recent: 保留的最近记录数量
            
        Returns:
            清理掉的记录数量
            
        调用时机: 长时间游戏后，历史记录过多时
        """
        if len(self.game_history) <= keep_recent:
            return 0
            
        old_count = len(self.game_history)
        self.game_history = self.game_history[-keep_recent:]
        return old_count - len(self.game_history)