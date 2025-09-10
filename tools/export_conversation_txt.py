#!/usr/bin/env python3
"""
对话导出TXT工具

直接调用方法将存储的对话导出为TXT格式
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def list_available_sessions():
    """列出可用的对话会话"""
    from Agent.api.conversation_api import ConversationAPI
    
    api = ConversationAPI("storage")
    result = api.list_sessions()
    
    if result["success"] and result["data"]["sessions"]:
        print("📋 可用的对话会话:")
        for i, session in enumerate(result["data"]["sessions"], 1):
            print(f"  {i}. {session['session_id']}")
            print(f"     玩家: {session.get('player_name', '未知')}")
            print(f"     回合数: {session.get('total_turns', 0)}")
            print(f"     最后更新: {session.get('last_updated', '未知')[:19].replace('T', ' ')}")
            print()
        return result["data"]["sessions"]
    else:
        print("❌ 没有找到可用的对话会话")
        return []

def export_session_to_txt(session_id: str, format_type: str = "readable"):
    """导出指定会话为TXT格式"""
    from Agent.plugins.api_memory_plugin import ApiMemoryPlugin
    
    # 构建存储路径
    storage_path = f"storage/{session_id}"
    
    # 检查会话是否存在
    if not ApiMemoryPlugin.storage_exists(storage_path):
        print(f"❌ 会话 {session_id} 不存在")
        return None
    
    # 导出为TXT
    txt_content = ApiMemoryPlugin.export_to_txt(storage_path, format_type)
    
    return txt_content

def save_txt_to_file(content: str, session_id: str, format_type: str):
    """保存TXT内容到文件"""
    from Agent.plugins.api_memory_plugin import ApiMemoryPlugin
    
    # 获取会话信息用于文件命名
    storage_path = f"storage/{session_id}"
    stats = ApiMemoryPlugin.get_storage_stats(storage_path)
    
    player_name = stats.get("player_name", "player").replace(" ", "_")
    created_date = stats.get("created_at", "")[:10]
    
    # 生成文件名
    file_extension = "md" if format_type == "markdown" else "txt"
    filename = f"trpg_{player_name}_{created_date}_{session_id}.{file_extension}"
    
    # 保存文件
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filename

def main():
    """主函数 - 交互式导出"""
    print("🎮 TRPG对话记录导出工具\n")
    
    # 列出可用会话
    sessions = list_available_sessions()
    if not sessions:
        return
    
    # 选择会话
    try:
        choice = input("请选择要导出的会话编号: ").strip()
        session_index = int(choice) - 1
        
        if session_index < 0 or session_index >= len(sessions):
            print("❌ 无效的选择")
            return
            
        selected_session = sessions[session_index]
        session_id = selected_session["session_id"]
        
    except (ValueError, KeyboardInterrupt):
        print("❌ 操作已取消")
        return
    
    # 选择导出格式
    print("\n📝 选择导出格式:")
    print("1. readable - 易读格式 (推荐)")
    print("2. compact - 紧凑格式")  
    print("3. markdown - Markdown格式")
    
    format_choice = input("请选择格式 (默认: readable): ").strip() or "1"
    
    format_map = {
        "1": "readable",
        "2": "compact", 
        "3": "markdown"
    }
    
    format_type = format_map.get(format_choice, "readable")
    
    print(f"\n🔄 正在导出会话 {session_id} ({format_type}格式)...")
    
    # 导出内容
    content = export_session_to_txt(session_id, format_type)
    if not content:
        return
    
    # 显示预览
    print(f"\n📄 导出内容预览 (前200字符):")
    print("-" * 50)
    print(content[:200] + ("..." if len(content) > 200 else ""))
    print("-" * 50)
    
    # 询问是否保存到文件
    save_choice = input(f"\n💾 是否保存到文件? (y/n, 默认: y): ").strip().lower()
    
    if save_choice in ["", "y", "yes"]:
        filename = save_txt_to_file(content, session_id, format_type)
        print(f"✅ 已保存到: {filename}")
        print(f"📊 文件大小: {len(content.encode('utf-8'))} 字节")
    else:
        print("\n📋 完整导出内容:")
        print("=" * 50)
        print(content)
        print("=" * 50)

def quick_export(session_id: str, format_type: str = "readable", save_file: bool = True):
    """快速导出函数 - 可以在其他脚本中调用"""
    content = export_session_to_txt(session_id, format_type)
    if not content:
        return None
    
    if save_file:
        filename = save_txt_to_file(content, session_id, format_type)
        print(f"✅ {session_id} 已导出到: {filename}")
        return filename
    else:
        return content

# 使用示例
def usage_examples():
    """使用示例"""
    print("📚 使用示例:")
    print()
    
    print("1. 交互式导出:")
    print("   python export_conversation_txt.py")
    print()
    
    print("2. 在Python代码中调用:")
    print("   from export_conversation_txt import quick_export")
    print("   quick_export('integration_test_session', 'readable')")
    print()
    
    print("3. 直接调用API方法:")
    print("   from Agent.plugins.api_memory_plugin import ApiMemoryPlugin")
    print("   content = ApiMemoryPlugin.export_to_txt('storage/session_id', 'readable')")
    print("   print(content)")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        usage_examples()
    else:
        main()