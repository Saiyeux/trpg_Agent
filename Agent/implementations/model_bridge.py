"""
真实的ModelBridge实现

基于现有ModelClient实现三层AI调用架构，支持意图分类、执行处理和场景生成。
"""

import json
import time
from typing import Dict, Any, List, Optional
from ..interfaces.communication_interfaces import (
    ModelBridge, IntentMessage, ExecutionMessage, ContextManager, PromptTemplate
)
from ..interfaces.data_structures import Intent, ExecutionResult, IntentType
from ..interfaces.state_interfaces import GameState
from ..interfaces.execution_interfaces import ExecutionEngine
from ..client.model_client import ModelClient, APIType
from .dynamic_content_generator import DynamicContentGenerator


class SimpleContextManager(ContextManager):
    """简单的上下文管理器实现"""
    
    def build_intent_context(self, user_input: str, game_state: GameState) -> Dict[str, Any]:
        """构建意图识别的上下文"""
        world = getattr(game_state, 'world_state', game_state.world)
        npcs = world.npcs
        # 处理npcs可能是dict或list的情况
        if isinstance(npcs, dict):
            npcs = npcs.values()
        return {
            'current_location': world.current_location,
            'player_hp': game_state.player_state.hp,
            'inventory_count': len(game_state.player_state.inventory),
            'nearby_npcs': [npc.name for npc in npcs]
        }
    
    def build_execution_context(self, intent: Intent, game_state: GameState) -> Dict[str, Any]:
        """构建执行引擎的上下文"""
        return {
            'intent_type': intent.type,
            'intent_target': intent.target,
            'player_state': {
                'hp': game_state.player_state.hp,
                'max_hp': game_state.player_state.max_hp,
                'inventory': [item.name for item in game_state.player_state.inventory]
            }
        }
    
    def build_scene_context(self, execution_result: ExecutionResult, 
                          intent: Intent, game_state: GameState) -> Dict[str, Any]:
        """构建场景生成的上下文"""
        return {
            'action_successful': execution_result.success,
            'action_taken': execution_result.action_taken,
            'state_changes': [f"{change.target} {change.property}: {change.old_value}→{change.value}" for change in execution_result.state_changes],
            'current_scene': game_state.world_state.current_location
        }
    
    def get_history_context(self, game_state: GameState, limit: int = 5) -> List[Dict[str, Any]]:
        """获取历史上下文"""
        # 简化实现，返回最近的历史记录
        history = []
        if hasattr(game_state, 'history') and game_state.history:
            for entry in game_state.history[-limit:]:
                history.append({
                    'type': 'action',
                    'content': entry.get('description', '')
                })
        return history


