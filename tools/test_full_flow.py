#!/usr/bin/env python3
"""完整流程测试"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Agent.config.ai_config import detect_and_configure_ai, create_ai_client_from_config
from Agent.implementations.model_bridge import RealModelBridge
from Agent.implementations.execution_engine import RealExecutionEngine
from Agent.implementations.game_state import RealGameState

def test_full_flow():
    # 初始化
    ai_config = detect_and_configure_ai()
    if not ai_config:
        print("没有AI服务")
        return
    
    model_client = create_ai_client_from_config(ai_config)
    execution_engine = RealExecutionEngine()
    game_state = RealGameState()
    model_bridge = RealModelBridge(model_client, execution_engine, game_state)
    
    print("测试完整对话和交易流程:")
    
    # 测试对话
    print("\n=== 测试对话 ===")
    response = model_bridge.process_user_input("和商人对话")
    print("用户: 和商人对话")
    print(f"AI: {response}")
    
    # 检查是否包含攻击内容
    attack_words = ["攻击", "伤害", "生命值", "血量", "躲开", "命中"]
    has_attack = any(word in response for word in attack_words)
    print(f"包含攻击内容: {'是' if has_attack else '否'}")
    
    # 测试交易
    print("\n=== 测试交易 ===")
    response = model_bridge.process_user_input("购买商人的物品")
    print("用户: 购买商人的物品")
    print(f"AI: {response}")
    
    has_attack = any(word in response for word in attack_words)
    print(f"包含攻击内容: {'是' if has_attack else '否'}")
    
    # 测试状态查询
    print("\n=== 测试状态查询 ===")
    response = model_bridge.process_user_input("查看我的状态")
    print("用户: 查看我的状态")
    print(f"AI: {response}")
    
    has_attack = any(word in response for word in attack_words)
    print(f"包含攻击内容: {'是' if has_attack else '否'}")

if __name__ == "__main__":
    test_full_flow()