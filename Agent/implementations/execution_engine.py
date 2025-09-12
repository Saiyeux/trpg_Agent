"""
真实的ExecutionEngine实现

基于接口定义实现真实的执行引擎，支持函数注册和动态执行。
"""

import time
import random
from typing import Dict, Any, List, Optional, Callable
from ..interfaces.execution_interfaces import (
    ExecutionEngine, GameFunction, FunctionRegistry, StateTransaction
)
from ..interfaces.data_structures import Intent, ExecutionResult, StateChange, DiceRoll
from ..interfaces.state_interfaces import GameState
from ..interfaces.state_management_interfaces import StateManagerRegistry
from .fillable_state_managers import (
    FillablePlayerStateManager, FillableNPCStateManager, FillableEnvironmentStateManager
)


class RealFunctionRegistry(FunctionRegistry):
    """真实的函数注册表实现"""
    
    def __init__(self):
        self._functions: Dict[str, GameFunction] = {}
        self._categories: Dict[str, List[str]] = {}
    
    def register(self, function: GameFunction) -> None:
        """注册游戏函数"""
        self._functions[function.name] = function
        
        # 按类别组织
        category = function.metadata.get('category', 'other')
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(function.name)
    
    def get_function(self, name: str) -> Optional[GameFunction]:
        """获取指定名称的函数"""
        return self._functions.get(name)
    
    def get_functions_by_category(self, category: str) -> List[GameFunction]:
        """获取指定类别的所有函数"""
        function_names = self._categories.get(category, [])
        return [self._functions[name] for name in function_names]
    
    def list_all_functions(self) -> List[GameFunction]:
        """列出所有注册的函数"""
        return list(self._functions.values())
    
    def find_functions_by_intent(self, intent: Intent) -> List[GameFunction]:
        """根据意图查找合适的函数"""
        # 基于意图类别匹配（使用中文分类）
        if intent.category == "攻击":
            return self.get_functions_by_category("攻击")
        elif intent.category == "搜索":
            return self.get_functions_by_category("搜索")
        elif intent.category == "对话":
            return self.get_functions_by_category("对话")
        elif intent.category == "交易":
            return self.get_functions_by_category("交易")
        elif intent.category == "移动":
            return self.get_functions_by_category("移动")
        elif intent.category == "状态查询":
            return self.get_functions_by_category("状态查询")
        elif intent.category == "交互":
            return self.get_functions_by_category("交互")
        elif intent.category == "技能":
            return self.get_functions_by_category("技能")
        else:
            return self.get_functions_by_category("其他")
    
    def get_all_functions(self) -> Dict[str, GameFunction]:
        """获取所有已注册的函数"""
        return self._functions.copy()
    
    def unregister(self, name: str) -> bool:
        """注销函数"""
        if name in self._functions:
            del self._functions[name]
            # 从分类中移除
            for category, function_names in self._categories.items():
                if name in function_names:
                    function_names.remove(name)
            return True
        return False


