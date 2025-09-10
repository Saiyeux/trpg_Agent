"""
游戏引擎

TRPG系统的核心引擎，协调各个模块的工作，管理游戏流程。
提供完整的游戏会话管理和用户交互功能。

主要功能:
- 游戏会话管理
- 用户输入处理
- AI交互协调
- 游戏状态维护
- 优雅的退出处理
"""

import signal
import sys
import json
from typing import Dict, Any, Optional

from .game_state import GameState
from ..client.model_client import ModelClient, APIType
from ..utils.intent_analyzer import IntentAnalyzer
from ..utils.action_dispatcher import ActionDispatcher
from ..utils.logger import GameLogger
from ..config.settings import ConfigManager


class GameEngine:
    """
    AI-TRPG 游戏引擎
    
    系统的核心控制器，负责协调所有模块的工作，管理完整的游戏会话。
    处理用户输入、AI交互、状态更新和日志记录。
    """
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """
        初始化游戏引擎
        
        Args:
            config_manager: 配置管理器实例，如果为None则创建新实例
        """
        # 加载配置
        self.config = config_manager or ConfigManager()
        
        # 验证配置
        config_errors = self.config.validate_config()
        if config_errors:
            print("配置验证失败:")
            for error in config_errors:
                print(f"  - {error}")
            print("请运行配置程序修复配置")
            sys.exit(1)
            
        # 初始化各个组件
        self._initialize_components()
        
        # 设置信号处理器（Ctrl+C优雅退出）
        signal.signal(signal.SIGINT, self._signal_handler)
        
        print("AI-TRPG 游戏引擎初始化完成")
        
    def start_game(self) -> None:
        """
        启动新的游戏会话
        
        调用时机: 程序入口，开始新游戏时
        """
        print("\n" + "="*50)
        print("    欢迎来到 AI-TRPG 世界！")  
        print("="*50)
        
        # 显示当前配置
        self.config.display_config()
        
        # 获取玩家信息
        self._setup_player()
        
        # 设置RAG会话
        self._setup_rag_session()
        
        # 记录游戏开始事件
        self.logger.log_game_event("游戏开始", f"玩家 {self.game_state.player_name} 开始新的冒险")
        
        # 生成初始场景
        self._generate_initial_scene()
        
        # 进入主游戏循环
        self._main_game_loop()
        
    def _initialize_components(self) -> None:
        """初始化所有游戏组件"""
        # 获取配置
        api_config = self.config.get_api_config()
        game_config = self.config.get_game_config()
        logging_config = self.config.get_logging_config()
        rag_config = self.config.get_rag_config()
        
        # 初始化核心组件
        self.game_state = GameState()
        
        # 初始化AI客户端
        self.ai_client = ModelClient(
            model_name=api_config['model'],
            api_type=self.config.get_api_type(),
            base_url=api_config['base_url'],
            context_limit=api_config['context_limit']
        )
        
        # 初始化工具组件
        self.intent_analyzer = IntentAnalyzer()
        self.action_dispatcher = ActionDispatcher()
        self.logger = GameLogger(logging_config['log_file'])
        
        # 保存配置引用
        self.game_config = game_config
        self.rag_config = rag_config
        
        # 初始化RAG功能
        self._initialize_rag()
        
    def _setup_player(self) -> None:
        """设置玩家信息"""
        while True:
            player_name = input("\n请输入你的角色名: ").strip()
            if player_name:
                self.game_state.player_name = player_name
                break
            print("角色名不能为空，请重新输入")
            
        print(f"\n欢迎，{self.game_state.player_name}！你的冒险即将开始...")
        
    def _generate_initial_scene(self) -> None:
        """生成游戏的初始场景"""
        try:
            print("\n正在生成初始场景...")
            
            initial_scene = self.ai_client.generate_scene(
                context_history=[],
                player_name=self.game_state.player_name,
                turn_count=0
            )
            
            # 记录日志
            self.logger.log_model_interaction(
                "初始场景生成", 
                f"为玩家 {self.game_state.player_name} 生成初始场景",
                initial_scene
            )
            
            # 更新游戏状态
            self.game_state.current_scene = initial_scene
            self.game_state.add_to_history("初始场景", initial_scene)
            
            print(f"\n🎭 场景描述:")
            print(f"{initial_scene}")
            
        except Exception as e:
            print(f"生成初始场景失败: {e}")
            print("请检查AI服务是否正常运行")
            sys.exit(1)
            
    def _main_game_loop(self) -> None:
        """主游戏循环"""
        print(f"\n" + "-"*50)
        print("游戏开始！输入 'help' 查看帮助，输入 'quit' 退出游戏")
        print("-"*50)
        
        while True:
            try:
                # 开始新回合
                self.game_state.next_turn()
                
                # 获取用户输入
                user_input = self._get_user_input()
                
                # 处理特殊命令
                if self._handle_special_commands(user_input):
                    continue
                    
                # 记录玩家行动
                self.game_state.add_to_history("玩家行动", user_input)
                self.logger.log_game_event("玩家行动", user_input, {
                    'turn': self.game_state.turn_count,
                    'player': self.game_state.player_name
                })
                
                # 处理玩家行动
                self._process_player_action(user_input)
                
                # 生成新场景
                self._generate_next_scene()
                
                # 存储完整的对话轮次到RAG
                ai_response = self.game_state.current_scene or "场景生成失败"
                self._store_conversation_turn(user_input, ai_response)
                
            except KeyboardInterrupt:
                # Ctrl+C 被信号处理器捕获，这里不应该到达
                break
            except Exception as e:
                print(f"\n处理过程中出错: {e}")
                print("请重试或输入 'quit' 退出游戏")
                
    def _get_user_input(self) -> str:
        """获取用户输入"""
        # 计算当前上下文长度
        context = self.game_state.get_context(
            last_n=self.game_config['context_history_limit'],
            context_limit=self.ai_client.context_limit
        )
        context_text = "\n".join([f"{entry['type']}: {entry['content']}" for entry in context])
        context_length_k = len(context_text) / 1000
        
        # 构建状态信息
        status_parts = [f"回合 {self.game_state.turn_count}"]
        status_parts.append(f"即时上下文: {context_length_k:.1f}k")
        
        # 添加RAG记忆信息
        if self.rag_plugin and self.rag_storage_path:
            try:
                stats = self.rag_plugin.get_storage_stats(self.rag_storage_path)
                memory_count = stats.get('total_turns', 0)
                if memory_count > 0:
                    status_parts.append(f"🧠 记忆: {memory_count}轮")
            except:
                pass
        
        print(f"\n📍 {' | '.join(status_parts)}")
        return input("你的行动: ").strip()
        
    def _handle_special_commands(self, user_input: str) -> bool:
        """
        处理特殊命令
        
        Args:
            user_input: 用户输入
            
        Returns:
            True如果是特殊命令并已处理，False如果需要继续正常处理
        """
        command = user_input.lower()
        
        if command in ['quit', 'exit', '退出']:
            self._graceful_shutdown("用户主动退出")
            return True
            
        elif command in ['help', '帮助']:
            self._show_help()
            return True
            
        elif command in ['stats', '统计']:
            self.intent_analyzer.display_statistics()
            return True
            
        elif command in ['status', '状态']:
            self._show_game_status()
            return True
            
        elif command in ['config', '配置']:
            self.config.display_config()
            return True
            
        return False
        
    def _process_player_action(self, user_input: str) -> None:
        """处理玩家行动"""
        try:
            # AI分析玩家意图
            print("\n🤖 正在分析你的意图...")
            raw_intent = self.ai_client.analyze_intent(user_input, self.game_state.current_scene)
            
            # 解析意图数据
            intent_data = self._parse_intent_data(raw_intent)
            
            # 记录意图
            self.intent_analyzer.add_intent(intent_data)
            
            # 记录AI交互日志
            self.logger.log_model_interaction("意图分析", user_input, raw_intent, intent_data)
            
            # 显示意图分析结果
            self._display_intent_analysis(intent_data)
            
            # 尝试执行对应行动
            self._execute_action(intent_data)
            
        except Exception as e:
            print(f"处理玩家行动时出错: {e}")
            
    def _parse_intent_data(self, raw_intent: str) -> Dict[str, Any]:
        """解析AI返回的意图数据"""
        try:
            # 直接尝试解析JSON
            return json.loads(raw_intent)
        except json.JSONDecodeError:
            # 尝试提取被```json包装的JSON
            cleaned_json = self._extract_json_from_markdown(raw_intent)
            if cleaned_json:
                try:
                    return json.loads(cleaned_json)
                except json.JSONDecodeError:
                    pass
            
            # 解析失败时返回默认结构
            return {
                'intent': '解析失败的意图',
                'category': '解析错误', 
                'target': '未知',
                'response': raw_intent  # 保留原始响应
            }
            
    def _extract_json_from_markdown(self, text: str) -> str:
        """从Markdown代码块中提取JSON"""
        import re
        
        # 匹配```json...```格式
        json_pattern = r'```json\s*\n(.*?)\n```'
        match = re.search(json_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
            
        # 匹配```...```格式（没有json标记）
        code_pattern = r'```\s*\n(.*?)\n```'
        match = re.search(code_pattern, text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            # 检查是否像JSON（以{开头，以}结尾）
            if content.startswith('{') and content.endswith('}'):
                return content
                
        return ""
            
    def _display_intent_analysis(self, intent_data: Dict[str, Any]) -> None:
        """显示意图分析结果"""
        print(f"\n📋 意图分析:")
        print(f"   意图: {intent_data.get('intent', '未知')}")
        print(f"   分类: {intent_data.get('category', '未分类')}")
        
        # 显示执行结果
        action_result = self.action_dispatcher.dispatch_action(
            intent_data.get('category', ''),
            intent_data,
            self.game_state
        )
        
        if action_result:
            print(f"   执行: {action_result}")
        else:
            print(f"   执行: 生成回复")
            
        # 显示AI的直接回应
        if 'response' in intent_data:
            print(f"\n💬 回应: {intent_data['response']}")
            
    def _execute_action(self, intent_data: Dict[str, Any]) -> None:
        """执行对应的行动逻辑"""
        # 这里可以添加更复杂的行动执行逻辑
        # 目前主要依靠action_dispatcher处理
        pass
        
    def _generate_next_scene(self) -> None:
        """生成下一个场景"""
        try:
            print("\n🎬 正在生成新场景...")
            
            # 获取上下文
            context = self.game_state.get_context(
                last_n=self.game_config['context_history_limit'],
                context_limit=self.ai_client.context_limit
            )
            
            # 查询RAG增强上下文
            rag_context = ""
            if self.rag_plugin and context:
                # 使用最近的玩家输入查询相关历史
                last_input = context[-1].get('content', '') if context else ''
                if last_input:
                    rag_context = self._query_rag_context(last_input)
            
            # 生成新场景
            new_scene = self.ai_client.generate_scene(
                context_history=context,
                player_name=self.game_state.player_name,
                turn_count=self.game_state.turn_count,
                rag_context=rag_context
            )
            
            # 记录日志
            self.logger.log_model_interaction("场景生成", "生成新场景", new_scene)
            
            # 更新游戏状态
            self.game_state.current_scene = new_scene
            self.game_state.add_to_history("场景", new_scene)
            
            # 显示新场景
            print(f"\n🎭 场景描述:")
            print(f"{new_scene}")
            
        except Exception as e:
            print(f"生成场景失败: {e}")
            
    def _show_help(self) -> None:
        """显示帮助信息"""
        print(f"\n=== 游戏帮助 ===")
        print("基本命令:")
        print("  help/帮助    - 显示此帮助")
        print("  quit/退出    - 退出游戏")
        print("  stats/统计   - 显示意图统计")
        print("  status/状态  - 显示游戏状态")
        print("  config/配置  - 显示当前配置")
        print("\n游戏玩法:")
        print("  描述你想要执行的行动，AI会分析你的意图并生成相应场景")
        print("  例如: '探索前方的洞穴'、'与NPC对话'、'查看背包'等")
        print("================")
        
    def _show_game_status(self) -> None:
        """显示游戏状态"""
        game_info = self.game_state.get_game_info()
        session_info = self.logger.get_session_info()
        
        print(f"\n=== 游戏状态 ===")
        print(f"玩家: {game_info['player_name']}")
        print(f"当前回合: {game_info['turn_count']}")
        print(f"即时历史: {game_info['history_count']} 条")
        print(f"会话时长: {session_info['session_duration']}")
        
        # 显示RAG记忆状态
        if self.rag_plugin and self.rag_storage_path:
            try:
                stats = self.rag_plugin.get_storage_stats(self.rag_storage_path)
                print(f"🧠 长期记忆: {stats.get('total_turns', 0)} 轮对话")
                storage_mb = stats.get('storage_size', 0) / 1024 / 1024
                print(f"   存储大小: {storage_mb:.2f} MB")
                if stats.get('created_at'):
                    print(f"   创建时间: {stats['created_at'][:19].replace('T', ' ')}")
            except Exception as e:
                print(f"🧠 长期记忆: 获取状态失败 ({e})")
        else:
            print("🧠 长期记忆: 未启用")
            
        print("================")
        
    def _signal_handler(self, sig, frame) -> None:
        """
        信号处理器，处理Ctrl+C
        
        Args:
            sig: 信号类型
            frame: 当前帧
        """
        print("\n\n🛑 检测到中断信号...")
        self._graceful_shutdown("用户中断")
        
    def _graceful_shutdown(self, reason: str) -> None:
        """
        优雅关闭游戏
        
        Args:
            reason: 关闭原因
        """
        print(f"\n{'='*50}")
        print("           游戏会话结束")
        print(f"{'='*50}")
        
        # 显示统计信息
        self.intent_analyzer.display_statistics()
        
        # 记录会话总结
        intent_stats = self.intent_analyzer.get_statistics()
        game_info = self.game_state.get_game_info()
        
        self.logger.log_game_event("游戏结束", reason, {
            'final_turn': self.game_state.turn_count,
            'total_intents': intent_stats.get('total_intents', 0)
        })
        
        self.logger.log_session_summary(intent_stats, game_info)
        
        # 显示日志文件位置
        print(f"\n📋 游戏日志已保存到: {self.logger.get_log_file_path()}")
        print("\n感谢游戏！再见！👋")
        
        sys.exit(0)
        
    def _initialize_rag(self) -> None:
        """初始化RAG功能"""
        self.rag_plugin = None
        self.rag_storage_path = None
        
        # 检查RAG是否启用
        if not self.rag_config.get('enabled', False):
            return
            
        try:
            # 导入RAG插件
            from ..plugins import PluginRegistry
            from ..plugins.api_memory_plugin import ApiMemoryPlugin
            
            # 获取插件
            plugin_class = PluginRegistry.get_plugin("memory")
            if plugin_class:
                self.rag_plugin = plugin_class
                print("✅ RAG功能已启用")
            else:
                print("⚠️  RAG插件未找到，功能将被禁用")
                
        except ImportError as e:
            print(f"⚠️  RAG模块导入失败: {e}")
            print("   请安装依赖: pip install lightrag-hku")
        except Exception as e:
            print(f"⚠️  RAG初始化失败: {e}")
    
    def _setup_rag_session(self) -> None:
        """设置RAG会话存储"""
        if not self.rag_plugin:
            return
            
        try:
            # 生成会话存储路径
            from datetime import datetime
            session_id = f"trpg_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            base_path = self.rag_config.get('storage_path', 'storage/conversations')
            self.rag_storage_path = f"{base_path}/{session_id}"
            
            # 初始化存储
            if self.rag_plugin.initialize_storage(self.rag_storage_path):
                print(f"📁 RAG会话已创建: {session_id}")
            else:
                print("⚠️  RAG存储初始化失败")
                self.rag_plugin = None
                
        except Exception as e:
            print(f"⚠️  RAG会话设置失败: {e}")
            self.rag_plugin = None
    
    def _store_conversation_turn(self, user_input: str, ai_response: str) -> None:
        """存储对话轮次到RAG"""
        if not self.rag_plugin or not self.rag_storage_path:
            return
            
        try:
            from ..interfaces.memory_interface import ConversationTurn
            from datetime import datetime
            
            turn_data = ConversationTurn(
                user_input=user_input,
                ai_response=ai_response,
                turn=self.game_state.turn_count,
                timestamp=datetime.now().isoformat(),
                scene=self.game_state.current_scene or "未知场景",
                metadata={
                    "player_name": self.game_state.player_name
                }
            )
            
            self.rag_plugin.store_turn(self.rag_storage_path, turn_data)
            
        except Exception as e:
            print(f"⚠️  RAG存储失败: {e}")
    
    def _query_rag_context(self, query: str) -> str:
        """查询RAG增强上下文"""
        if not self.rag_plugin or not self.rag_storage_path:
            return ""
            
        try:
            limit = self.rag_config.get('query_limit', 3)
            results = self.rag_plugin.query_relevant(self.rag_storage_path, query, limit)
            
            if results:
                context_parts = []
                for result in results:
                    context_parts.append(f"相关回忆 (相关度{result.relevance:.1f}): {result.content}")
                return "\n".join(context_parts)
            
        except Exception as e:
            print(f"⚠️  RAG查询失败: {e}")
            
        return ""