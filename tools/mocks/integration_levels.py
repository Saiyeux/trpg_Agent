"""
集成测试级别定义

定义4个级别的渐进式集成测试，从全Mock到完全真实实现。
支持逐步替换组件，降低集成复杂度。
"""

from typing import Dict, Any, Type, List
from dataclasses import dataclass

from .mock_game_state import MockGameState
from .mock_execution_engine import MockExecutionEngine, MockFunctionRegistry
from .mock_model_bridge import MockModelBridge, MockContextManager


@dataclass
class IntegrationComponents:
    """集成测试组件集合"""
    game_state: Any
    execution_engine: Any
    function_registry: Any
    model_bridge: Any
    context_manager: Any
    description: str


class IntegrationLevel:
    """
    集成测试级别管理器
    
    提供4个级别的渐进式集成测试配置：
    Level 1: 全Mock - 验证接口兼容性
    Level 2: 真实ExecutionEngine - 验证执行逻辑  
    Level 3: 真实GameState - 验证状态管理
    Level 4: 全真实 - 端到端验证
    """
    
    @staticmethod
    def level_1_all_mocks() -> IntegrationComponents:
        """
        Level 1: 全部Mock
        
        用途: 验证接口兼容性，确保所有接口定义正确
        特点: 可预测结果，快速执行，无外部依赖
        """
        return IntegrationComponents(
            game_state=MockGameState(),
            execution_engine=MockExecutionEngine(),
            function_registry=MockFunctionRegistry(),
            model_bridge=MockModelBridge(),
            context_manager=MockContextManager(),
            description="Level 1: 全Mock集成 - 接口兼容性验证"
        )
    
    @staticmethod
    def level_2_real_execution() -> IntegrationComponents:
        """
        Level 2: 真实ExecutionEngine + Mock其他
        
        用途: 验证执行引擎逻辑，Function库功能
        特点: 真实执行逻辑，Mock状态和通信
        """
        # 这里会在Phase 1实现真实的ExecutionEngine后替换
        return IntegrationComponents(
            game_state=MockGameState(),
            execution_engine=MockExecutionEngine(),  # 待替换为RealExecutionEngine
            function_registry=MockFunctionRegistry(),  # 待替换为RealFunctionRegistry
            model_bridge=MockModelBridge(),
            context_manager=MockContextManager(),
            description="Level 2: 真实执行引擎 - 执行逻辑验证"
        )
    
    @staticmethod
    def level_3_real_state() -> IntegrationComponents:
        """
        Level 3: 真实ExecutionEngine + GameState + Mock其他
        
        用途: 验证状态管理和持久化
        特点: 真实执行和状态，Mock通信层
        """
        return IntegrationComponents(
            game_state=MockGameState(),  # 待替换为RealGameState
            execution_engine=MockExecutionEngine(),  # 待替换为RealExecutionEngine
            function_registry=MockFunctionRegistry(),  # 待替换为RealFunctionRegistry  
            model_bridge=MockModelBridge(),
            context_manager=MockContextManager(),
            description="Level 3: 真实状态管理 - 状态系统验证"
        )
    
    @staticmethod
    def level_4_full_integration() -> IntegrationComponents:
        """
        Level 4: 全部真实实现
        
        用途: 端到端集成测试
        特点: 完整系统测试，包含AI调用
        """
        return IntegrationComponents(
            game_state=MockGameState(),  # 待替换为RealGameState
            execution_engine=MockExecutionEngine(),  # 待替换为RealExecutionEngine
            function_registry=MockFunctionRegistry(),  # 待替换为RealFunctionRegistry
            model_bridge=MockModelBridge(),  # 待替换为RealModelBridge
            context_manager=MockContextManager(),  # 待替换为RealContextManager
            description="Level 4: 完全集成 - 端到端验证"
        )
    
    @staticmethod
    def get_all_levels() -> Dict[str, IntegrationComponents]:
        """获取所有集成级别"""
        return {
            "level_1": IntegrationLevel.level_1_all_mocks(),
            "level_2": IntegrationLevel.level_2_real_execution(),
            "level_3": IntegrationLevel.level_3_real_state(),
            "level_4": IntegrationLevel.level_4_full_integration()
        }
    
    @staticmethod
    def describe_levels() -> str:
        """获取所有级别的描述"""
        descriptions = []
        for level_name, components in IntegrationLevel.get_all_levels().items():
            descriptions.append(f"{level_name}: {components.description}")
        return "\n".join(descriptions)