class RealStateTransaction(StateTransaction):
    """真实的状态事务实现"""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self._changes: List[StateChange] = []
        self._original_state = None
        self._committed = False
    
    def __enter__(self) -> 'RealStateTransaction':
        """开始事务"""
        # 保存原始状态（简化实现）
        world = getattr(self.game_state, 'world_state', self.game_state.world)
        npcs = world.npcs
        # 处理npcs可能是dict或list的情况
        if isinstance(npcs, dict):
            npcs = npcs.values()
        
        self._original_state = {
            'player_hp': self.game_state.player_state.hp,
            'npc_states': {npc.name: npc.hp for npc in npcs}
        }
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """结束事务"""
        if exc_type is not None and not self._committed:
            # 发生异常且未提交，回滚状态
            self.rollback()
    
    def add_change(self, change: StateChange) -> None:
        """添加状态变更"""
        self._changes.append(change)
        
        # 立即应用变更（简化实现）
        if change.target == "player" and change.property == "hp":
            self.game_state.player_state.hp = change.value
        else:
            # 假设是NPC
            npcs = getattr(self.game_state, 'world_state', self.game_state.world).npcs
            # 处理npcs可能是dict或list的情况
            if isinstance(npcs, dict):
                npcs = npcs.values()
            for npc in npcs:
                if npc.name == change.target and change.property == "hp":
                    npc.hp = change.value
    
    def commit(self) -> List[StateChange]:
        """提交事务"""
        self._committed = True
        return self._changes.copy()
    
    def rollback(self) -> None:
        """回滚事务"""
        if self._original_state:
            # 回滚玩家状态
            self.game_state.player_state.hp = self._original_state['player_hp']
            
            # 回滚NPC状态
            world = getattr(self.game_state, 'world_state', self.game_state.world)
            npcs = world.npcs
            # 处理npcs可能是dict或list的情况
            if isinstance(npcs, dict):
                npcs = npcs.values()
            
            for npc in npcs:
                if npc.name in self._original_state['npc_states']:
                    npc.hp = self._original_state['npc_states'][npc.name]
    
    def get_changes(self) -> List[StateChange]:
        """获取所有变更"""
        return self._changes.copy()
    
    def begin(self) -> None:
        """开始事务 - 兼容接口"""
        # 在__enter__中已经处理了开始逻辑
        pass


class AttackFunction(GameFunction):
    """攻击函数实现"""
    
    def __init__(self):
        self.name = "attack"
        self.description = "对目标进行攻击"
        self.metadata = {
            'category': '攻击',
            'requires_target': True,
            'can_fail': True
        }
    
    def can_execute(self, intent: Intent, game_state: 'GameState') -> bool:
        """检查是否可以执行攻击"""
        # 检查是否是攻击意图
        if intent.category != "攻击":
            return False
        
        # 检查是否有目标
        if not intent.target:
            return False
        
        # 检查目标是否存在
        target_name = intent.target
        npcs = getattr(game_state, 'world_state', game_state.world).npcs
        # 处理npcs可能是dict或list的情况
        if isinstance(npcs, dict):
            npcs = npcs.values()
        for npc in npcs:
            if target_name.lower() in npc.name.lower():
                return True
        
        return False
    
    def execute(self, intent: Intent, game_state: GameState, 
                transaction: StateTransaction) -> ExecutionResult:
        """执行攻击"""
        target_name = intent.target
        
        # 查找目标NPC
        target_npc = None
        world = getattr(game_state, 'world_state', game_state.world)
        npcs = world.npcs
        # 处理npcs可能是dict或list的情况
        if isinstance(npcs, dict):
            npcs = npcs.values()
        for npc in npcs:
            if target_name.lower() in npc.name.lower():
                target_npc = npc
                break
        
        if not target_npc:
            return ExecutionResult(
                success=False,
                action_taken=f"尝试攻击{target_name}",
                failure_reason=f"找不到目标：{target_name}",
                state_changes=[],
                dice_results=[]
            )
        
        # 检查目标是否已死亡
        if target_npc.hp <= 0:
            return ExecutionResult(
                success=False,
                action_taken=f"尝试攻击{target_npc.name}",
                failure_reason=f"{target_npc.name}已经被击败了",
                state_changes=[],
                dice_results=[]
            )
        
        # 执行攻击计算
        # 投骰子确定伤害
        damage_roll = DiceRoll(
            name="伤害骰",
            dice_type="1d6",
            result=random.randint(1, 6),
            modifier=2  # 基础攻击加成
        )
        
        total_damage = damage_roll.result + damage_roll.modifier
        new_hp = max(0, target_npc.hp - total_damage)
        
        # 记录状态变更
        hp_change = StateChange(
            target=target_npc.name,
            action="modify",
            property="hp",
            value=new_hp,
            old_value=target_npc.hp
        )
        
        # 应用变更
        transaction.add_change(hp_change)
        
        # 判断是否击败
        if new_hp <= 0:
            action_description = f"攻击{target_npc.name}造成{total_damage}点伤害，将其击败"
            result_description = f"你成功击败了{target_npc.name}！"
        else:
            action_description = f"攻击{target_npc.name}造成{total_damage}点伤害"
            result_description = f"你对{target_npc.name}造成了{total_damage}点伤害，它还剩{new_hp}点生命值"
        
        return ExecutionResult(
            success=True,
            action_taken=action_description,
            state_changes=[hp_change],
            dice_results=[damage_roll]
        )