class TRPGPromptTemplate(PromptTemplate):
    """TRPG专用的Prompt模板"""
    
    def get_intent_recognition_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        """获取意图识别的Prompt"""
        nearby_npcs = ", ".join(context.get('nearby_npcs', []))
        
        prompt = f"""你是专业的TRPG游戏意图分析师。你的任务是准确分析玩家输入并返回结构化的意图信息。

## 当前游戏环境
- 位置：{context.get('current_location', '未知')}
- 玩家血量：{context.get('player_hp', 0)}
- 背包物品：{context.get('inventory_count', 0)}个
- 附近NPC：{nearby_npcs if nearby_npcs else '无'}

## 玩家输入
"{user_input}"

## 意图分类标准
**攻击**: 包含"攻击"、"打"、"砍"、"刺"、"射击"、"战斗"、"杀"、"击"等词汇
**搜索**: 包含"搜索"、"寻找"、"查看"、"观察"、"探索"、"检查"等词汇  
**对话**: 包含"说话"、"交谈"、"询问"、"告诉"、"对话"、"和...对话"、"与...交谈"、"问"、"聊天"等词汇
**交易**: 包含"购买"、"买"、"交易"、"售卖"、"商店"、"花钱"、"支付"等词汇
**移动**: 包含"去"、"走"、"移动"、"进入"、"离开"、"前往"等词汇
**状态查询**: 包含"状态"、"属性"、"背包"、"血量"、"技能"、"查看我的"等词汇
**交互**: 包含"撬锁"、"开锁"、"使用"、"激活"、"触发"、"操作"、"拉"、"推"、"按"、"转动"、"施展"、"释放技能"、"技能"等词汇

## 目标识别要求 ⚠️ 严格遵守
- 如果提到具体名词（如"哥布林"、"宝箱"、"商人"），直接使用该名词
- 如果使用代词（如"它"、"他"），根据上下文推断具体目标  
- **【重要】如果没有明确目标，必须使用"未指定"，绝对禁止添加默认目标**
- **【禁止】绝对不要自动添加"哥布林"、"敌人"等默认目标**
- **【检查】输出前务必检查：用户是否明确提到了目标？没有则必须标记"未指定"**

## 【特别警告】常见错误纠正
❌ 错误示例: "攻击" → target: "哥布林" (用户没提到哥布林!)
✅ 正确示例: "攻击" → target: "未指定"
❌ 错误示例: "施放火球术" → target: "哥布林" (用户没提到哥布林!)  
✅ 正确示例: "施放火球术" → target: "未指定"
❌ 错误示例: "使用技能" → category: "其他" (技能使用是交互!)
✅ 正确示例: "使用技能" → category: "交互"

## 输出格式
请返回纯JSON格式，不要使用代码块包装：
{{
    "type": "执行",
    "category": "攻击|搜索|对话|交易|移动|状态查询|交互|其他",
    "target": "明确的目标对象（如哥布林、商人、宝箱）或'未指定'",
    "description": "玩家想要执行的具体动作描述"
}}

## 严格要求
1. category必须精确使用以下值之一：攻击|搜索|对话|交易|移动|状态查询|交互|其他
2. 禁止在category中添加"类"字，如"对话类"是错误的，应该是"对话"
3. target必须具体明确，如无明确目标必须使用"未指定"
4. description要准确反映玩家的核心意图
5. 输出必须是有效的JSON格式，不要添加任何注释或说明文本

## 类别选择示例
- "和商人对话" → category: "对话", target: "商人"
- "购买物品" → category: "交易", target: "商人"
- "查看状态" → category: "状态查询", target: "自己"
- "攻击哥布林" → category: "攻击", target: "哥布林"
- "搜索宝箱" → category: "搜索", target: "宝箱"
- "撬锁" → category: "交互", target: "未指定"
- "攻击" → category: "攻击", target: "未指定"

请严格按照要求返回JSON："""
        return prompt
    
    def get_scene_generation_prompt(self, execution_message: ExecutionMessage) -> str:
        """获取场景生成的Prompt"""
        result = execution_message.execution_result
        intent = execution_message.original_intent
        
        # 格式化状态变更
        changes_text = ""
        if result.state_changes:
            changes_text = "\n".join([f"- {change.target} {change.property}变更: {change.old_value}→{change.value}" for change in result.state_changes])
        
        # 根据成功/失败生成不同的引导
        success_indicator = "✅ 成功" if result.success else "❌ 失败"
        
        prompt = f"""你是专业的TRPG城主，负责根据游戏执行结果生成沉浸式的场景描述。

## 执行情况总览
状态：{success_indicator}
玩家意图：{intent.action}
实际行动：{result.action_taken}

## 状态变更详情
{changes_text if changes_text else '无状态变更'}

## 骰子结果
{self._format_dice_results(result.dice_results)}

## 【重要】强制描述要求
你必须使用以下句式模板，禁止偏离：

**攻击成功时**：
"你的[武器/攻击方式]准确命中[目标]，造成[具体数值]点伤害。[目标]的生命值从[原值]降至[新值]点。"

**攻击失败时**：
"你的攻击落空了，[目标]敏捷地躲开了你的[武器/攻击方式]。[目标]的生命值保持在[数值]点。"

**搜索成功时**：
"你仔细搜索[地点/对象]，发现了[具体物品名称]。"

**搜索失败时**：
"你搜索了[地点/对象]，没有发现任何有用的物品。"

## 严格禁用词汇
以下词汇绝对禁止出现在描述中：
- "似乎"、"好像"、"仿佛"、"大概"
- "可能"、"也许"、"或许"、"应该"
- "感觉"、"看起来"、"听起来"
- "某种程度上"、"一定程度上"

## 必须包含内容
1. **精确数值**：每个涉及数值的结果都必须给出具体数字
2. **明确结果**：行动的成功/失败状态必须明确声明
3. **具体物品**：如果涉及物品，必须给出具体名称
4. **状态变化**：如果有属性变化，必须说明变化前后的具体数值

## 写作要求
- 语言生动形象，但绝对准确
- 使用断定式语句，不使用推测性表达
- 控制在100-200字内
- 使用第二人称"你"称呼玩家
- 每个句子都必须包含具体的、可量化的信息

请严格按照上述模板生成场景描述："""
        return prompt
    
    def format_execution_result(self, execution_result: ExecutionResult) -> str:
        """格式化执行结果用于Prompt"""
        return f"行动：{execution_result.action_taken}，成功：{execution_result.success}"
    
    def _format_dice_results(self, dice_results) -> str:
        """格式化骰子结果"""
        if not dice_results:
            return "无骰子投掷"
        
        formatted = []
        for dice in dice_results:
            formatted.append(f"{dice.name}: {dice.dice_type} = {dice.result} + {dice.modifier} = {dice.total}")
        return "\n".join(formatted)


