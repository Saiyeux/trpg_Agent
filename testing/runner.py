#!/usr/bin/env python3
"""
交互式测试执行器

引导用户完成TRPG Agent系统的各模块测试，记录日志并自动分析结果。
"""

import os
import sys
import time
import functools
import inspect
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from testing.common.logger import TestLogger
from testing.common.ai_setup import AISetupHelper
from testing.common.interactive_ui import InteractiveUI

@dataclass
class CallTrace:
    """函数调用跟踪记录"""
    function_name: str
    module_name: str
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    return_value: Any = None
    execution_time: float = 0.0
    timestamp: float = 0.0
    success: bool = True
    error: str = ""

class CallTracer:
    """函数调用跟踪器"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.call_stack: List[CallTrace] = []
        self.depth = 0
    
    def trace_calls(self, func: Callable) -> Callable:
        """装饰器：跟踪函数调用"""
        if not self.enabled:
            return func
            
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 开始跟踪
            trace = CallTrace(
                function_name=func.__name__,
                module_name=func.__module__,
                args=self._serialize_args(args),
                kwargs=self._serialize_kwargs(kwargs),
                timestamp=time.time()
            )
            
            self.depth += 1
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                trace.return_value = self._serialize_value(result)
                trace.success = True
                return result
            except Exception as e:
                trace.success = False
                trace.error = str(e)
                raise
            finally:
                trace.execution_time = time.time() - start_time
                self.call_stack.append(trace)
                self.depth -= 1
                
        return wrapper
    
    def _serialize_args(self, args) -> List[Any]:
        """序列化参数"""
        return [self._serialize_value(arg) for arg in args]
    
    def _serialize_kwargs(self, kwargs) -> Dict[str, Any]:
        """序列化关键字参数"""
        return {k: self._serialize_value(v) for k, v in kwargs.items()}
    
    def _serialize_value(self, value) -> Any:
        """序列化值"""
        if value is None:
            return None
        elif isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, (list, tuple)):
            return f"<{type(value).__name__}[{len(value)}]>"
        elif isinstance(value, dict):
            return f"<dict[{len(value)}]>"
        else:
            return f"<{type(value).__name__}>"
    
    def get_call_summary(self) -> List[Dict[str, Any]]:
        """获取调用摘要"""
        return [
            {
                "函数": f"{trace.module_name.split('.')[-1]}.{trace.function_name}",
                "参数": f"args={trace.args}, kwargs={trace.kwargs}",
                "返回": str(trace.return_value)[:100] + "..." if len(str(trace.return_value)) > 100 else str(trace.return_value),
                "耗时": f"{trace.execution_time:.3f}s",
                "状态": "✅" if trace.success else f"❌ {trace.error}"
            }
            for trace in self.call_stack
        ]
    
    def clear(self):
        """清空调用栈"""
        self.call_stack.clear()
        self.depth = 0

@dataclass
class TestModule:
    """测试模块定义"""
    name: str
    display_name: str
    description: str
    guide_file: str
    enabled: bool = True

class InteractiveTestRunner:
    """交互式测试执行器"""
    
    def __init__(self):
        self.ui = InteractiveUI()
        self.logger = TestLogger()
        self.ai_helper = AISetupHelper()
        self.call_tracer = CallTracer(enabled=True)
        
        # 定义可用的测试模块
        self.modules = [
            TestModule(
                name="intent_classification",
                display_name="意图识别系统",
                description="测试AI对用户输入的理解和分类能力",
                guide_file="intent_classification.md"
            ),
            TestModule(
                name="execution_engine", 
                display_name="执行引擎",
                description="测试游戏逻辑的执行正确性和状态管理",
                guide_file="execution_engine.md"
            ),
            TestModule(
                name="scene_generation",
                display_name="场景生成",
                description="测试AI场景描述的质量和一致性",
                guide_file="scene_generation.md"
            ),
            TestModule(
                name="dynamic_content",
                display_name="动态内容生成", 
                description="测试AI动态创建游戏内容的能力",
                guide_file="dynamic_content.md"
            ),
            TestModule(
                name="full_integration",
                display_name="完整集成测试",
                description="测试端到端完整流程的协调性",
                guide_file="full_integration.md"
            )
        ]
    
    def start(self):
        """启动交互式测试系统"""
        self.ui.show_header()
        
        while True:
            choice = self.ui.show_main_menu(self.modules)
            
            if choice == 0:
                self.show_historical_reports()
            elif choice == -1:
                self.ui.show_message("👋 感谢使用TRPG Agent测试系统！")
                break
            elif 1 <= choice <= len(self.modules):
                module = self.modules[choice - 1]
                if module.enabled:
                    self.run_module_test(module)
                else:
                    self.ui.show_error(f"模块 {module.display_name} 暂时不可用")
            else:
                self.ui.show_error("无效的选择，请重新输入")
    
    def run_module_test(self, module: TestModule):
        """运行指定模块的测试"""
        self.ui.show_section_header(f"🧪 {module.display_name} 测试")
        
        # 1. 检查AI服务可用性
        if not self.ai_helper.check_ai_availability():
            self.ui.show_error("❌ AI服务不可用，请检查配置")
            return
        
        # 2. 显示测试指南
        if not self.show_guide(module):
            return
        
        # 3. 确认用户准备就绪
        if not self.ui.confirm("准备开始测试？"):
            return
        
        # 4. 创建测试会话
        session = self.logger.create_session(module.name)
        self.ui.show_message(f"📊 测试会话创建: {session.session_id}")
        
        # 5. 执行测试
        try:
            self.execute_test_session(module, session)
        except KeyboardInterrupt:
            self.ui.show_warning("⚠️  测试被用户中断")
        except Exception as e:
            self.ui.show_error(f"❌ 测试执行错误: {str(e)}")
        finally:
            # 6. 结束会话并分析结果
            self.logger.end_session(session)
            self.analyze_session_results(module, session)
    
    def show_guide(self, module: TestModule) -> bool:
        """显示测试指南"""
        guide_path = Path(__file__).parent / "guides" / module.guide_file
        
        if not guide_path.exists():
            self.ui.show_warning(f"⚠️  指南文件不存在: {module.guide_file}")
            self.ui.show_message("将使用默认测试流程...")
            return True
        
        try:
            with open(guide_path, 'r', encoding='utf-8') as f:
                guide_content = f.read()
            
            self.ui.show_guide(guide_content)
            return True
            
        except Exception as e:
            self.ui.show_error(f"❌ 无法读取指南文件: {str(e)}")
            return False
    
    def execute_test_session(self, module: TestModule, session):
        """执行测试会话"""
        self.ui.show_message(f"🔄 开始 {module.display_name} 测试...")
        
        # 根据模块类型执行不同的测试逻辑
        if module.name == "intent_classification":
            self.run_intent_classification_test(session)
        elif module.name == "execution_engine":
            self.run_execution_engine_test(session)
        elif module.name == "scene_generation":
            self.run_scene_generation_test(session)
        elif module.name == "dynamic_content":
            self.run_dynamic_content_test(session)
        elif module.name == "full_integration":
            self.run_full_integration_test(session)
        else:
            self.ui.show_error(f"未知的测试模块: {module.name}")
    
    def run_intent_classification_test(self, session):
        """运行意图识别测试"""
        self.ui.show_message("🎯 意图识别测试")
        self.ui.show_message("连续测试模式 - 逐条输入测试用例，系统会立即分析并显示结果")
        self.ui.show_message("提示: 可以尝试攻击、对话、搜索、交易、状态查询等不同类型")
        print("快速测试示例:")
        print("  • 攻击: '我要攻击哥布林', '砍死那个敌人', '使用火球术'")
        print("  • 对话: '和村长对话', '询问任务', '打招呼'")
        print("  • 搜索: '搜索宝箱', '查找道具', '探索房间'")
        print("  • 状态: '查看状态', '显示背包', '我的血量'")
        print("  • 其他: '休息', '买装备', '学习技能'")
        self.ui.show_message("输入 'quit'、'exit'、'done' 或 '退出' 结束测试")
        print()
        
        test_count = 0
        
        while True:
            # 获取用户输入
            user_input = self.ui.get_input(f"测试输入 #{test_count + 1} (quit退出): ")
            
            # 检查退出条件
            if not user_input or user_input.lower() in ['done', '完成', 'quit', 'exit', '退出']:
                if test_count == 0:
                    self.ui.show_warning("⚠️  没有进行任何测试")
                else:
                    self.ui.show_success(f"✅ 完成 {test_count} 个测试用例")
                break
            
            if not user_input.strip():
                continue
            
            test_count += 1
            
            # 显示当前测试
            self.ui.show_message(f"\n--- 测试用例 #{test_count} ---")
            self.ui.show_message(f"输入: {user_input}")
            
            # 执行意图识别
            start_time = time.time()
            result = self._execute_intent_classification(user_input)
            execution_time = time.time() - start_time
            
            # 显示结果
            self.ui.show_result("意图识别结果", result)
            
            # 记录日志
            self.logger.log_test(
                session=session,
                test_case=f"意图识别_{test_count}",
                user_input=user_input,
                system_output=str(result),
                execution_time=execution_time,
                success=result.get('success', False),
                metadata=result
            )
            
            # 显示分隔线
            print("─" * 60)
            
        if test_count > 0:
            self.ui.show_message(f"\n🎯 本轮测试统计: 共 {test_count} 个用例")
    
    def run_execution_engine_test(self, session):
        """运行执行引擎测试"""
        self.ui.show_message("⚙️ 执行引擎测试")
        self.ui.show_message("连续测试模式 - 测试完整的意图→执行→结果流程")
        self.ui.show_message("支持所有类别：攻击、搜索、对话、交易、移动、状态查询、交互、技能")
        print("测试示例:")
        print("  • 攻击类: '攻击哥布林', '攻击' (无目标测试)")
        print("  • 搜索类: '搜索宝箱', '探索房间'")
        print("  • 技能类: '施放火球术', '治疗术' (测试状态变更)")
        print("  • 交互类: '撬锁', '开门'")
        print("  • 移动类: '去村庄', '向北走'")
        self.ui.show_message("输入 'quit'、'exit'、'done' 或 '退出' 结束测试")
        print()
        
        test_count = 0
        
        while True:
            user_input = self.ui.get_input(f"执行引擎测试 #{test_count + 1} (quit退出): ")
            
            if not user_input or user_input.lower() in ['done', '完成', 'quit', 'exit', '退出']:
                if test_count == 0:
                    self.ui.show_warning("⚠️  没有进行任何测试")
                else:
                    self.ui.show_success(f"✅ 完成 {test_count} 个测试用例")
                break
            
            if not user_input.strip():
                continue
            
            test_count += 1
            
            # 显示当前测试
            self.ui.show_message(f"\n--- 测试用例 #{test_count} ---")
            self.ui.show_message(f"输入: {user_input}")
            
            # 执行完整的意图→执行流程测试
            start_time = time.time()
            self.call_tracer.clear()  # 清空之前的调用栈
            result = self._execute_full_pipeline_test_with_tracing(user_input)
            execution_time = time.time() - start_time
            
            # 显示结果
            self.ui.show_result("执行引擎测试结果", result)
            
            # 显示调用栈
            call_summary = self.call_tracer.get_call_summary()
            if call_summary:
                print("\n📋 函数调用栈:")
                for i, call in enumerate(call_summary, 1):
                    print(f"  {i}. {call['函数']}")
                    print(f"     入参: {call['参数']}")
                    print(f"     出参: {call['返回']}")
                    print(f"     耗时: {call['耗时']} | {call['状态']}")
                    print()
            
            # 记录日志
            self.logger.log_test(
                session=session,
                test_case=f"执行引擎_{test_count}",
                user_input=user_input,
                system_output=str(result),
                execution_time=execution_time,
                success=result.get('success', False),
                metadata=result
            )
            
            # 显示分隔线
            print("─" * 60)
            
        if test_count > 0:
            self.ui.show_message(f"\n⚙️ 本轮测试统计: 共 {test_count} 个用例")
    
    def run_scene_generation_test(self, session):
        """运行场景生成测试"""
        self.ui.show_message("🎬 场景生成测试")
        self.ui.show_message("测试AI场景描述的质量和一致性")
        self.ui.show_message("输入 'quit'、'exit'、'done' 或 '退出' 结束测试")
        print()
        
        test_count = 0
        
        while True:
            user_input = self.ui.get_input(f"场景生成测试 #{test_count + 1} (quit退出): ")
            
            if not user_input or user_input.lower() in ['done', '完成', 'quit', 'exit', '退出']:
                if test_count == 0:
                    self.ui.show_warning("⚠️  没有进行任何测试")
                else:
                    self.ui.show_success(f"✅ 完成 {test_count} 个测试用例")
                break
            
            if not user_input.strip():
                continue
            
            test_count += 1
            self.ui.show_message(f"\n--- 测试用例 #{test_count} ---")
            self.ui.show_message("🎬 场景生成测试 - 开发中...")
            print("─" * 60)
        
        if test_count > 0:
            self.ui.show_message(f"\n🎬 本轮测试统计: 共 {test_count} 个用例")
    
    def run_dynamic_content_test(self, session):
        """运行动态内容测试"""
        self.ui.show_message("✨ 动态内容生成测试")
        self.ui.show_message("测试AI动态创建游戏内容的能力")
        self.ui.show_message("输入 'quit'、'exit'、'done' 或 '退出' 结束测试")
        print()
        
        test_count = 0
        
        while True:
            user_input = self.ui.get_input(f"动态内容测试 #{test_count + 1} (quit退出): ")
            
            if not user_input or user_input.lower() in ['done', '完成', 'quit', 'exit', '退出']:
                if test_count == 0:
                    self.ui.show_warning("⚠️  没有进行任何测试")
                else:
                    self.ui.show_success(f"✅ 完成 {test_count} 个测试用例")
                break
            
            if not user_input.strip():
                continue
            
            test_count += 1
            self.ui.show_message(f"\n--- 测试用例 #{test_count} ---")
            self.ui.show_message("✨ 动态内容测试 - 开发中...")
            print("─" * 60)
        
        if test_count > 0:
            self.ui.show_message(f"\n✨ 本轮测试统计: 共 {test_count} 个用例")
    
    def run_full_integration_test(self, session):
        """运行完整集成测试"""
        self.ui.show_message("🔗 完整集成测试")
        self.ui.show_message("测试端到端完整流程的协调性")
        self.ui.show_message("输入 'quit'、'exit'、'done' 或 '退出' 结束测试")
        print()
        
        test_count = 0
        
        while True:
            user_input = self.ui.get_input(f"完整集成测试 #{test_count + 1} (quit退出): ")
            
            if not user_input or user_input.lower() in ['done', '完成', 'quit', 'exit', '退出']:
                if test_count == 0:
                    self.ui.show_warning("⚠️  没有进行任何测试")
                else:
                    self.ui.show_success(f"✅ 完成 {test_count} 个测试用例")
                break
            
            if not user_input.strip():
                continue
            
            test_count += 1
            self.ui.show_message(f"\n--- 测试用例 #{test_count} ---")
            self.ui.show_message("🔗 完整集成测试 - 开发中...")
            print("─" * 60)
        
        if test_count > 0:
            self.ui.show_message(f"\n🔗 本轮测试统计: 共 {test_count} 个用例")
    
    def _execute_intent_classification(self, user_input: str) -> Dict[str, Any]:
        """执行真实的意图识别系统"""
        try:
            # 获取AI配置和客户端
            ai_config = self.ai_helper.get_ai_config()
            model_client = self.ai_helper.get_model_client()
            
            if not model_client:
                return {
                    "success": False,
                    "error": "AI客户端不可用",
                    "intent_category": "未知",
                    "target": "未知",
                    "confidence": 0.0
                }
            
            # 导入并初始化系统组件
            from Agent.implementations.model_bridge import RealModelBridge
            from Agent.implementations.execution_engine import RealExecutionEngine
            from Agent.implementations.game_state import RealGameState
            
            execution_engine = RealExecutionEngine()
            game_state = RealGameState()
            model_bridge = RealModelBridge(model_client, execution_engine, game_state)
            
            # 执行意图识别
            start_time = time.time()
            intent_message = model_bridge.classify_intent(user_input)
            processing_time = time.time() - start_time
            
            # 提取结果
            intent = intent_message.intent
            result = {
                "success": True,
                "intent_category": intent.category,
                "target": intent.target,
                "action": intent.action,
                "confidence": intent_message.confidence,
                "processing_time": processing_time,
                "raw_input": intent_message.raw_input,
                "timestamp": intent_message.timestamp
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "intent_category": "错误",
                "target": "未知",
                "confidence": 0.0,
                "processing_time": 0.0
            }
    
    def _execute_full_pipeline_test(self, user_input: str) -> Dict[str, Any]:
        """执行完整的意图→执行流程测试"""
        try:
            # Step 1: 意图识别
            intent_result = self._execute_intent_classification(user_input)
            if not intent_result.get('success'):
                return {
                    "success": False,
                    "执行阶段": "意图识别失败",
                    "error": f"意图识别失败: {intent_result.get('error')}",
                    "意图识别结果": intent_result
                }
            
            # Step 2: 创建Intent对象
            from Agent.interfaces.data_structures import Intent, IntentType
            intent = Intent(
                type=IntentType.EXECUTION,
                category=intent_result.get('intent_category', '其他'),
                action=intent_result.get('action', user_input),
                target=intent_result.get('target', '')
            )
            
            # Step 3: 创建执行引擎和游戏状态
            from Agent.implementations.execution_engine import RealExecutionEngine
            from Agent.implementations.game_state import RealGameState
            
            execution_engine = RealExecutionEngine()
            game_state = RealGameState()
            
            # Step 4: 执行意图
            execution_result = execution_engine.process(intent, game_state)
            
            # Step 5: 格式化结果
            result = {
                "success": True,
                "执行阶段": "完成",
                "意图类别": intent.category,
                "意图目标": intent.target,
                "意图动作": intent.action,
                "执行成功": "是" if execution_result.success else "否",
                "执行行动": execution_result.action_taken,
                "状态变更数": len(execution_result.state_changes),
                "骰子次数": len(execution_result.dice_results),
                "需要AI内容": "是" if (execution_result.metadata.get("requires_ai_content", False) if execution_result.metadata else False) else "否"
            }
            
            if not execution_result.success:
                result["失败原因"] = execution_result.failure_reason
            
            if execution_result.dice_results:
                result["骰子详情"] = [
                    f"{dice.name}: {dice.result}+{dice.modifier}={dice.total}"
                    for dice in execution_result.dice_results
                ]
            
            if execution_result.state_changes:
                result["状态变更详情"] = [
                    f"{change.target}.{change.property}: {change.old_value}→{change.value}"
                    for change in execution_result.state_changes
                ]
            
            return result
            
        except Exception as e:
            import traceback
            return {
                "success": False,
                "执行阶段": "执行引擎错误",
                "error": str(e),
                "错误详情": traceback.format_exc()
            }
    
    def _execute_full_pipeline_test_with_tracing(self, user_input: str) -> Dict[str, Any]:
        """执行完整的意图→执行流程测试（带调用跟踪）"""
        try:
            # Step 1: 意图识别（带跟踪）
            intent_result = self.call_tracer.trace_calls(self._execute_intent_classification)(user_input)
            if not intent_result.get('success'):
                return {
                    "success": False,
                    "执行阶段": "意图识别失败",
                    "error": f"意图识别失败: {intent_result.get('error')}",
                    "意图识别结果": intent_result
                }
            
            # Step 2: 创建Intent对象
            from Agent.interfaces.data_structures import Intent, IntentType
            intent = Intent(
                type=IntentType.EXECUTION,
                category=intent_result.get('intent_category', '其他'),
                action=intent_result.get('action', user_input),
                target=intent_result.get('target', '')
            )
            
            # Step 3: 创建执行引擎和游戏状态
            from Agent.implementations.execution_engine import RealExecutionEngine
            from Agent.implementations.game_state import RealGameState
            
            execution_engine = RealExecutionEngine()
            game_state = RealGameState()
            
            # 动态应用跟踪装饰器到执行引擎的关键方法
            execution_engine.process = self.call_tracer.trace_calls(execution_engine.process)
            
            # 查找并跟踪对应的Function
            functions = execution_engine.registry.find_functions_by_intent(intent)
            if functions:
                func = functions[0]
                func.execute = self.call_tracer.trace_calls(func.execute)
                func.can_execute = self.call_tracer.trace_calls(func.can_execute)
            
            # Step 4: 执行意图（现在会被跟踪）
            execution_result = execution_engine.process(intent, game_state)
            
            # Step 5: 格式化结果
            result = {
                "success": True,
                "执行阶段": "完成",
                "意图类别": intent.category,
                "意图目标": intent.target,
                "意图动作": intent.action,
                "执行成功": "是" if execution_result.success else "否",
                "执行行动": execution_result.action_taken,
                "状态变更数": len(execution_result.state_changes),
                "骰子次数": len(execution_result.dice_results),
                "需要AI内容": "是" if (execution_result.metadata.get("requires_ai_content", False) if execution_result.metadata else False) else "否"
            }
            
            if not execution_result.success:
                result["失败原因"] = execution_result.failure_reason
            
            if execution_result.dice_results:
                result["骰子详情"] = [
                    f"{dice.name}: {dice.result}+{dice.modifier}={dice.total}"
                    for dice in execution_result.dice_results
                ]
            
            if execution_result.state_changes:
                result["状态变更详情"] = [
                    f"{change.target}.{change.property}: {change.old_value}→{change.value}"
                    for change in execution_result.state_changes
                ]
            
            return result
            
        except Exception as e:
            import traceback
            return {
                "success": False,
                "执行阶段": "执行引擎错误",
                "error": str(e),
                "错误详情": traceback.format_exc()
            }
    
    def analyze_session_results(self, module: TestModule, session):
        """分析测试会话结果"""
        self.ui.show_section_header("📊 测试结果分析")
        
        # 基础统计
        total_tests = len(session.test_logs)
        success_count = sum(1 for log in session.test_logs if log.success)
        success_rate = success_count / total_tests if total_tests > 0 else 0
        
        avg_time = sum(log.execution_time for log in session.test_logs) / total_tests if total_tests > 0 else 0
        
        self.ui.show_message(f"测试总数: {total_tests}")
        self.ui.show_message(f"成功次数: {success_count}")
        self.ui.show_message(f"成功率: {success_rate:.1%}")
        self.ui.show_message(f"平均响应时间: {avg_time:.2f}秒")
        
        # 生成详细报告
        report_path = self.logger.generate_report(session)
        if report_path:
            self.ui.show_message(f"📄 详细报告已保存: {report_path}")
    
    def show_historical_reports(self):
        """显示历史测试报告"""
        self.ui.show_section_header("📚 历史测试报告")
        
        logs_dir = Path(__file__).parent / "logs"
        if not logs_dir.exists():
            self.ui.show_message("暂无历史测试记录")
            return
        
        # 列出最近的测试会话
        sessions = sorted([d for d in logs_dir.iterdir() if d.is_dir()], reverse=True)[:10]
        
        if not sessions:
            self.ui.show_message("暂无历史测试记录")
            return
        
        self.ui.show_message("最近10次测试会话:")
        for i, session_dir in enumerate(sessions, 1):
            self.ui.show_message(f"{i}. {session_dir.name}")
        
        # 可以添加查看具体报告的功能

def main():
    """主入口"""
    try:
        runner = InteractiveTestRunner()
        runner.start()
    except KeyboardInterrupt:
        print("\n\n👋 测试系统已退出")
    except Exception as e:
        print(f"\n❌ 系统错误: {str(e)}")

if __name__ == "__main__":
    main()