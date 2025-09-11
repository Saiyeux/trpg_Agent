#!/usr/bin/env python3
"""调试状态查询问题"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Agent.config.ai_config import detect_and_configure_ai, create_ai_client_from_config
from Agent.implementations.model_bridge import RealModelBridge
from Agent.implementations.execution_engine import RealExecutionEngine
from Agent.implementations.game_state import RealGameState

def debug_status():
    # 初始化
    ai_config = detect_and_configure_ai()
    if not ai_config:
        return
    
    model_client = create_ai_client_from_config(ai_config)
    execution_engine = RealExecutionEngine()
    game_state = RealGameState()
    model_bridge = RealModelBridge(model_client, execution_engine, game_state)
    
    print("调试状态查询:")
    
    # 测试意图识别
    intent_message = model_bridge.classify_intent("查看我的状态")
    print(f"意图类别: {intent_message.intent.category}")
    print(f"意图目标: {intent_message.intent.target}")
    
    # 测试执行引擎
    execution_result = execution_engine.process(intent_message.intent, game_state)
    print(f"执行成功: {execution_result.success}")
    print(f"执行动作: {execution_result.action_taken}")
    print(f"失败原因: {execution_result.failure_reason}")
    print(f"元数据: {execution_result.metadata}")
    
    # 检查支持的功能
    supported = execution_engine.get_supported_categories()
    print(f"支持的类别: {supported}")
    
    # 检查查找到的函数
    functions = execution_engine.registry.find_functions_by_intent(intent_message.intent)
    print(f"找到的函数数量: {len(functions)}")
    for func in functions:
        print(f"  函数: {func.name} - {func.description}")

if __name__ == "__main__":
    debug_status()