#!/usr/bin/env python3
"""
API存储格式测试脚本

测试新的API导向存储格式和相关API功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_api_memory_plugin():
    """测试API记忆插件"""
    print("🧪 测试API记忆插件...")
    
    try:
        from Agent.interfaces.memory_interface import ConversationTurn
        from Agent.plugins.api_memory_plugin import ApiMemoryPlugin
        from datetime import datetime
        
        # 测试存储路径创建
        test_path = "storage/api_test_session"
        if ApiMemoryPlugin.initialize_storage(test_path):
            print("✅ API存储初始化成功")
        else:
            print("❌ API存储初始化失败")
            return False
        
        # 添加测试数据
        test_turns = [
            {
                "user_input": "你好，我想开始一个魔法冒险",
                "ai_response": "欢迎来到魔法世界！你站在一座古老的魔法塔前，塔顶闪烁着神秘的光芒...",
                "turn": 1,
                "scene": "魔法塔入口",
                "player": "法师艾莉"
            },
            {
                "user_input": "我想进入魔法塔探索",
                "ai_response": "你推开厚重的木门，里面传来古老魔法的气息。楼梯螺旋向上延伸...",
                "turn": 2,
                "scene": "魔法塔一层",
                "player": "法师艾莉"
            },
            {
                "user_input": "我在一层找找有什么魔法道具",
                "ai_response": "你在一个书架上发现了一本发光的法术书和一根水晶法杖...",
                "turn": 3,
                "scene": "魔法塔一层图书室",
                "player": "法师艾莉"
            }
        ]
        
        # 存储测试数据
        for turn_data in test_turns:
            conversation_turn = ConversationTurn(
                user_input=turn_data["user_input"],
                ai_response=turn_data["ai_response"],
                turn=turn_data["turn"],
                timestamp=datetime.now().isoformat(),
                scene=turn_data["scene"],
                metadata={"player_name": turn_data["player"]}
            )
            
            if not ApiMemoryPlugin.store_turn(test_path, conversation_turn):
                print(f"❌ 存储第{turn_data['turn']}轮失败")
                return False
        
        print(f"✅ 成功存储 {len(test_turns)} 轮对话")
        
        # 测试分页查询
        history_result = ApiMemoryPlugin.get_conversation_history(test_path, page=1, page_size=2)
        print(f"✅ 分页查询: 第1页显示 {len(history_result.get('conversations', []))} 条记录")
        
        # 测试搜索功能
        search_results = ApiMemoryPlugin.search_conversations(test_path, "魔法", limit=5)
        print(f"✅ 搜索功能: 找到 {len(search_results)} 个包含'魔法'的记录")
        
        # 测试TXT导出
        txt_content = ApiMemoryPlugin.export_to_txt(test_path, "readable")
        print(f"✅ TXT导出: 生成 {len(txt_content)} 字符的文本")
        print(f"   前100字符: {txt_content[:100]}...")
        
        # 测试统计信息
        stats = ApiMemoryPlugin.get_storage_stats(test_path)
        print(f"✅ 统计信息: 总计 {stats.get('total_turns', 0)} 轮对话")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_conversation_api():
    """测试对话API"""
    print("\n🧪 测试对话API...")
    
    try:
        from Agent.api.conversation_api import ConversationAPI
        
        # 使用之前创建的测试会话
        api = ConversationAPI("storage")
        
        # 测试会话列表
        sessions = api.list_sessions()
        if sessions["success"]:
            print(f"✅ 会话列表: 找到 {sessions['data']['total']} 个会话")
            
            if sessions["data"]["sessions"]:
                # 使用第一个会话进行测试
                test_session = sessions["data"]["sessions"][0]["session_id"]
                print(f"   使用会话: {test_session}")
                
                # 测试历史记录API
                history = api.get_conversation_history(test_session, page=1, page_size=5)
                if history["success"]:
                    print(f"✅ 历史记录API: 获取 {len(history['data']['conversations'])} 条记录")
                
                # 测试搜索API
                search = api.search_conversations(test_session, "魔法")
                if search["success"]:
                    print(f"✅ 搜索API: 找到 {search['data']['total']} 个匹配结果")
                
                # 测试导出API
                export = api.export_conversation(test_session, "readable")
                if export["success"]:
                    print(f"✅ 导出API: 生成 {export['data']['size']} 字节文件")
                    print(f"   文件名: {export['data']['filename']}")
                
                # 测试统计API
                stats = api.get_session_stats(test_session)
                if stats["success"]:
                    basic_info = stats["data"]["basic_info"]
                    statistics = stats["data"]["statistics"]
                    print(f"✅ 统计API: {basic_info.get('total_turns', 0)} 轮对话")
                    print(f"   平均回复长度: {statistics.get('avg_response_length', 0)} 字符")
                    print(f"   场景数量: {statistics.get('scenes_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def demo_export_formats():
    """演示不同导出格式"""
    print("\n🧪 演示导出格式...")
    
    try:
        from Agent.plugins.api_memory_plugin import ApiMemoryPlugin
        
        test_path = "storage/api_test_session"
        if not ApiMemoryPlugin.storage_exists(test_path):
            print("⚠️ 测试会话不存在，跳过导出演示")
            return True
        
        formats = ["readable", "compact", "markdown"]
        
        for fmt in formats:
            content = ApiMemoryPlugin.export_to_txt(test_path, fmt)
            print(f"\n--- {fmt.upper()} 格式 ---")
            print(content[:200] + "..." if len(content) > 200 else content)
        
        return True
        
    except Exception as e:
        print(f"❌ 导出演示失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始API存储格式测试\n")
    
    success_count = 0
    total_tests = 3
    
    # 测试API记忆插件
    if test_api_memory_plugin():
        success_count += 1
    
    # 测试对话API
    if test_conversation_api():
        success_count += 1
    
    # 演示导出格式
    if demo_export_formats():
        success_count += 1
    
    print(f"\n{'='*50}")
    print(f"测试完成: {success_count}/{total_tests} 项通过")
    
    if success_count == total_tests:
        print("✅ 所有测试通过！")
        print("\n📋 下一步:")
        print("   1. 替换游戏引擎中的记忆插件")
        print("   2. 集成到Web服务框架（Flask/FastAPI）")
        print("   3. 开发前端历史查看页面")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)