class SearchFunction(GameFunction):
    """搜索函数实现"""
    
    def __init__(self):
        self.name = "search"
        self.description = "搜索指定目标或区域"
        self.metadata = {
            'category': '搜索',
            'requires_target': False,
            'can_fail': True
        }
    
    def can_execute(self, intent: Intent, game_state: 'GameState') -> bool:
        """检查是否可以执行搜索"""
        # 搜索功能比较通用，只要是搜索意图就可以执行
        return intent.category == "搜索"
    
    def execute(self, intent: Intent, game_state: GameState, 
                transaction: StateTransaction) -> ExecutionResult:
        """执行搜索"""
        target = intent.target or "周围环境"
        
        # 搜索检定
        search_roll = DiceRoll(
            name="搜索检定",
            dice_type="1d20",
            result=random.randint(1, 20),
            modifier=0
        )
        
        success = search_roll.result >= 10  # DC 10
        
        if success:
            return ExecutionResult(
                success=True,
                action_taken=f"搜索{target}成功",
                state_changes=[],
                dice_results=[search_roll],
                metadata={"requires_ai_content": True, "search_target": target}
            )
        else:
            return ExecutionResult(
                success=False,
                action_taken=f"搜索{target}失败",
                failure_reason=f"你仔细搜索了{target}，但没有发现任何有价值的东西",
                state_changes=[],
                dice_results=[search_roll]
            )


class DialogueFunction(GameFunction):
    """对话函数实现"""
    
    def __init__(self):
        self.name = "dialogue"
        self.description = "与NPC或其他角色对话"
        self.metadata = {
            'category': '对话',
            'requires_target': True,
            'can_fail': False
        }
    
    def can_execute(self, intent: Intent, game_state: 'GameState') -> bool:
        """检查是否可以执行对话"""
        if intent.category != "对话":
            return False
        
        # 检查是否有对话目标
        if not intent.target:
            return False
        
        # 检查目标NPC是否存在
        target_name = intent.target
        world = getattr(game_state, 'world_state', game_state.world)
        npcs = world.npcs
        if isinstance(npcs, dict):
            npcs = npcs.values()
        
        for npc in npcs:
            if target_name.lower() in npc.name.lower():
                return True
        
        return False
    
    def execute(self, intent: Intent, game_state: GameState, 
                transaction: StateTransaction) -> ExecutionResult:
        """执行对话"""
        target_name = intent.target
        
        # 查找目标NPC
        target_npc = None
        world = getattr(game_state, 'world_state', game_state.world)
        npcs = world.npcs
        if isinstance(npcs, dict):
            npcs = npcs.values()
        
        for npc in npcs:
            if target_name.lower() in npc.name.lower():
                target_npc = npc
                break
        
        if not target_npc:
            return ExecutionResult(
                success=False,
                action_taken=f"尝试与{target_name}对话",
                failure_reason=f"找不到{target_name}",
                state_changes=[],
                dice_results=[]
            )
        
        # 检查NPC是否存活且能对话
        if not target_npc.alive:
            return ExecutionResult(
                success=False,
                action_taken=f"尝试与{target_npc.name}对话",
                failure_reason=f"{target_npc.name}已经无法回应了",
                state_changes=[],
                dice_results=[]
            )
        
        # 成功对话
        return ExecutionResult(
            success=True,
            action_taken=f"与{target_npc.name}对话",
            state_changes=[],
            dice_results=[],
            metadata={"requires_ai_content": True, "dialogue_target": target_npc.name, "npc_type": target_npc.type}
        )


