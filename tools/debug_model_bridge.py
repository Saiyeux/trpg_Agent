#!/usr/bin/env python3
"""调试ModelBridge完整流程"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Agent.config.ai_config import detect_and_configure_ai, create_ai_client_from_config
from Agent.implementations.model_bridge import RealModelBridge
from Agent.implementations.execution_engine import RealExecutionEngine
from Agent.implementations.game_state import RealGameState

def debug_model_bridge():
    # 初始化
    ai_config = detect_and_configure_ai()
    if not ai_config:
        return
    
    model_client = create_ai_client_from_config(ai_config)
    execution_engine = RealExecutionEngine()
    game_state = RealGameState()
    model_bridge = RealModelBridge(model_client, execution_engine, game_state)
    
    user_input = "查看我的状态"
    print(f"调试完整流程: {user_input}")
    
    # 第1步：意图识别
    print("\n=== 步骤1: 意图识别 ===")
    intent_message = model_bridge.classify_intent(user_input)
    print(f"意图类别: {intent_message.intent.category}")
    print(f"意图目标: {intent_message.intent.target}")
    print(f"意图动作: {intent_message.intent.action}")
    
    # 第2步：意图执行
    print("\n=== 步骤2: 意图执行 ===")
    execution_message = model_bridge.execute_intent(intent_message)
    execution_result = execution_message.execution_result
    print(f"执行成功: {execution_result.success}")
    print(f"执行动作: {execution_result.action_taken}")
    print(f"失败原因: {execution_result.failure_reason}")
    print(f"元数据: {execution_result.metadata}")
    print(f"是否需要AI内容: {execution_result.metadata.get('requires_ai_content', False)}")
    
    # 第3步：场景生成
    print("\n=== 步骤3: 场景生成 ===")
    intent = execution_message.original_intent
    print(f"原始意图类别: {intent.category}")
    print(f"执行结果成功: {execution_result.success}")
    
    # 检查条件
    condition1 = intent.category == "状态查询"
    condition2 = execution_result.success
    print(f"条件检查 - 类别是状态查询: {condition1}")
    print(f"条件检查 - 执行成功: {condition2}")
    print(f"应该进入状态查询分支: {condition1 and condition2}")
    
    # 手动调用场景生成
    scene_response = model_bridge.generate_scene(execution_message)
    print(f"\n最终场景: {scene_response}")

if __name__ == "__main__":
    debug_model_bridge()