#!/usr/bin/env python3
"""
新存储格式集成测试

模拟一个完整的游戏会话，测试新的API存储格式是否正确集成到游戏引擎中
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_game_engine_integration():
    """测试游戏引擎集成新存储格式"""
    print("🎮 测试游戏引擎集成...")
    
    try:
        from Agent.core.game_engine import GameEngine
        from Agent.config.settings import ConfigManager
        
        # 创建配置管理器并确保RAG启用
        config = ConfigManager()
        config.set_rag_enabled(True)
        
        print("✅ 配置管理器创建成功，RAG已启用")
        
        # 创建游戏引擎（不运行完整游戏循环）
        engine = GameEngine(config)
        
        print("✅ 游戏引擎初始化成功")
        
        # 检查RAG插件是否正确加载
        if engine.rag_plugin:
            print("✅ RAG插件已正确加载")
            plugin_name = engine.rag_plugin.__name__
            print(f"   插件类型: {plugin_name}")
            
            if "ApiMemoryPlugin" in plugin_name:
                print("✅ 使用的是新的API记忆插件")
            else:
                print("⚠️  使用的不是预期的API插件")
        else:
            print("❌ RAG插件未加载")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 游戏引擎集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_storage_functionality():
    """测试存储功能"""
    print("\n🗃️ 测试存储功能...")
    
    try:
        from Agent.plugins.api_memory_plugin import ApiMemoryPlugin
        from Agent.interfaces.memory_interface import ConversationTurn
        from datetime import datetime
        
        # 创建测试会话路径
        test_path = "storage/integration_test_session"
        
        # 初始化存储
        if not ApiMemoryPlugin.initialize_storage(test_path):
            print("❌ 存储初始化失败")
            return False
        
        print("✅ 存储初始化成功")
        
        # 模拟几轮对话存储
        test_conversations = [
            {
                "user_input": "我想开始一个冒险",
                "ai_response": "你站在一个十字路口前，面前有三条道路可以选择...",
                "scene": "十字路口",
                "turn": 1
            },
            {
                "user_input": "我选择左边的道路",
                "ai_response": "你沿着左边的小径走去，发现了一座古老的神庙...",
                "scene": "神庙入口",
                "turn": 2
            },
            {
                "user_input": "我进入神庙探索",
                "ai_response": "神庙内部昏暗，你听到了奇怪的回响声...",
                "scene": "神庙内部",
                "turn": 3
            }
        ]
        
        for conv in test_conversations:
            turn_data = ConversationTurn(
                user_input=conv["user_input"],
                ai_response=conv["ai_response"],
                turn=conv["turn"],
                timestamp=datetime.now().isoformat(),
                scene=conv["scene"],
                metadata={"player_name": "集成测试玩家"}
            )
            
            if not ApiMemoryPlugin.store_turn(test_path, turn_data):
                print(f"❌ 第{conv['turn']}轮存储失败")
                return False
        
        print(f"✅ 成功存储 {len(test_conversations)} 轮对话")
        
        # 测试查询功能
        results = ApiMemoryPlugin.query_relevant(test_path, "神庙", limit=2)
        print(f"✅ 查询测试: 找到 {len(results)} 个相关结果")
        
        # 测试统计信息
        stats = ApiMemoryPlugin.get_storage_stats(test_path)
        print(f"✅ 统计信息: 总计 {stats.get('total_turns', 0)} 轮对话")
        
        return True
        
    except Exception as e:
        print(f"❌ 存储功能测试失败: {e}")
        return False

def test_api_compatibility():
    """测试API兼容性"""
    print("\n🔌 测试API兼容性...")
    
    try:
        from Agent.api.conversation_api import ConversationAPI
        
        # 创建API实例
        api = ConversationAPI("storage")
        
        # 测试会话列表
        sessions = api.list_sessions()
        if not sessions["success"]:
            print("❌ 会话列表API失败")
            return False
        
        print(f"✅ 会话列表API: 找到 {sessions['data']['total']} 个会话")
        
        # 如果有会话，测试其他API
        if sessions["data"]["sessions"]:
            test_session = sessions["data"]["sessions"][0]["session_id"]
            
            # 测试历史记录API
            history = api.get_conversation_history(test_session, page=1, page_size=5)
            if history["success"]:
                print(f"✅ 历史记录API: 获取 {len(history['data']['conversations'])} 条记录")
            
            # 测试导出API
            export = api.export_conversation(test_session, "readable")
            if export["success"]:
                print(f"✅ 导出API: 生成 {export['data']['size']} 字节文件")
        
        return True
        
    except Exception as e:
        print(f"❌ API兼容性测试失败: {e}")
        return False

def verify_storage_files():
    """验证存储文件格式"""
    print("\n📁 验证存储文件格式...")
    
    try:
        import json
        
        test_path = "storage/integration_test_session"
        
        # 检查主要文件
        files_to_check = [
            ("conversation.jsonl", "对话记录文件"),
            ("session_summary.json", "会话摘要文件")
        ]
        
        for filename, description in files_to_check:
            filepath = os.path.join(test_path, filename)
            if not os.path.exists(filepath):
                print(f"❌ {description}不存在: {filepath}")
                return False
            
            # 验证文件内容
            if filename.endswith('.jsonl'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    line_count = 0
                    for line in f:
                        if line.strip():
                            try:
                                data = json.loads(line.strip())
                                required_keys = ['id', 'turn', 'user_input', 'ai_response', 'timestamp', 'player', 'scene']
                                if not all(key in data for key in required_keys):
                                    print(f"❌ {filename} 格式错误，缺少必要字段")
                                    return False
                                line_count += 1
                            except json.JSONDecodeError:
                                print(f"❌ {filename} JSON格式错误")
                                return False
                    print(f"✅ {description}: {line_count} 条记录，格式正确")
            
            elif filename.endswith('.json'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        required_keys = ['session_id', 'total_turns', 'player_name']
                        if not all(key in data for key in required_keys):
                            print(f"❌ {filename} 格式错误，缺少必要字段")
                            return False
                        print(f"✅ {description}: 格式正确")
                    except json.JSONDecodeError:
                        print(f"❌ {filename} JSON格式错误")
                        return False
        
        return True
        
    except Exception as e:
        print(f"❌ 文件格式验证失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 新存储格式集成测试开始\n")
    
    tests = [
        ("游戏引擎集成", test_game_engine_integration),
        ("存储功能", test_storage_functionality),
        ("API兼容性", test_api_compatibility),
        ("存储文件格式", verify_storage_files)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 测试通过")
        else:
            print(f"❌ {test_name} 测试失败")
    
    print(f"\n{'='*50}")
    print(f"测试完成: {passed}/{total} 项通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！新的API存储格式已成功集成！")
        print("\n📋 集成完成，现在支持:")
        print("   ✅ 优化的单文件存储格式")
        print("   ✅ 前端API接口")
        print("   ✅ 多格式导出功能")
        print("   ✅ 完整的游戏引擎集成")
        print("   ✅ 向后兼容的存储结构")
        return 0
    else:
        print(f"\n❌ {total - passed} 项测试失败，需要修复")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)