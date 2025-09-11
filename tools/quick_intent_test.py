#!/usr/bin/env python3
"""快速意图识别测试"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Agent.config.ai_config import detect_and_configure_ai, create_ai_client_from_config
from Agent.implementations.model_bridge import RealModelBridge
from Agent.implementations.execution_engine import RealExecutionEngine
from Agent.implementations.game_state import RealGameState

def quick_test():
    # 初始化
    ai_config = detect_and_configure_ai()
    if not ai_config:
        return
    
    model_client = create_ai_client_from_config(ai_config)
    execution_engine = RealExecutionEngine()
    game_state = RealGameState()
    model_bridge = RealModelBridge(model_client, execution_engine, game_state)
    
    # 测试用例
    test_cases = [
        "和商人对话",
        "购买商人的物品", 
        "查看我的状态"
    ]
    
    print("快速意图识别测试:")
    for test_input in test_cases:
        intent_message = model_bridge.classify_intent(test_input)
        print(f"输入: {test_input}")
        print(f"类别: {intent_message.intent.category}")
        print(f"目标: {intent_message.intent.target}")
        print("---")

if __name__ == "__main__":
    quick_test()