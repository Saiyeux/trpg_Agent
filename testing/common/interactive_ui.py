"""
交互式用户界面工具

提供友好的命令行交互界面，支持测试引导和结果展示。
"""

import os
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass 
class TestModule:
    name: str
    display_name: str
    description: str
    guide_file: str
    enabled: bool = True

class InteractiveUI:
    """交互式用户界面"""
    
    def __init__(self):
        self.width = 60
    
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_header(self):
        """显示系统头部"""
        self.clear_screen()
        print("=" * self.width)
        print("🎮 TRPG Agent 交互式测试系统".center(self.width - 6))
        print("=" * self.width)
        print()
    
    def show_section_header(self, title: str):
        """显示章节头部"""
        print()
        print("─" * self.width)
        print(f"📋 {title}")
        print("─" * self.width)
    
    def show_main_menu(self, modules: List[TestModule]) -> int:
        """显示主菜单并返回用户选择"""
        print("请选择要测试的模块:")
        print()
        
        for i, module in enumerate(modules, 1):
            status = "✅" if module.enabled else "⚠️"
            print(f"  [{i}] {status} {module.display_name}")
            print(f"      {module.description}")
            print()
        
        print(f"  [0] 📚 查看历史测试报告")
        print(f"  [q] 🚪 退出系统")
        print()
        
        while True:
            try:
                choice = input("请输入选择: ").strip().lower()
                
                if choice in ['q', 'quit', 'exit', '退出']:
                    return -1
                
                choice_num = int(choice)
                if 0 <= choice_num <= len(modules):
                    return choice_num
                else:
                    self.show_error("选择超出范围，请重新输入")
            except ValueError:
                self.show_error("请输入有效的数字")
    
    def show_guide(self, guide_content: str):
        """显示测试指南"""
        print("📖 测试指南")
        print("=" * self.width)
        print(guide_content)
        print("=" * self.width)
        
        input("\n按回车继续...")
    
    def show_message(self, message: str):
        """显示普通消息"""
        print(f"💬 {message}")
    
    def show_success(self, message: str):
        """显示成功消息"""
        print(f"✅ {message}")
    
    def show_warning(self, message: str):
        """显示警告消息"""
        print(f"⚠️  {message}")
    
    def show_error(self, message: str):
        """显示错误消息"""
        print(f"❌ {message}")
    
    def show_result(self, title: str, result: Dict[str, Any]):
        """显示测试结果"""
        print(f"\n🎯 {title}:")
        for key, value in result.items():
            if key == 'success':
                icon = "✅" if value else "❌"
                print(f"  {icon} 执行状态: {'成功' if value else '失败'}")
            elif key == 'confidence':
                print(f"  📊 置信度: {value:.2f}")
            elif key == 'processing_time':
                print(f"  ⏱️  处理时间: {value:.2f}秒")
            else:
                print(f"  📝 {key}: {value}")
        print()
    
    def get_input(self, prompt: str) -> str:
        """获取用户输入"""
        return input(f"📝 {prompt}")
    
    def confirm(self, question: str) -> bool:
        """确认对话框"""
        while True:
            response = input(f"❓ {question} (y/n): ").strip().lower()
            if response in ['y', 'yes', '是', 'Y']:
                return True
            elif response in ['n', 'no', '否', 'N']:
                return False
            else:
                self.show_error("请输入 y/n")