class TradeFunction(GameFunction):
    """交易函数实现"""
    
    def __init__(self):
        self.name = "trade"
        self.description = "与商人交易或购买物品"
        self.metadata = {
            'category': '交易',
            'requires_target': True,
            'can_fail': True
        }
    
    def can_execute(self, intent: Intent, game_state: 'GameState') -> bool:
        """检查是否可以执行交易"""
        if intent.category != "交易":
            return False
        
        # 检查是否有交易目标
        if not intent.target:
            return False
        
        # 检查目标商人是否存在
        target_name = intent.target
        world = getattr(game_state, 'world_state', game_state.world)
        npcs = world.npcs
        if isinstance(npcs, dict):
            npcs = npcs.values()
        
        for npc in npcs:
            if (target_name.lower() in npc.name.lower() and 
                npc.type in ["友好", "商人", "merchant"]):
                return True
        
        return False
    
    def execute(self, intent: Intent, game_state: GameState, 
                transaction: StateTransaction) -> ExecutionResult:
        """执行交易"""
        target_name = intent.target
        
        # 查找目标商人
        target_merchant = None
        world = getattr(game_state, 'world_state', game_state.world)
        npcs = world.npcs
        if isinstance(npcs, dict):
            npcs = npcs.values()
        
        for npc in npcs:
            if (target_name.lower() in npc.name.lower() and 
                npc.type in ["友好", "商人", "merchant"]):
                target_merchant = npc
                break
        
        if not target_merchant:
            return ExecutionResult(
                success=False,
                action_taken=f"尝试与{target_name}交易",
                failure_reason=f"找不到可交易的商人{target_name}",
                state_changes=[],
                dice_results=[]
            )
        
        # 成功开始交易
        return ExecutionResult(
            success=True,
            action_taken=f"与{target_merchant.name}进行交易",
            state_changes=[],
            dice_results=[],
            metadata={"requires_ai_content": True, "trade_target": target_merchant.name, "merchant_inventory": len(target_merchant.inventory)}
        )


class StatusFunction(GameFunction):
    """状态查询函数实现"""
    
    def __init__(self):
        self.name = "status"
        self.description = "查看玩家状态信息"
        self.metadata = {
            'category': '状态查询',
            'requires_target': False,
            'can_fail': False
        }
    
    def can_execute(self, intent: Intent, game_state: 'GameState') -> bool:
        """检查是否可以执行状态查询"""
        return intent.category == "状态查询"
    
    def execute(self, intent: Intent, game_state: GameState, 
                transaction: StateTransaction) -> ExecutionResult:
        """执行状态查询"""
        player = game_state.player_state
        
        status_info = {
            "hp": f"{player.hp}/{player.max_hp}",
            "mp": f"{player.mp}/{player.max_mp}",
            "location": player.location,
            "inventory_count": len(player.inventory),
            "level": getattr(player, 'level', 1),
            "gold": getattr(player, 'gold', 0)
        }
        
        status_text = f"生命值: {status_info['hp']}, 魔法值: {status_info['mp']}, 位置: {status_info['location']}, 背包: {status_info['inventory_count']}个物品, 金币: {status_info['gold']}"
        
        return ExecutionResult(
            success=True,
            action_taken="查看角色状态",
            state_changes=[],
            dice_results=[],
            additional_info=status_info,
            metadata={"status_display": status_text}
        )


class MovementFunction(GameFunction):
    """移动函数实现"""
    
    def __init__(self):
        self.name = "movement"
        self.description = "移动到指定地点或方向"
        self.metadata = {
            'category': '移动',
            'requires_target': True,
            'can_fail': True
        }
    
    def can_execute(self, intent: Intent, game_state: 'GameState') -> bool:
        """检查是否可以执行移动"""
        return intent.category == "移动"
    
    def execute(self, intent: Intent, game_state: GameState, 
                transaction: StateTransaction) -> ExecutionResult:
        """执行移动"""
        target = intent.target or "未指定方向"
        
        if intent.target in ["未指定", ""]:
            return ExecutionResult(
                success=False,
                action_taken=f"尝试移动",
                failure_reason="需要指定移动目标或方向",
                state_changes=[],
                dice_results=[]
            )
        
        # 简化的移动实现
        return ExecutionResult(
            success=True,
            action_taken=f"向{target}移动",
            state_changes=[],
            dice_results=[],
            metadata={"requires_ai_content": True, "movement_target": target}
        )


