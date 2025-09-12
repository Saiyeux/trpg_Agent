"""
文本生成系统测试模块

测试新的文本生成、响应解析和动态内容生成功能。
"""

import time
from typing import Dict, Any, List, Optional
from ..common.interactive_ui import InteractiveUI
from ..common.ai_setup import AIServiceChecker
from ..common.test_interface import TestModule

from Agent.ai.text_generator import TextGenerator, LMStudioConfig, create_text_generator
from Agent.ai.response_parser import ResponseParser, parse_ai_response
from Agent.implementations.content_generation_functions import create_content_orchestrator
from Agent.implementations.execution_engine import RealExecutionEngine
from Agent.interfaces.data_structures import Intent, ExecutionResult, StateChange


class TextGenerationTestModule(TestModule):
    """文本生成测试模块"""
    
    def __init__(self):
        self.name = "文本生成系统测试"
        self.description = "测试LM Studio文本生成、响应解析和动态内容生成"
        self.ui = InteractiveUI()
        self.ai_checker = AIServiceChecker()
        self.text_generator: Optional[TextGenerator] = None
        self.response_parser = ResponseParser()
        self.content_orchestrator = create_content_orchestrator()
        self.execution_engine = RealExecutionEngine()
    
    def run_tests(self) -> Dict[str, Any]:
        """运行所有文本生成相关测试"""
        results = {
            "start_time": time.time(),
            "tests": [],
            "summary": {}
        }
        
        try:
            # 1. 测试LM Studio连接
            self.ui.print_section("1. LM Studio连接测试")
            connection_result = self._test_lm_studio_connection()
            results["tests"].append({"name": "LM Studio连接", "result": connection_result})
            
            if not connection_result["success"]:
                self.ui.print_error("LM Studio连接失败，跳过后续测试")
                return results
            
            # 2. 测试基础文本生成
            self.ui.print_section("2. 基础文本生成测试")
            text_gen_result = self._test_basic_text_generation()
            results["tests"].append({"name": "基础文本生成", "result": text_gen_result})
            
            # 3. 测试响应解析
            self.ui.print_section("3. 响应解析测试")
            parsing_result = self._test_response_parsing()
            results["tests"].append({"name": "响应解析", "result": parsing_result})
            
            # 4. 测试动态内容生成
            self.ui.print_section("4. 动态内容生成测试")
            content_gen_result = self._test_dynamic_content_generation()
            results["tests"].append({"name": "动态内容生成", "result": content_gen_result})
            
            # 5. 完整流程测试
            self.ui.print_section("5. 完整流程测试")
            integration_result = self._test_full_integration()
            results["tests"].append({"name": "完整流程集成", "result": integration_result})
            
        except Exception as e:
            self.ui.print_error(f"测试过程中出现异常: {str(e)}")
            results["error"] = str(e)
        
        finally:
            results["end_time"] = time.time()
            results["duration"] = results["end_time"] - results["start_time"]
            
            # 生成测试摘要
            results["summary"] = self._generate_test_summary(results["tests"])
            self._display_test_summary(results["summary"])
        
        return results
    
    def _test_lm_studio_connection(self) -> Dict[str, Any]:
        """测试LM Studio连接"""
        result = {
            "success": False,
            "message": "",
            "details": {}
        }
        
        try:
            # 检查LM Studio服务
            self.ui.print_step("检查LM Studio服务状态...")
            lm_studio_status = self.ai_checker.check_lm_studio()
            
            if not lm_studio_status["available"]:
                result["message"] = "LM Studio服务不可用"
                result["details"] = lm_studio_status
                return result
            
            # 创建文本生成器
            self.ui.print_step("初始化文本生成器...")
            self.text_generator = create_text_generator("http://localhost:1234")
            
            # 测试连接
            available_models = self.text_generator.get_available_models()
            
            result["success"] = True
            result["message"] = f"成功连接LM Studio，可用模型: {len(available_models)}个"
            result["details"] = {
                "available_models": available_models,
                "current_model": self.text_generator._current_model
            }
            
            self.ui.print_success(result["message"])
            for model in available_models:
                self.ui.print_info(f"  - {model}")
            
        except Exception as e:
            result["message"] = f"LM Studio连接失败: {str(e)}"
            result["details"] = {"error": str(e)}
            self.ui.print_error(result["message"])
        
        return result
    
    def _test_basic_text_generation(self) -> Dict[str, Any]:
        """测试基础文本生成"""
        result = {
            "success": False,
            "message": "",
            "details": {}
        }
        
        if not self.text_generator:
            result["message"] = "文本生成器未初始化"
            return result
        
        try:
            # 创建测试执行结果
            test_execution_result = ExecutionResult(
                success=True,
                intent_category="攻击",
                target="森林哥布林",
                result_description="成功攻击了森林哥布林",
                state_changes=[]
            )
            
            # 创建测试状态变更
            test_state_changes = [
                StateChange(
                    target="forest_goblin",
                    property_name="hp",
                    old_value=30,
                    new_value=15,
                    change_reason="受到玩家攻击"
                )
            ]
            
            # 创建测试游戏上下文
            test_context = {
                "player_location": "幽暗森林",
                "player_hp": 100,
                "player_mp": 50
            }
            
            self.ui.print_step("生成测试文本...")
            text_response = self.text_generator.generate_response(
                test_execution_result, test_state_changes, test_context
            )
            
            if text_response.success:
                result["success"] = True
                result["message"] = "文本生成成功"
                result["details"] = {
                    "generated_text": text_response.content,
                    "has_potential_changes": text_response.has_potential_changes,
                    "metadata": text_response.metadata
                }
                
                self.ui.print_success("生成的文本内容:")
                self.ui.print_info(f'"{text_response.content}"')
                self.ui.print_info(f"包含潜在变更: {text_response.has_potential_changes}")
                
            else:
                result["message"] = f"文本生成失败: {text_response.error_message}"
                result["details"] = {"error": text_response.error_message}
        
        except Exception as e:
            result["message"] = f"测试异常: {str(e)}"
            result["details"] = {"error": str(e)}
        
        return result
    
    def _test_response_parsing(self) -> Dict[str, Any]:
        """测试响应解析"""
        result = {
            "success": False,
            "message": "",
            "details": {}
        }
        
        try:
            # 测试文本样例
            test_texts = [
                "你成功击败了哥布林，获得了一把锈剑和10枚金币。",
                "你来到了神秘森林深处，发现了一座古老的神庙。【新增内容：古老神庙】",
                "你施放火球术消耗了15点魔法值，造成了25点伤害。",
                "你遇见了一位神秘商人，他向你兜售各种奇异的商品。"
            ]
            
            self.ui.print_step("解析测试文本...")
            
            parsing_results = []
            for i, test_text in enumerate(test_texts, 1):
                self.ui.print_info(f"测试文本 {i}: {test_text}")
                
                state_changes, content_requests = parse_ai_response(test_text)
                
                parsing_result = {
                    "text": test_text,
                    "state_changes": [
                        {
                            "target": change.target,
                            "property": change.property_path,
                            "operation": change.operation.value,
                            "value": change.value,
                            "confidence": change.confidence
                        } for change in state_changes
                    ],
                    "content_requests": [
                        {
                            "type": req.content_type.value,
                            "name": req.name,
                            "confidence": req.confidence
                        } for req in content_requests
                    ]
                }
                
                parsing_results.append(parsing_result)
                
                if state_changes:
                    self.ui.print_success(f"  检测到 {len(state_changes)} 个状态变更")
                    for change in state_changes:
                        self.ui.print_info(f"    - {change.target}.{change.property_path}: {change.operation.value} {change.value}")
                
                if content_requests:
                    self.ui.print_success(f"  检测到 {len(content_requests)} 个内容生成请求")
                    for req in content_requests:
                        self.ui.print_info(f"    - {req.content_type.value}: {req.name}")
            
            result["success"] = True
            result["message"] = f"成功解析 {len(test_texts)} 个测试文本"
            result["details"] = {"parsing_results": parsing_results}
            
        except Exception as e:
            result["message"] = f"解析测试异常: {str(e)}"
            result["details"] = {"error": str(e)}
        
        return result
    
    def _test_dynamic_content_generation(self) -> Dict[str, Any]:
        """测试动态内容生成"""
        result = {
            "success": False,
            "message": "",
            "details": {}
        }
        
        try:
            from Agent.ai.response_parser import ContentGenerationRequest, ContentType
            from Agent.interfaces.state_interfaces import GameState
            
            # 创建测试游戏状态
            test_game_state = self._create_test_game_state()
            
            # 创建测试内容生成请求
            test_requests = [
                ContentGenerationRequest(
                    content_type=ContentType.LOCATION,
                    name="神秘古塔",
                    description="一座高耸入云的古老法师塔",
                    properties={"location_type": "dungeon"},
                    confidence=0.9,
                    source_text="发现了一座神秘古塔"
                ),
                ContentGenerationRequest(
                    content_type=ContentType.NPC,
                    name="古塔守卫",
                    description="守护古塔的神秘守卫",
                    properties={"personality": "hostile"},
                    confidence=0.8,
                    source_text="遇见了古塔守卫"
                ),
                ContentGenerationRequest(
                    content_type=ContentType.ITEM,
                    name="魔法水晶",
                    description="散发着神秘光芒的水晶",
                    properties={"item_type": "reagent"},
                    confidence=0.7,
                    source_text="获得了魔法水晶"
                )
            ]
            
            self.ui.print_step("执行动态内容生成...")
            
            generation_results = self.content_orchestrator.process_generation_requests(
                test_requests, test_game_state
            )
            
            success_count = sum(1 for r in generation_results if r.success)
            
            result["success"] = success_count > 0
            result["message"] = f"成功生成 {success_count}/{len(test_requests)} 个内容"
            result["details"] = {
                "generation_results": [
                    {
                        "success": r.success,
                        "action": r.action_taken,
                        "error": r.failure_reason if not r.success else None,
                        "additional_info": r.additional_info
                    } for r in generation_results
                ]
            }
            
            # 显示生成结果
            for i, (request, gen_result) in enumerate(zip(test_requests, generation_results)):
                if gen_result.success:
                    self.ui.print_success(f"✅ {request.content_type.value}: {request.name}")
                    if gen_result.additional_info:
                        for key, value in gen_result.additional_info.items():
                            self.ui.print_info(f"    {key}: {value}")
                else:
                    self.ui.print_error(f"❌ {request.content_type.value}: {gen_result.failure_reason}")
        
        except Exception as e:
            result["message"] = f"动态内容生成测试异常: {str(e)}"
            result["details"] = {"error": str(e)}
        
        return result
    
    def _test_full_integration(self) -> Dict[str, Any]:
        """测试完整集成流程"""
        result = {
            "success": False,
            "message": "",
            "details": {}
        }
        
        if not self.text_generator:
            result["message"] = "文本生成器未初始化"
            return result
        
        try:
            # 1. 模拟执行引擎处理
            self.ui.print_step("1. 执行引擎处理意图...")
            
            test_intent = Intent(
                category="攻击",
                action="攻击森林哥布林",
                target="森林哥布林"
            )
            
            # 获取测试游戏状态
            test_game_state = self._create_test_game_state()
            
            # 执行意图
            execution_result = self.execution_engine.process(test_intent, test_game_state)
            
            self.ui.print_info(f"执行结果: {execution_result.success}")
            if execution_result.success:
                self.ui.print_info(f"动作: {execution_result.action_taken}")
                self.ui.print_info(f"状态变更数: {len(execution_result.state_changes)}")
            
            # 2. 文本生成
            self.ui.print_step("2. 生成响应文本...")
            
            game_context = {
                "player_location": "幽暗森林",
                "player_hp": test_game_state.player_state.hp,
                "player_mp": test_game_state.player_state.mp
            }
            
            text_response = self.text_generator.generate_response(
                execution_result, execution_result.state_changes, game_context
            )
            
            if text_response.success:
                self.ui.print_success("生成文本:")
                self.ui.print_info(f'"{text_response.content}"')
                
                # 3. 解析响应
                self.ui.print_step("3. 解析响应文本...")
                
                state_changes, content_requests = parse_ai_response(text_response.content)
                
                self.ui.print_info(f"检测到状态变更: {len(state_changes)}")
                self.ui.print_info(f"检测到内容生成请求: {len(content_requests)}")
                
                # 4. 处理动态内容生成
                if content_requests:
                    self.ui.print_step("4. 处理动态内容生成...")
                    
                    generation_results = self.content_orchestrator.process_generation_requests(
                        content_requests, test_game_state
                    )
                    
                    success_count = sum(1 for r in generation_results if r.success)
                    self.ui.print_info(f"成功生成内容: {success_count}/{len(content_requests)}")
                
                result["success"] = True
                result["message"] = "完整流程测试成功"
                result["details"] = {
                    "execution_success": execution_result.success,
                    "text_generation_success": text_response.success,
                    "generated_text": text_response.content,
                    "parsed_changes": len(state_changes),
                    "parsed_requests": len(content_requests),
                    "content_generated": sum(1 for r in generation_results if r.success) if content_requests else 0
                }
            else:
                result["message"] = f"文本生成失败: {text_response.error_message}"
                
        except Exception as e:
            result["message"] = f"集成测试异常: {str(e)}"
            result["details"] = {"error": str(e)}
        
        return result
    
    def _create_test_game_state(self):
        """创建测试游戏状态"""
        # 简化的测试游戏状态
        class TestGameState:
            def __init__(self):
                self.player_state = TestPlayerState()
                self.world = TestWorld()
        
        class TestPlayerState:
            def __init__(self):
                self.hp = 100
                self.max_hp = 100
                self.mp = 50
                self.max_mp = 50
                self.location = "幽暗森林"
                self.inventory = []
        
        class TestWorld:
            def __init__(self):
                self.npcs = [TestNPC()]
        
        class TestNPC:
            def __init__(self):
                self.name = "森林哥布林"
                self.hp = 30
                self.alive = True
                self.type = "敌对"
        
        return TestGameState()
    
    def _generate_test_summary(self, tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成测试摘要"""
        total_tests = len(tests)
        passed_tests = sum(1 for test in tests if test["result"]["success"])
        failed_tests = total_tests - passed_tests
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "overall_success": failed_tests == 0
        }
    
    def _display_test_summary(self, summary: Dict[str, Any]):
        """显示测试摘要"""
        self.ui.print_section("测试摘要")
        self.ui.print_info(f"总测试数: {summary['total_tests']}")
        self.ui.print_info(f"通过测试: {summary['passed_tests']}")
        self.ui.print_info(f"失败测试: {summary['failed_tests']}")
        self.ui.print_info(f"成功率: {summary['success_rate']:.1f}%")
        
        if summary['overall_success']:
            self.ui.print_success("🎉 所有测试通过！")
        else:
            self.ui.print_error(f"❌ {summary['failed_tests']} 个测试失败")