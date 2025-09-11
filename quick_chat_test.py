#!/usr/bin/env python3
"""
快速对话测试
验证真实AI集成的TRPG系统是否可以进行交互对话
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Agent.config.ai_config import detect_and_configure_ai, create_ai_client_from_config
from Agent.implementations.model_bridge import RealModelBridge
from Agent.implementations.execution_engine import RealExecutionEngine
from Agent.implementations.game_state import RealGameState


def main():
    print("🎮 TRPG AI对话系统启动中...")
    
    # 1. 检测AI服务
    ai_config = detect_and_configure_ai()
    if not ai_config:
        print("❌ 没有可用的AI服务")
        return
    
    print(f"✅ 使用AI服务: {ai_config.name}")
    
    # 2. 初始化系统
    model_client = create_ai_client_from_config(ai_config)
    execution_engine = RealExecutionEngine()
    game_state = RealGameState()
    
    model_bridge = RealModelBridge(
        model_client=model_client,
        execution_engine=execution_engine,
        game_state=game_state
    )
    
    print("✅ 系统初始化完成")
    print("\n" + "="*60)
    print("🌟 欢迎来到AI TRPG世界！")
    print("="*60)
    print("你现在在起始村庄，周围有哥布林和商人老约翰。")
    print("你可以尝试：")
    print("- 攻击哥布林")
    print("- 搜索周围")
    print("- 和商人对话")
    print("- 查看我的状态")
    print("\n输入 'quit' 或 'exit' 退出")
    print("="*60)
    
    # 3. 对话循环
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("\n👋 感谢游玩！再见！")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 AI正在思考...")
            response = model_bridge.process_user_input(user_input)
            print(f"\n城主: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 游戏被中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 出现错误: {e}")
            print("请重试...")


if __name__ == "__main__":
    main()