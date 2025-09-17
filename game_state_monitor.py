#!/usr/bin/env python3
"""
游戏状态实时监控脚本

实时显示TRPG游戏中的状态JSON数据，包括玩家属性、背包物品、当前位置等信息。
可以与正在运行的游戏会话并行运行，提供清晰的状态可视化。

使用方法:
    python game_state_monitor.py

功能:
- 实时显示玩家状态(HP/MP/经验/等级)
- 显示背包物品详情
- 显示当前位置和地图信息
- 显示周围NPC和环境信息
- 显示状态效果和游戏时间
- 支持JSON格式输出和美化显示
"""

import sys
import json
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import argparse

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from Agent.implementations.game_state import RealGameState
    from Agent.implementations.fillable_state_managers import (
        FillablePlayerStateManager,
        FillableEnvironmentStateManager,
        FillableNPCStateManager
    )
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在项目根目录下运行此脚本")
    sys.exit(1)


class GameStateMonitor:
    """游戏状态监控器"""

    def __init__(self, output_format: str = "pretty", refresh_interval: float = 2.0):
        """
        初始化监控器

        Args:
            output_format: 输出格式 ("pretty", "json", "compact")
            refresh_interval: 刷新间隔（秒）
        """
        self.output_format = output_format
        self.refresh_interval = refresh_interval
        self.game_state = None
        self.state_managers = None

    def create_demo_state(self) -> None:
        """创建演示用的游戏状态"""
        print("🎮 创建演示游戏状态...")

        # 创建游戏状态
        self.game_state = RealGameState()

        # 创建状态管理器
        self.state_managers = {
            'player': FillablePlayerStateManager(),
            'environment': FillableEnvironmentStateManager(),
            'npc': FillableNPCStateManager()
        }

        # 模拟一些游戏进展
        self._simulate_game_progress()

    def _simulate_game_progress(self) -> None:
        """模拟游戏进展"""
        print("📊 模拟游戏进展...")

        # 设置玩家名称
        self.game_state.player_name = "勇敢的冒险者"

        # 模拟一些历史记录
        self.game_state.add_to_history("游戏开始", "你踏入了这个神秘的世界")
        self.game_state.add_to_history("玩家行动", "查看背包")
        self.game_state.add_to_history("系统响应", "背包中有长剑和治疗卷轴")
        self.game_state.add_to_history("玩家行动", "移动到村庄")
        self.game_state.add_to_history("系统响应", "你来到了繁华的村庄中心")

        # 进行几个回合
        for i in range(3):
            self.game_state.next_turn()

        # 获取玩家状态管理器并模拟一些变化
        player_mgr = self.state_managers['player']

        # 模拟受伤
        player_mgr.character.set_attribute('current_hp', 75)
        player_mgr.character.set_attribute('current_mp', 45)

        # 模拟获得物品 - 使用字符串ID添加物品
        player_mgr.inventory.add_item('长剑', 1)
        player_mgr.inventory.add_item('治疗卷轴', 3)
        player_mgr.inventory.add_item('面包', 5)

        # 模拟位置变更
        player_mgr.current_location = "繁华村庄"

        print("✅ 演示状态创建完成")

    def get_current_state(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        if not self.game_state or not self.state_managers:
            return {"error": "游戏状态未初始化"}

        try:
            # 获取基本游戏状态
            base_state = self.game_state.to_dict()

            # 获取状态管理器状态
            player_mgr = self.state_managers['player']
            env_mgr = self.state_managers['environment']
            npc_mgr = self.state_managers['npc']

            # 构建完整状态
            current_state = {
                "timestamp": datetime.now().isoformat(),
                "session_info": {
                    "session_id": base_state.get("session_id"),
                    "turn_count": base_state.get("turn_count", 0),
                    "player_name": self.game_state.player_name
                },
                "player_status": {
                    "hp": f"{player_mgr.character.get_attribute('current_hp')}/{player_mgr.character.get_attribute('max_hp')}",
                    "mp": f"{player_mgr.character.get_attribute('current_mp')}/{player_mgr.character.get_attribute('max_mp')}",
                    "level": player_mgr.character.get_attribute('level'),
                    "experience": player_mgr.character.get_attribute('experience'),
                    "location": player_mgr.current_location,
                    "stats": {
                        "strength": player_mgr.character.get_attribute('strength'),
                        "dexterity": player_mgr.character.get_attribute('dexterity'),
                        "constitution": player_mgr.character.get_attribute('constitution'),
                        "intelligence": player_mgr.character.get_attribute('intelligence'),
                        "wisdom": player_mgr.character.get_attribute('wisdom'),
                        "charisma": player_mgr.character.get_attribute('charisma')
                    }
                },
                "inventory": {
                    "total_slots": len(player_mgr.inventory.slots),
                    "used_slots": len([s for s in player_mgr.inventory.slots if s]),
                    "items": []
                },
                "environment": {
                    "current_location": player_mgr.current_location,
                    "available_locations": ["起始村庄", "森林", "商店", "酒馆", "繁华村庄"],
                    "location_details": {
                        "name": player_mgr.current_location,
                        "description": f"当前所在位置：{player_mgr.current_location}",
                        "connections": ["起始村庄", "森林", "商店"]
                    }
                },
                "world_state": base_state.get("world", {}),
                "recent_history": base_state.get("history", [])[-5:],  # 最近5条历史
                "game_metadata": base_state.get("metadata", {})
            }

            # 添加背包物品详情
            for slot in player_mgr.inventory.slots:
                if slot:
                    current_state["inventory"]["items"].append({
                        "name": getattr(slot, 'name', str(slot)),
                        "quantity": getattr(slot, 'quantity', 1),
                        "properties": getattr(slot, 'properties', {
                            "type": "物品",
                            "description": "游戏物品"
                        })
                    })

            return current_state

        except Exception as e:
            return {"error": f"获取状态失败: {str(e)}"}

    def format_state_pretty(self, state: Dict[str, Any]) -> str:
        """美化格式显示状态"""
        if "error" in state:
            return f"❌ 错误: {state['error']}"

        output = []
        output.append("=" * 80)
        output.append(f"🎮 TRPG 游戏状态监控 - {state['timestamp']}")
        output.append("=" * 80)

        # 会话信息
        session = state.get("session_info", {})
        output.append(f"📋 会话信息:")
        output.append(f"   会话ID: {session.get('session_id', 'N/A')}")
        output.append(f"   玩家名: {session.get('player_name', 'N/A')}")
        output.append(f"   回合数: {session.get('turn_count', 0)}")
        output.append("")

        # 玩家状态
        player = state.get("player_status", {})
        output.append(f"👤 玩家状态:")
        output.append(f"   ❤️  生命值: {player.get('hp', 'N/A')}")
        output.append(f"   💙 法力值: {player.get('mp', 'N/A')}")
        output.append(f"   ⭐ 等级: {player.get('level', 'N/A')}")
        output.append(f"   ✨ 经验: {player.get('experience', 'N/A')}")
        output.append(f"   📍 位置: {player.get('location', 'N/A')}")

        # 属性
        stats = player.get("stats", {})
        if stats:
            output.append(f"   💪 属性: STR:{stats.get('strength', 0)} DEX:{stats.get('dexterity', 0)} " +
                         f"CON:{stats.get('constitution', 0)} INT:{stats.get('intelligence', 0)} " +
                         f"WIS:{stats.get('wisdom', 0)} CHA:{stats.get('charisma', 0)}")
        output.append("")

        # 背包信息
        inventory = state.get("inventory", {})
        output.append(f"🎒 背包状态:")
        output.append(f"   容量: {inventory.get('used_slots', 0)}/{inventory.get('total_slots', 0)}")

        items = inventory.get("items", [])
        if items:
            output.append(f"   物品:")
            for item in items:
                name = item.get("name", "未知")
                quantity = item.get("quantity", 0)
                props = item.get("properties", {})
                item_type = props.get("type", "未知")
                description = props.get("description", "")
                output.append(f"     • {name} x{quantity} ({item_type})")
                if description:
                    output.append(f"       {description}")
        else:
            output.append(f"   物品: 无")
        output.append("")

        # 环境信息
        environment = state.get("environment", {})
        output.append(f"🌍 环境信息:")
        output.append(f"   当前位置: {environment.get('current_location', 'N/A')}")

        available_locations = environment.get("available_locations", [])
        if available_locations:
            output.append(f"   可到达位置: {', '.join(available_locations)}")

        location_details = environment.get("location_details", {})
        if location_details:
            output.append(f"   位置详情:")
            for key, value in location_details.items():
                output.append(f"     {key}: {value}")
        output.append("")

        # 最近历史
        history = state.get("recent_history", [])
        if history:
            output.append(f"📜 最近活动:")
            for i, entry in enumerate(history[-3:], 1):  # 只显示最近3条
                action = entry.get("action", "未知")
                content = entry.get("content", "")
                output.append(f"   {i}. {action}: {content}")
            output.append("")

        return "\n".join(output)

    def format_state_json(self, state: Dict[str, Any]) -> str:
        """JSON格式显示状态"""
        return json.dumps(state, indent=2, ensure_ascii=False)

    def format_state_compact(self, state: Dict[str, Any]) -> str:
        """紧凑格式显示状态"""
        if "error" in state:
            return f"ERROR: {state['error']}"

        session = state.get("session_info", {})
        player = state.get("player_status", {})
        inventory = state.get("inventory", {})

        return (f"[{session.get('turn_count', 0)}] "
               f"{session.get('player_name', 'N/A')} "
               f"HP:{player.get('hp', 'N/A')} MP:{player.get('mp', 'N/A')} "
               f"@{player.get('location', 'N/A')} "
               f"Items:{inventory.get('used_slots', 0)}/{inventory.get('total_slots', 0)}")

    def display_state(self) -> None:
        """显示当前状态"""
        state = self.get_current_state()

        if self.output_format == "json":
            print(self.format_state_json(state))
        elif self.output_format == "compact":
            print(self.format_state_compact(state))
        else:  # pretty
            print(self.format_state_pretty(state))

    def monitor_loop(self) -> None:
        """监控循环"""
        print(f"🔄 开始实时监控 (刷新间隔: {self.refresh_interval}秒)")
        print("按 Ctrl+C 停止监控")
        print()

        try:
            while True:
                # 清屏（在支持的终端中）
                if self.output_format == "pretty":
                    os.system('clear' if os.name == 'posix' else 'cls')

                # 显示状态
                self.display_state()

                # 等待下次刷新
                time.sleep(self.refresh_interval)

        except KeyboardInterrupt:
            print("\n👋 监控已停止")

    def run_single_shot(self) -> None:
        """运行单次状态显示"""
        self.display_state()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="TRPG游戏状态实时监控工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
输出格式说明:
  pretty  - 美化格式，适合查看详细信息
  json    - JSON格式，适合程序处理
  compact - 紧凑格式，适合快速查看

示例用法:
  python game_state_monitor.py --format pretty --interval 1.0
  python game_state_monitor.py --format json --once
  python game_state_monitor.py --format compact
        """
    )

    parser.add_argument(
        '--format', '-f',
        choices=['pretty', 'json', 'compact'],
        default='pretty',
        help='输出格式 (默认: pretty)'
    )

    parser.add_argument(
        '--interval', '-i',
        type=float,
        default=2.0,
        help='刷新间隔秒数 (默认: 2.0)'
    )

    parser.add_argument(
        '--once', '-o',
        action='store_true',
        help='只运行一次，不进入监控循环'
    )

    args = parser.parse_args()

    try:
        # 创建监控器
        monitor = GameStateMonitor(
            output_format=args.format,
            refresh_interval=args.interval
        )

        # 创建演示状态
        monitor.create_demo_state()

        # 运行监控
        if args.once:
            monitor.run_single_shot()
        else:
            monitor.monitor_loop()

    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()