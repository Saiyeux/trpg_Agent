#!/usr/bin/env python3
"""
RAG功能测试脚本

测试LightRAG集成是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_rag_plugin():
    """测试RAG插件基本功能"""
    print("🧪 测试RAG插件功能...")
    
    try:
        # 测试导入
        from Agent.interfaces.memory_interface import ConversationTurn
        from Agent.plugins.simple_memory_plugin import SimpleMemoryPlugin
        print("✅ 记忆模块导入成功")
        
        # 测试存储路径创建
        test_path = "storage/test_session"
        if SimpleMemoryPlugin.initialize_storage(test_path):
            print("✅ 记忆存储初始化成功")
        else:
            print("❌ 记忆存储初始化失败")
            return False
        
        # 测试基本存储
        from datetime import datetime
        test_turn = ConversationTurn(
            user_input="你好，我想探索这个神秘的洞穴",
            ai_response="你看到一个阴暗的洞口，里面传来微弱的光芒...",
            turn=1,
            timestamp=datetime.now().isoformat(),
            scene="神秘洞穴入口",
            metadata={"player_name": "测试玩家"}
        )
        
        if SimpleMemoryPlugin.store_turn(test_path, test_turn):
            print("✅ 记忆数据存储成功")
        else:
            print("❌ 记忆数据存储失败")
            return False
        
        # 再存储一轮用于测试查询
        test_turn2 = ConversationTurn(
            user_input="我在洞穴里找到了什么宝藏吗？",
            ai_response="你在洞穴深处发现了一个闪闪发光的宝箱...",
            turn=2,
            timestamp=datetime.now().isoformat(),
            scene="洞穴深处",
            metadata={"player_name": "测试玩家"}
        )
        SimpleMemoryPlugin.store_turn(test_path, test_turn2)
        
        # 测试查询功能
        results = SimpleMemoryPlugin.query_relevant(test_path, "洞穴探索", limit=2)
        if results:
            print(f"✅ 记忆查询成功，找到 {len(results)} 个相关结果")
            for i, result in enumerate(results):
                print(f"   结果{i+1}: {result.content[:50]}... (相关度: {result.relevance:.2f})")
        else:
            print("⚠️  记忆查询无结果")
        
        # 测试上下文获取
        context = SimpleMemoryPlugin.get_recent_context(test_path, turns=2)
        print(f"✅ 上下文获取: {context[:100]}...")
        
        # 测试统计功能
        stats = SimpleMemoryPlugin.get_storage_stats(test_path)
        print(f"✅ 记忆统计: {stats}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("   请确保已安装 lightrag-hku: pip install lightrag-hku")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_config_integration():
    """测试配置集成"""
    print("\n🧪 测试配置集成...")
    
    try:
        from Agent.config.settings import ConfigManager
        
        config = ConfigManager()
        rag_config = config.get_rag_config()
        
        print(f"✅ RAG配置获取成功: {rag_config}")
        
        # 测试启用RAG
        config.set_rag_enabled(True)
        rag_config = config.get_rag_config()
        
        if rag_config.get('enabled'):
            print("✅ RAG启用成功")
        else:
            print("❌ RAG启用失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始RAG功能测试\n")
    
    # 测试基本插件功能
    if not test_rag_plugin():
        print("\n❌ RAG插件测试失败")
        return 1
    
    # 测试配置集成
    if not test_config_integration():
        print("\n❌ 配置集成测试失败")
        return 1
    
    print("\n✅ 所有RAG测试通过！")
    print("\n📋 接下来可以:")
    print("   1. 运行 python main.py config 启用RAG功能")
    print("   2. 运行 python main.py 开始带RAG的游戏")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)