class RealModelBridge(ModelBridge):
    """真实的ModelBridge实现"""
    
    def __init__(self, model_client: ModelClient, execution_engine: ExecutionEngine, 
                 game_state: GameState):
        """
        初始化ModelBridge
        
        Args:
            model_client: AI模型客户端
            execution_engine: 执行引擎
            game_state: 游戏状态
        """
        self.model_client = model_client
        self.execution_engine = execution_engine
        self.game_state = game_state
        self.context_manager = SimpleContextManager()
        self.prompt_template = TRPGPromptTemplate()
        self.content_generator = DynamicContentGenerator(model_client, game_state)
        
        # 调用历史记录（用于调试）
        self.call_history = []
    
    def process_user_input(self, user_input: str) -> str:
        """处理用户输入的完整流程"""
        try:
            # Layer 1: 意图分类
            intent_message = self.classify_intent(user_input)
            
            # Layer 2: 意图执行
            execution_message = self.execute_intent(intent_message)
            
            # Layer 3: 场景生成
            scene_response = self.generate_scene(execution_message)
            
            return scene_response
            
        except Exception as e:
            return f"处理请求时出错：{str(e)}"
    
    def classify_intent(self, user_input: str) -> IntentMessage:
        """Layer 1: 意图分类"""
        # 构建上下文
        context = self.context_manager.build_intent_context(user_input, self.game_state)
        
        # 获取Prompt
        prompt = self.prompt_template.get_intent_recognition_prompt(user_input, context)
        
        # 使用优化的Prompt调用AI模型
        ai_response = self.model_client._make_request(prompt, "意图分析")
        
        # 记录调用历史
        self.call_history.append({
            'layer': 'Intent Classification',
            'prompt': prompt,
            'response': ai_response,
            'timestamp': time.time()
        })
        
        
        # 解析AI响应
        try:
            intent_data = json.loads(ai_response.strip())
            intent = Intent(
                type=IntentType.EXECUTION,
                category=intent_data.get('category', '其他'),
                action=intent_data.get('description', user_input),
                target=intent_data.get('target', '')
            )
        except json.JSONDecodeError:
            # 解析失败时的fallback
            intent = Intent(
                type=IntentType.EXECUTION,
                category='其他',
                action=user_input,
                target='未知'
            )
        
        return IntentMessage(
            intent=intent,
            confidence=0.8,  # 简化实现，固定置信度
            raw_input=user_input,
            context=context,
            timestamp=time.time()
        )
    
    def execute_intent(self, intent_message: IntentMessage) -> ExecutionMessage:
        """Layer 2: 意图执行"""
        # 构建执行上下文
        context = self.context_manager.build_execution_context(
            intent_message.intent, self.game_state
        )
        
        # 执行意图
        execution_result = self.execution_engine.process(
            intent_message.intent, self.game_state
        )
        
        # 记录调用历史
        self.call_history.append({
            'layer': 'Intent Execution',
            'intent': intent_message.intent.to_dict(),
            'result': execution_result.to_dict(),
            'timestamp': time.time()
        })
        
        return ExecutionMessage(
            execution_result=execution_result,
            original_intent=intent_message.intent,
            game_state_snapshot={},  # 简化实现
            rag_context="",  # 暂不实现RAG
            timestamp=time.time()
        )
    
    def generate_scene(self, execution_message: ExecutionMessage) -> str:
        """Layer 3: 场景生成"""
        execution_result = execution_message.execution_result
        
        # 检查是否需要特殊处理
        if (execution_result.metadata.get("requires_ai_content") or 
            execution_message.original_intent.category in ["状态查询"]):
            scene_response = self._generate_dynamic_content_scene(execution_message)
        else:
            scene_response = self._generate_standard_scene(execution_message)
        
        # 记录调用历史
        self.call_history.append({
            'layer': 'Scene Generation',
            'execution_type': 'dynamic' if execution_result.metadata.get("requires_ai_content") else 'standard',
            'response': scene_response,
            'timestamp': time.time()
        })
        
        return scene_response
    
    def _generate_dynamic_content_scene(self, execution_message: ExecutionMessage) -> str:
        """生成包含动态内容的场景"""
        execution_result = execution_message.execution_result
        intent = execution_message.original_intent
        
        if intent.category == "搜索" and execution_result.success:
            # 使用AI生成搜索结果
            search_target = execution_result.metadata.get("search_target", "周围")
            search_context = f"玩家搜索检定结果：{execution_result.dice_results[0].total}"
            
            ai_result = self.content_generator.generate_search_result(
                location=self.game_state.world.current_location,
                search_context=search_context
            )
            
            # 更新执行结果
            if ai_result.get("success"):
                execution_result.action_taken = f"搜索{search_target}，{ai_result['narrative']}"
            
            return ai_result.get("narrative", "你进行了搜索，但什么也没找到。")
        
        elif intent.category == "对话" and execution_result.success:
            # 使用AI生成NPC对话
            dialogue_target = execution_result.metadata.get("dialogue_target", "")
            npc_type = execution_result.metadata.get("npc_type", "未知")
            context = f"玩家想要与{dialogue_target}（{npc_type}）进行对话"
            
            dialogue_response = self.content_generator.generate_npc_dialogue(
                npc_name=dialogue_target,
                context=context
            )
            
            return f"你走向{dialogue_target}开始对话。\n\n{dialogue_target}说：\"{dialogue_response}\""
        
        elif intent.category == "交易" and execution_result.success:
            # 使用AI生成交易场景
            trade_target = execution_result.metadata.get("trade_target", "")
            merchant_inventory_count = execution_result.metadata.get("merchant_inventory", 0)
            
            # 这里可以展开为更复杂的交易系统
            return f"你走向{trade_target}提出交易请求。\n\n{trade_target}微笑着说：\"欢迎来到我的店铺！我这里有{merchant_inventory_count}种商品。你想要看看什么？\""
        
        elif intent.category == "状态查询" and execution_result.success:
            # 直接显示状态信息
            status_display = execution_result.metadata.get("status_display", "状态信息获取失败")
            return f"你查看了自己的当前状态：\n{status_display}"
        
        # 其他类型的动态内容生成
        return self._generate_standard_scene(execution_message)
    
    def _generate_standard_scene(self, execution_message: ExecutionMessage) -> str:
        """生成标准场景描述"""
        
        # 获取Prompt
        prompt = self.prompt_template.get_scene_generation_prompt(execution_message)
        
        # 使用优化的Prompt调用AI模型生成场景
        return self.model_client._make_request(prompt, "场景生成")
    
    def get_call_history(self) -> List[Dict[str, Any]]:
        """获取调用历史（用于调试）"""
        return self.call_history.copy()
    
    def clear_history(self):
        """清空调用历史"""
        self.call_history.clear()
    
    def handle_error(self, error) -> str:
        """错误处理"""
        return f"抱歉，在{error.layer}层处理时出现错误：{error.message}"