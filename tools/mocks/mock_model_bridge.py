"""
模型桥接器Mock实现

提供ModelBridge、ContextManager等通信组件的Mock实现，
支持模拟AI模型调用和消息传递。
"""

from typing import Dict, List, Any, Optional
import time
import random

from Agent.interfaces.communication_interfaces import (
    ModelBridge, ContextManager, PromptTemplate,
    IntentMessage, ExecutionMessage, ErrorMessage
)
from Agent.interfaces.data_structures import (
    Intent, IntentType, ExecutionResult
)


class MockContextManager(ContextManager):
    """上下文管理器Mock实现"""
    
    def build_intent_context(self, user_input: str, 
                           game_state: 'GameState') -> Dict[str, Any]:
        """构建意图识别的上下文"""
        return {
            'user_input': user_input,
            'current_location': game_state.player.get_location(),
            'player_hp': game_state.player.get_hp(),
            'turn': game_state.get_turn_count(),
            'recent_history': game_state.get_recent_history(3)
        }
    
    def build_execution_context(self, intent: Intent, 
                              game_state: 'GameState') -> Dict[str, Any]:
        """构建执行引擎的上下文"""
        return {
            'intent': intent.to_dict(),
            'player_state': game_state.player.to_dict(),
            'current_location_npcs': [
                npc.name for npc in game_state.world.get_all_npcs().values()
                if npc.alive
            ],
            'turn': game_state.get_turn_count()
        }
    
    def build_scene_context(self, execution_result: ExecutionResult,
                          intent: Intent, game_state: 'GameState') -> Dict[str, Any]:
        """构建场景生成的上下文"""
        return {
            'execution_result': execution_result.to_dict(),
            'original_intent': intent.to_dict(),
            'player_state': game_state.player.to_dict(),
            'world_context': {
                'location': game_state.player.get_location(),
                'nearby_npcs': [
                    npc.name for npc in game_state.world.get_all_npcs().values()
                    if npc.alive
                ]
            },
            'turn': game_state.get_turn_count(),
            'history': game_state.get_recent_history(2)
        }
    
    def get_history_context(self, game_state: 'GameState', 
                          limit: int = 5) -> List[Dict[str, Any]]:
        """获取历史上下文"""
        return game_state.get_recent_history(limit)


class MockPromptTemplate(PromptTemplate):
    """Prompt模板Mock实现"""
    
    def get_intent_recognition_prompt(self, user_input: str, 
                                    context: Dict[str, Any]) -> str:
        """获取意图识别的Prompt"""
        return f"""
分析玩家行动并输出JSON格式结果:

玩家输入: {user_input}
当前位置: {context.get('current_location', '未知')}
当前回合: {context.get('turn', 0)}

请分析意图并输出以下格式:
{{
  "type": "执行/查询/探索/推理",
  "category": "具体分类",
  "action": "行动描述",
  "target": "目标对象",
  "parameters": {{}},
  "confidence": 0.9
}}
"""
    
    def get_scene_generation_prompt(self, execution_message: ExecutionMessage) -> str:
        """获取场景生成的Prompt"""
        result = execution_message.execution_result
        intent = execution_message.original_intent
        
        return f"""
你是TRPG的城主(DM)，根据执行结果生成回复:

玩家意图: {intent.action}
执行结果: {result.action_taken}
成功状态: {'成功' if result.success else '失败'}

关键要求:
1. 基于执行结果给出具体回复
2. 如果有伤害数值，必须明确说出
3. 如果找到物品，必须说出具体物品名称
4. 避免使用"你感受到"、"似乎"等模糊描述
5. 给出玩家行动的明确结果

请生成沉浸式的回复文本。
"""
    
    def format_execution_result(self, execution_result: ExecutionResult) -> str:
        """格式化执行结果用于Prompt"""
        if execution_result.success:
            result_text = f"执行成功: {execution_result.action_taken}"
            
            # 添加骰子结果
            if execution_result.dice_results:
                dice_info = ", ".join([
                    f"{dr.name}:{dr.total}" 
                    for dr in execution_result.dice_results
                ])
                result_text += f" (骰子结果: {dice_info})"
            
            # 添加状态变更
            if execution_result.state_changes:
                changes_info = ", ".join([
                    f"{sc.target}的{sc.property}{sc.action}:{sc.value}"
                    for sc in execution_result.state_changes
                ])
                result_text += f" [状态变更: {changes_info}]"
            
            return result_text
        else:
            return f"执行失败: {execution_result.failure_reason}"