class InteractionFunction(GameFunction):
    """交互函数实现"""
    
    def __init__(self):
        self.name = "interaction"
        self.description = "与环境物体交互"
        self.metadata = {
            'category': '交互',
            'requires_target': False,
            'can_fail': True
        }
    
    def can_execute(self, intent: Intent, game_state: 'GameState') -> bool:
        """检查是否可以执行交互"""
        return intent.category == "交互"
    
    def execute(self, intent: Intent, game_state: GameState, 
                transaction: StateTransaction) -> ExecutionResult:
        """执行交互"""
        target = intent.target or "周围物体"
        
        # 交互检定
        interaction_roll = DiceRoll(
            name="交互检定",
            dice_type="1d20",
            result=random.randint(1, 20),
            modifier=0
        )
        
        success = interaction_roll.result >= 12  # DC 12
        
        if success:
            return ExecutionResult(
                success=True,
                action_taken=f"成功与{target}交互",
                state_changes=[],
                dice_results=[interaction_roll],
                metadata={"requires_ai_content": True, "interaction_target": target}
            )
        else:
            return ExecutionResult(
                success=False,
                action_taken=f"尝试与{target}交互",
                failure_reason=f"交互失败，{target}没有反应",
                state_changes=[],
                dice_results=[interaction_roll]
            )


class SkillFunction(GameFunction):
    """技能函数实现"""
    
    def __init__(self):
        self.name = "skill"
        self.description = "使用各种技能和法术"
        self.metadata = {
            'category': '技能',
            'requires_target': False,
            'can_fail': True
        }
    
    def can_execute(self, intent: Intent, game_state: 'GameState') -> bool:
        """检查是否可以执行技能"""
        return intent.category == "技能"
    
    def execute(self, intent: Intent, game_state: GameState, 
                transaction: StateTransaction) -> ExecutionResult:
        """执行技能"""
        skill_name = intent.action
        target = intent.target or "未指定"
        
        # 技能检定
        skill_roll = DiceRoll(
            name="技能检定",
            dice_type="1d20",
            result=random.randint(1, 20),
            modifier=2  # 基础技能加成
        )
        
        success = skill_roll.result >= 10  # DC 10
        
        if success:
            # 根据技能类型可能需要状态变更
            state_changes = []
            
            # 如果是治疗类技能，恢复生命值
            if any(word in skill_name.lower() for word in ["治疗", "恢复", "医疗"]):
                heal_amount = random.randint(1, 8) + 2
                new_hp = min(game_state.player_state.max_hp, 
                           game_state.player_state.hp + heal_amount)
                
                if new_hp > game_state.player_state.hp:
                    hp_change = StateChange(
                        target="player",
                        action="modify",
                        property="hp",
                        value=new_hp,
                        old_value=game_state.player_state.hp
                    )
                    transaction.add_change(hp_change)
                    state_changes = [hp_change]
            
            return ExecutionResult(
                success=True,
                action_taken=f"成功施放{skill_name}",
                state_changes=state_changes,
                dice_results=[skill_roll],
                metadata={
                    "requires_ai_content": True, 
                    "skill_name": skill_name,
                    "skill_target": target
                }
            )
        else:
            return ExecutionResult(
                success=False,
                action_taken=f"尝试施放{skill_name}",
                failure_reason=f"技能施放失败",
                state_changes=[],
                dice_results=[skill_roll]
            )


