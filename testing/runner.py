#!/usr/bin/env python3
"""
交互式测试执行器

引导用户完成TRPG Agent系统的各模块测试，记录日志并自动分析结果。
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from testing.common.logger import TestLogger
from testing.common.ai_setup import AISetupHelper
from testing.common.interactive_ui import InteractiveUI

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
        self.ui.show_message("测试游戏逻辑的执行正确性和状态管理")
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
            self.ui.show_message(f"\n--- 测试用例 #{test_count} ---")
            self.ui.show_message("⚙️ 执行引擎测试 - 开发中...")
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