class MockModelBridge(ModelBridge):
    """模型桥接器Mock实现"""
    
    def __init__(self):
        self.context_manager = MockContextManager()
        self.prompt_template = MockPromptTemplate()
        self.call_history: List[Dict[str, Any]] = []
        
        # Mock的ExecutionEngine和GameState
        from .mock_execution_engine import MockExecutionEngine
        from .mock_game_state import MockGameState
        
        self.execution_engine = MockExecutionEngine()
        self.game_state = MockGameState()
        
        # 性能统计
        self.performance_stats = {
            'intent_classification_time': [],
            'execution_time': [],
            'scene_generation_time': [],
            'total_response_time': []
        }
    
    def process_user_input(self, user_input: str) -> str:
        """处理用户输入的完整流程"""
        start_time = time.time()
        
        try:
            # 记录调用
            call_record = {
                'user_input': user_input,
                'timestamp': start_time,
                'stages': {}
            }
            
            # Stage 1: 意图分类
            intent_start = time.time()
            intent_message = self.classify_intent(user_input)
            intent_time = time.time() - intent_start
            call_record['stages']['intent_classification'] = intent_time
            
            # Stage 2: 意图执行
            execution_start = time.time()
            execution_message = self.execute_intent(intent_message)
            execution_time = time.time() - execution_start
            call_record['stages']['execution'] = execution_time
            
            # Stage 3: 场景生成
            scene_start = time.time()
            scene_response = self.generate_scene(execution_message)
            scene_time = time.time() - scene_start
            call_record['stages']['scene_generation'] = scene_time
            
            total_time = time.time() - start_time
            call_record['total_time'] = total_time
            call_record['response'] = scene_response
            
            # 更新性能统计
            self.performance_stats['intent_classification_time'].append(intent_time)
            self.performance_stats['execution_time'].append(execution_time)
            self.performance_stats['scene_generation_time'].append(scene_time)
            self.performance_stats['total_response_time'].append(total_time)
            
            self.call_history.append(call_record)
            return scene_response
            
        except Exception as e:
            error = ErrorMessage(
                layer="ModelBridge",
                error_type="ProcessingError",
                message=str(e),
                original_input=user_input,
                timestamp=time.time()
            )
            return self.handle_error(error)
    
    def classify_intent(self, user_input: str) -> IntentMessage:
        """Layer 1: 意图分类"""
        # Mock意图识别逻辑
        context = self.context_manager.build_intent_context(user_input, self.game_state)
        
        # 简单的关键词匹配
        intent = self._mock_intent_classification(user_input)
        
        return IntentMessage(
            intent=intent,
            confidence=0.9,
            raw_input=user_input,
            context=context,
            timestamp=time.time()
        )
    
    def execute_intent(self, intent_message: IntentMessage) -> ExecutionMessage:
        """Layer 2: 意图执行"""
        # 使用Mock执行引擎处理
        execution_result = self.execution_engine.process(
            intent_message.intent, 
            self.game_state
        )
        
        return ExecutionMessage(
            execution_result=execution_result,
            original_intent=intent_message.intent,
            game_state_snapshot=self.game_state.create_snapshot(),
            rag_context="",  # Mock暂不实现RAG
            timestamp=time.time()
        )
    
    def generate_scene(self, execution_message: ExecutionMessage) -> str:
        """Layer 3: 场景生成"""
        # Mock场景生成逻辑
        result = execution_message.execution_result
        intent = execution_message.original_intent
        
        # 基于模板生成回复，确保给出具体结果
        if result.success:
            response = f"你{intent.action}。{result.action_taken}"
            
            # 添加具体的数值信息
            if result.dice_results:
                for dice in result.dice_results:
                    if dice.name == "伤害":
                        response += f"造成了{dice.total}点伤害。"
            
            # 添加发现的物品信息
            if result.state_changes:
                for change in result.state_changes:
                    if change.property == "items" and change.action == "add":
                        item_name = getattr(change.value, 'name', '未知物品')
                        response += f"你获得了{item_name}。"
            
            # 添加世界变化
            if result.world_changes:
                response += " ".join(result.world_changes)
            
            return response
        else:
            return f"你尝试{intent.action}，但是{result.failure_reason}。"
    
    def handle_error(self, error: ErrorMessage) -> str:
        """错误处理"""
        return f"抱歉，处理你的请求时遇到了问题: {error.message}"
    
    def _mock_intent_classification(self, user_input: str) -> Intent:
        """Mock意图分类逻辑"""
        user_input_lower = user_input.lower()
        
        # 简单的关键词匹配
        if any(keyword in user_input_lower for keyword in ["攻击", "打", "砍", "刺"]):
            # 提取目标
            target = "哥布林"  # 简化处理
            if "哥布林" in user_input:
                target = "哥布林"
            
            return Intent(
                type=IntentType.EXECUTION,
                category="攻击",
                action=f"攻击{target}",
                target=target,
                confidence=0.9
            )
        
        elif any(keyword in user_input_lower for keyword in ["搜索", "调查", "查看", "寻找"]):
            # 提取目标
            target = "书桌"  # 简化处理
            if "书桌" in user_input:
                target = "书桌"
            elif "箱子" in user_input:
                target = "箱子"
            
            return Intent(
                type=IntentType.EXECUTION,
                category="搜索",
                action=f"搜索{target}",
                target=target,
                confidence=0.85
            )
        
        else:
            # 默认为探索类
            return Intent(
                type=IntentType.EXPLORATION,
                category="其他",
                action=user_input,
                target="未知",
                confidence=0.6
            )
    
    # 测试和调试方法
    def get_call_history(self) -> List[Dict[str, Any]]:
        """获取调用历史"""
        return self.call_history.copy()
    
    def clear_call_history(self) -> None:
        """清空调用历史"""
        self.call_history.clear()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        summary = {}
        for metric_name, times in self.performance_stats.items():
            if times:
                summary[metric_name] = {
                    'avg': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'count': len(times)
                }
            else:
                summary[metric_name] = {'avg': 0, 'min': 0, 'max': 0, 'count': 0}
        return summary
    
    def reset_game_state(self) -> None:
        """重置游戏状态 - 用于测试"""
        from .mock_game_state import MockGameState
        self.game_state = MockGameState()