class RealExecutionEngine(ExecutionEngine):
    """真实的执行引擎实现"""
    
    def __init__(self, character_template: str = "战士"):
        self.registry = RealFunctionRegistry()
        self.execution_history: List[Dict[str, Any]] = []
        
        # 初始化状态管理器
        self.state_registry = StateManagerRegistry()
        self._init_state_managers(character_template)
        
        # 注册默认函数
        self._register_default_functions()
    
    def _init_state_managers(self, character_template: str):
        """初始化状态管理器"""
        # 创建状态管理器实例
        player_manager = FillablePlayerStateManager(character_template)
        npc_manager = FillableNPCStateManager()
        env_manager = FillableEnvironmentStateManager()
        
        # 注册到状态管理器注册表
        self.state_registry.register("player", player_manager)
        self.state_registry.register("npc", npc_manager)
        self.state_registry.register("environment", env_manager)
    
    def _register_default_functions(self):
        """注册默认的游戏函数"""
        self.registry.register(AttackFunction())
        self.registry.register(SearchFunction())
        self.registry.register(DialogueFunction())
        self.registry.register(TradeFunction())
        self.registry.register(StatusFunction())
        self.registry.register(MovementFunction())
        self.registry.register(InteractionFunction())
        self.registry.register(SkillFunction())
    
    def process(self, intent: Intent, game_state: GameState) -> ExecutionResult:
        """执行意图"""
        start_time = time.time()
        
        # 查找合适的函数
        functions = self.registry.find_functions_by_intent(intent)
        
        
        if not functions:
            # 没有找到合适的函数
            return ExecutionResult(
                success=False,
                action_taken="尝试执行动作",
                failure_reason=f"暂不支持'{intent.category}'类型的动作",
                state_changes=[],
                dice_results=[]
            )
        
        # 选择第一个匹配的函数（简化实现）
        function = functions[0]
        
        # 检查函数是否可以执行
        if not function.can_execute(intent, game_state):
            return ExecutionResult(
                success=False,
                action_taken="尝试执行动作",
                failure_reason=f"当前条件下无法执行'{intent.category}'动作",
                state_changes=[],
                dice_results=[]
            )
        
        # 使用事务执行
        try:
            with RealStateTransaction(game_state) as transaction:
                result = function.execute(intent, game_state, transaction)
                
                if result.success:
                    # 提交事务
                    committed_changes = transaction.commit()
                    # 更新结果中的状态变更
                    result.state_changes = committed_changes
                
                # 记录执行历史
                self.execution_history.append({
                    'intent': intent.to_dict(),
                    'function': function.name,
                    'result': result.to_dict(),
                    'execution_time': time.time() - start_time,
                    'timestamp': time.time()
                })
                
                return result
                
        except Exception as e:
            # 执行失败
            return ExecutionResult(
                success=False,
                action_taken="尝试执行动作",
                failure_reason=f"执行过程中出现错误：{str(e)}",
                state_changes=[],
                dice_results=[]
            )
    
    def register_function(self, function: GameFunction) -> None:
        """注册新的游戏函数"""
        self.registry.register(function)
    
    def get_available_functions(self, intent: Intent) -> List[GameFunction]:
        """获取可用的函数列表"""
        return self.registry.find_functions_by_intent(intent)
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history.copy()
    
    def get_supported_categories(self) -> List[str]:
        """获取支持的意图分类"""
        return ["攻击", "搜索", "对话", "交易", "移动", "状态查询", "交互", "技能", "其他"]
    
    def clear_history(self):
        """清空执行历史"""
        self.execution_history.clear()
    
    def get_state_registry(self) -> StateManagerRegistry:
        """获取状态管理器注册表"""
        return self.state_registry
    
    def get_player_manager(self) -> FillablePlayerStateManager:
        """获取玩家状态管理器"""
        return self.state_registry.get_manager("player")
    
    def get_npc_manager(self) -> FillableNPCStateManager:
        """获取NPC状态管理器"""
        return self.state_registry.get_manager("npc")
    
    def get_environment_manager(self) -> FillableEnvironmentStateManager:
        """获取环境状态管理器"""
        return self.state_registry.get_manager("environment")