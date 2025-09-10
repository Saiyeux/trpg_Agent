"""
意图分析器

负责玩家意图的识别、分类和统计分析。
提供意图记录、统计报告和数据分析功能。

主要功能:
- 意图数据记录和存储
- 实时统计分析
- 意图分布报告
- 历史数据查询
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter


class IntentData:
    """意图数据结构"""
    
    def __init__(self, intent: str, category: str, target: str, turn: int):
        """
        初始化意图数据
        
        Args:
            intent: 具体意图描述
            category: 意图分类
            target: 行动目标
            turn: 所在回合
        """
        self.intent = intent
        self.category = category
        self.target = target
        self.turn = turn


class IntentAnalyzer:
    """
    玩家意图分析器
    
    收集、分析和统计玩家在游戏中的所有意图行为。
    提供实时统计和详细的行为分析报告。
    """
    
    def __init__(self):
        """初始化意图分析器"""
        self.intents: List[IntentData] = []  # 所有意图记录
        self.categories: List[str] = []      # 所有分类记录（用于快速统计）
        
    def add_intent(self, raw_intent_data: str | Dict) -> bool:
        """
        添加新的意图记录
        
        Args:
            raw_intent_data: AI返回的原始意图数据（JSON字符串或字典）
            
        Returns:
            是否成功添加记录
            
        调用时机: 每次AI完成意图分析后
        """
        try:
            # 处理输入格式
            if isinstance(raw_intent_data, str):
                # 首先尝试直接解析
                try:
                    data = json.loads(raw_intent_data)
                except json.JSONDecodeError:
                    # 尝试从Markdown代码块中提取JSON
                    cleaned_json = self._extract_json_from_markdown(raw_intent_data)
                    if cleaned_json:
                        data = json.loads(cleaned_json)
                    else:
                        raise json.JSONDecodeError("无法提取有效JSON", raw_intent_data, 0)
            else:
                data = raw_intent_data
                
            # 创建意图记录
            intent_data = IntentData(
                intent=data.get('intent', '未知意图'),
                category=data.get('category', '未分类'),
                target=data.get('target', '未指定'),
                turn=len(self.intents) + 1
            )
            
            # 添加到记录中
            self.intents.append(intent_data)
            self.categories.append(intent_data.category)
            
            return True
            
        except (json.JSONDecodeError, KeyError, TypeError):
            # 解析失败时记录为未知意图
            self._add_unknown_intent()
            return False
            
    def _extract_json_from_markdown(self, text: str) -> str:
        """从Markdown代码块中提取JSON"""
        import re
        
        # 匹配```json...```格式
        json_pattern = r'```json\s*\n(.*?)\n```'
        match = re.search(json_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # 匹配```...```格式（没有json标记）
        code_pattern = r'```\s*\n(.*?)\n```'
        match = re.search(code_pattern, text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # 检查是否像JSON（以{开头，以}结尾）
            if content.startswith('{') and content.endswith('}'):
                return content
                
        return ""
            
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取完整的意图统计信息
        
        Returns:
            包含各种统计数据的字典
            
        调用时机: 游戏结束时或玩家查询统计时
        """
        if not self.intents:
            return self._empty_statistics()
            
        category_counter = Counter(self.categories)
        total_intents = len(self.intents)
        
        return {
            'total_intents': total_intents,
            'unique_categories': len(category_counter),
            'category_distribution': dict(category_counter),
            'most_common_category': category_counter.most_common(1)[0] if category_counter else None,
            'category_percentages': self._calculate_percentages(category_counter, total_intents),
            'turn_range': (1, total_intents) if total_intents > 0 else (0, 0)
        }
        
    def display_statistics(self) -> None:
        """
        在控制台显示统计信息
        
        调用时机: 游戏结束或玩家输入统计命令时
        """
        stats = self.get_statistics()
        
        print(f"\n=== 意图统计分析 ===")
        print(f"总意图数量: {stats['total_intents']}")
        print(f"意图类别数: {stats['unique_categories']}")
        
        if stats['total_intents'] > 0:
            print(f"\n各类别分布:")
            for category, percentage in stats['category_percentages'].items():
                count = stats['category_distribution'][category]
                print(f"  {category}: {count}次 ({percentage:.1f}%)")
            
            if stats['most_common_category']:
                most_common, count = stats['most_common_category']
                print(f"\n最常见意图: {most_common} ({count}次)")
                
        print("=" * 30)
                
    def get_recent_intents(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        获取最近的N个意图记录
        
        Args:
            n: 获取的记录数量
            
        Returns:
            最近的意图记录列表
            
        调用时机: 查看最近行为趋势时
        """
        recent_intents = self.intents[-n:] if len(self.intents) > n else self.intents
        
        return [
            {
                'intent': intent.intent,
                'category': intent.category,
                'target': intent.target,
                'turn': intent.turn
            }
            for intent in recent_intents
        ]
        
    def get_category_trend(self) -> List[str]:
        """
        获取意图分类的时间趋势
        
        Returns:
            按时间顺序的分类列表
            
        调用时机: 分析玩家行为模式时
        """
        return [intent.category for intent in self.intents]
        
    def search_intents_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        根据分类搜索意图记录
        
        Args:
            category: 要搜索的分类名
            
        Returns:
            符合条件的意图记录列表
            
        调用时机: 分析特定类型行为时
        """
        matching_intents = [
            intent for intent in self.intents 
            if intent.category.lower() == category.lower()
        ]
        
        return [
            {
                'intent': intent.intent,
                'category': intent.category,
                'target': intent.target,
                'turn': intent.turn
            }
            for intent in matching_intents
        ]
        
    def get_all_intents(self) -> List[Dict[str, Any]]:
        """
        获取所有意图记录
        
        Returns:
            完整的意图记录列表
            
        调用时机: 导出数据或详细分析时
        """
        return [
            {
                'intent': intent.intent,
                'category': intent.category,
                'target': intent.target,
                'turn': intent.turn
            }
            for intent in self.intents
        ]
        
    def _add_unknown_intent(self) -> None:
        """添加未知意图的默认记录"""
        unknown_intent = IntentData(
            intent="解析失败的意图",
            category="解析错误",
            target="未知",
            turn=len(self.intents) + 1
        )
        self.intents.append(unknown_intent)
        self.categories.append(unknown_intent.category)
        
    def _calculate_percentages(self, counter: Counter, total: int) -> Dict[str, float]:
        """计算各分类的百分比"""
        return {
            category: (count / total) * 100 
            for category, count in counter.items()
        }
        
    def _empty_statistics(self) -> Dict[str, Any]:
        """返回空统计数据"""
        return {
            'total_intents': 0,
            'unique_categories': 0,
            'category_distribution': {},
            'most_common_category': None,
            'category_percentages': {},
            'turn_range': (0, 0)
        }