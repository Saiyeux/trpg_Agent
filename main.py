#!/usr/bin/env python3
"""
AI-TRPG 主程序入口

基于大语言模型的桌游角色扮演游戏系统主程序。
支持交互式配置、游戏启动和调试模式。

使用方法:
    python main.py              # 启动游戏
    python main.py config       # 配置系统
    python main.py --debug      # 调试模式
    python main.py --help       # 显示帮助
"""

import sys
import os
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_trpg.core.game_engine import GameEngine
from ai_trpg.config.settings import ConfigManager


def setup_argument_parser() -> argparse.ArgumentParser:
    """设置命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="AI-TRPG: 基于大语言模型的桌游角色扮演游戏",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
    python main.py                    # 启动游戏
    python main.py config             # 配置系统  
    python main.py --debug            # 调试模式启动
    python main.py --validate-config  # 验证配置文件
    
更多信息请访问: https://github.com/your-repo/ai-trpg
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        choices=['config', 'play'],
        default='play',
        help='要执行的命令 (默认: play)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--config-file',
        type=str,
        default='config/game_config.json',
        help='指定配置文件路径 (默认: config/game_config.json)'
    )
    
    parser.add_argument(
        '--validate-config',
        action='store_true',
        help='验证配置文件并退出'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='AI-TRPG v1.0.0'
    )
    
    return parser


def print_banner():
    """打印程序横幅"""
    banner = """
╔══════════════════════════════════════════════════╗
║                   AI-TRPG                        ║
║          基于大语言模型的桌游角色扮演游戏        ║
║                                                  ║
║  🎭 智能场景生成  🤖 意图识别  📊 数据统计       ║
║  🔧 多AI后端支持  📝 详细日志  ⚙️  灵活配置       ║
╚══════════════════════════════════════════════════╝
"""
    print(banner)


def run_config_setup(config_file: str):
    """运行配置设置"""
    try:
        print("启动配置程序...")
        config_manager = ConfigManager(config_file)
        config_manager.interactive_setup()
    except KeyboardInterrupt:
        print("\n配置被中断")
    except Exception as e:
        print(f"配置过程中出错: {e}")
        sys.exit(1)


def validate_config(config_file: str):
    """验证配置文件"""
    try:
        config_manager = ConfigManager(config_file)
        errors = config_manager.validate_config()
        
        if errors:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        else:
            print("✅ 配置文件验证通过")
            config_manager.display_config()
            
    except Exception as e:
        print(f"❌ 验证配置时出错: {e}")
        sys.exit(1)


def run_game(config_file: str, debug_mode: bool = False):
    """运行游戏"""
    try:
        if debug_mode:
            print("🐛 调试模式已启用")
            import logging
            logging.basicConfig(level=logging.DEBUG)
            
        # 初始化配置管理器
        config_manager = ConfigManager(config_file)
        
        # 创建并启动游戏引擎
        print("初始化游戏引擎...")
        game_engine = GameEngine(config_manager)
        
        # 启动游戏
        game_engine.start_game()
        
    except KeyboardInterrupt:
        print("\n游戏被用户中断")
    except Exception as e:
        print(f"游戏运行出错: {e}")
        if debug_mode:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def check_requirements():
    """检查运行环境"""
    try:
        import requests
        print("✅ 依赖检查通过")
    except ImportError:
        print("❌ 缺少必要依赖，请运行: pip install requests")
        sys.exit(1)
        
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        sys.exit(1)


def create_default_directories():
    """创建默认目录结构"""
    directories = ['config', 'logs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        
    print("✅ 目录结构检查完成")


def main():
    """主函数"""
    # 设置命令行参数
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # 显示横幅
    if not args.validate_config:
        print_banner()
    
    # 检查运行环境
    check_requirements()
    create_default_directories()
    
    # 处理不同命令
    if args.validate_config:
        validate_config(args.config_file)
        return
        
    if args.command == 'config':
        run_config_setup(args.config_file)
    elif args.command == 'play':
        run_game(args.config_file, args.debug)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()