class TestScenario:
    """
    测试场景定义
    
    定义标准的测试场景，用于各个集成级别的验证。
    """
    
    @staticmethod
    def attack_goblin_scenario() -> Dict[str, Any]:
        """攻击哥布林场景 - 用于垂直MVP测试"""
        return {
            "name": "攻击哥布林",
            "user_input": "我攻击哥布林",
            "expected_intent": {
                "type": "执行",
                "category": "攻击", 
                "target": "哥布林"
            },
            "setup": lambda state: state.setup_enemy("哥布林", hp=10, ac=12),
            "expected_changes": [
                {"target": "npc_哥布林", "property": "hp", "action": "modify"}
            ],
            "success_criteria": [
                "ExecutionResult.success == True",
                "哥布林HP减少",
                "场景生成包含具体伤害数值"
            ]
        }
    
    @staticmethod
    def search_desk_scenario() -> Dict[str, Any]:
        """搜索书桌场景 - 用于搜索功能测试"""
        return {
            "name": "搜索书桌",
            "user_input": "我搜索书桌",
            "expected_intent": {
                "type": "执行",
                "category": "搜索",
                "target": "书桌"
            },
            "setup": lambda state: None,  # 无需特殊设置
            "expected_changes": [
                {"target": "player", "property": "items", "action": "add"}
            ],
            "success_criteria": [
                "ExecutionResult.success == True",
                "找到具体物品",
                "场景生成给出明确结果而非氛围描述"
            ]
        }
    
    @staticmethod
    def get_all_scenarios() -> Dict[str, Dict[str, Any]]:
        """获取所有测试场景"""
        return {
            "attack_goblin": TestScenario.attack_goblin_scenario(),
            "search_desk": TestScenario.search_desk_scenario()
        }


class IntegrationTestRunner:
    """
    集成测试运行器
    
    执行指定级别和场景的集成测试。
    """
    
    def __init__(self, level: IntegrationComponents):
        self.components = level
        self.results: List[Dict[str, Any]] = []
    
    def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行单个测试场景
        
        Args:
            scenario: 测试场景配置
            
        Returns:
            Dict[str, Any]: 测试结果
        """
        result = {
            "scenario_name": scenario["name"],
            "success": False,
            "error": None,
            "details": {}
        }
        
        try:
            # 设置测试环境
            if scenario.get("setup"):
                scenario["setup"](self.components.game_state)
            
            # 运行测试流程
            # 1. 意图识别
            intent_msg = self.components.model_bridge.classify_intent(scenario["user_input"])
            result["details"]["intent"] = intent_msg.to_dict()
            
            # 2. 执行引擎处理
            execution_msg = self.components.model_bridge.execute_intent(intent_msg)
            result["details"]["execution"] = execution_msg.to_dict()
            
            # 3. 场景生成
            scene_text = self.components.model_bridge.generate_scene(execution_msg)
            result["details"]["scene"] = scene_text
            
            # 验证结果
            result["success"] = self._validate_result(scenario, result["details"])
            
        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
        
        self.results.append(result)
        return result
    
    def _validate_result(self, scenario: Dict[str, Any], details: Dict[str, Any]) -> bool:
        """验证测试结果是否符合预期"""
        # 简化的验证逻辑，主要检查是否有执行结果
        execution_result = details.get("execution", {}).get("execution_result", {})
        return execution_result.get("success", False)
    
    def run_all_scenarios(self) -> List[Dict[str, Any]]:
        """运行所有测试场景"""
        scenarios = TestScenario.get_all_scenarios()
        for scenario in scenarios.values():
            self.run_scenario(scenario)
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        return {
            "level": self.components.description,
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": passed / total if total > 0 else 0
        }