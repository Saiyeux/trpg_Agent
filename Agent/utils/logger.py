"""
游戏日志记录器

负责记录TRPG游戏的详细日志，包括AI交互、意图分析、游戏事件等。
提供结构化的日志存储和检索功能。

主要功能:
- AI模型交互日志
- 游戏事件记录
- 会话统计报告
- 日志文件管理
"""

import json
import datetime
import os
from typing import Dict, Any, Optional


class GameLogger:
    """
    TRPG游戏日志记录器
    
    记录游戏过程中的所有重要事件和AI交互，
    为游戏分析和问题诊断提供详细的日志支持。
    """
    
    def __init__(self, log_file: str = "trpg_game.log"):
        """
        初始化游戏日志记录器
        
        Args:
            log_file: 日志文件路径
        """
        self.session_start = datetime.datetime.now()
        self.log_entry_count = 0
        
        # 生成带时间戳的日志文件名
        self.log_file = self._generate_timestamped_filename(log_file)
        
        # 确保日志目录存在
        self._ensure_log_directory()
        
        # 创建会话开始标记
        self._write_session_header()
        
    def log_model_interaction(self, interaction_type: str, prompt: str, 
                            response: str, intent_data: Optional[Dict] = None) -> None:
        """
        记录AI模型交互
        
        Args:
            interaction_type: 交互类型（如'场景生成'、'意图分析'）
            prompt: 发送给AI的提示
            response: AI的响应
            intent_data: 意图分析数据（可选）
            
        调用时机: 每次与AI模型交互后
        """
        self.log_entry_count += 1
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        
        # 构建日志条目
        log_entry = {
            'timestamp': timestamp,
            'entry_id': self.log_entry_count,
            'type': interaction_type,
            'prompt': prompt,
            'response': response,
        }
        
        # 添加意图数据（如果有）
        if intent_data:
            log_entry['intent_category'] = intent_data.get('category', '未分类')
            log_entry['intent_description'] = intent_data.get('intent', '未知')
        
        # 写入文件日志
        self._write_detailed_log(log_entry)
        
        # 控制台简化输出
        print(f"[日志] 第{self.log_entry_count}条 - {interaction_type} - {timestamp}")
        
    def log_game_event(self, event_type: str, description: str, data: Optional[Dict] = None) -> None:
        """
        记录游戏事件
        
        Args:
            event_type: 事件类型（如'玩家输入'、'回合开始'、'游戏结束'）
            description: 事件描述
            data: 附加数据（可选）
            
        调用时机: 游戏中的重要事件发生时
        """
        full_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{full_timestamp}] 游戏事件: {event_type}\n")
            f.write(f"描述: {description}\n")
            if data:
                f.write(f"数据: {json.dumps(data, ensure_ascii=False)}\n")
            f.write("-" * 30 + "\n")
            
    def log_session_summary(self, intent_stats: Dict[str, Any], game_info: Optional[Dict] = None) -> None:
        """
        记录会话总结
        
        Args:
            intent_stats: 意图统计数据
            game_info: 游戏信息（可选）
            
        调用时机: 游戏会话结束时
        """
        session_end = datetime.datetime.now()
        session_duration = session_end - self.session_start
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"会话总结 - {session_end.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
            f.write(f"会话开始: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"会话结束: {session_end.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"会话时长: {session_duration}\n")
            f.write(f"总交互次数: {self.log_entry_count}\n")
            
            if game_info:
                f.write(f"\n游戏信息:\n")
                for key, value in game_info.items():
                    f.write(f"  {key}: {value}\n")
            
            f.write(f"\n意图统计:\n")
            f.write(json.dumps(intent_stats, ensure_ascii=False, indent=2))
            f.write(f"\n{'='*60}\n\n")
            
    def get_log_file_path(self) -> str:
        """
        获取日志文件的绝对路径
        
        Returns:
            日志文件的绝对路径
            
        调用时机: 需要显示日志文件位置时
        """
        return os.path.abspath(self.log_file)
        
    def get_session_info(self) -> Dict[str, Any]:
        """
        获取当前会话信息
        
        Returns:
            会话信息字典
            
        调用时机: 查询当前会话状态时
        """
        current_time = datetime.datetime.now()
        
        return {
            'session_start': self.session_start.strftime('%H:%M:%S'),
            'current_time': current_time.strftime('%H:%M:%S'),
            'session_duration': str(current_time - self.session_start),
            'log_entries': self.log_entry_count,
            'log_file': self.get_log_file_path()
        }
        
    def _ensure_log_directory(self) -> None:
        """确保日志文件目录存在"""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
    def _write_session_header(self) -> None:
        """写入会话开始标记"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"新游戏会话开始 - {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n")
            
    def _generate_timestamped_filename(self, original_filename: str) -> str:
        """生成带时间戳的文件名"""
        # 获取文件名和扩展名
        name, ext = os.path.splitext(original_filename)
        
        # 生成时间戳
        timestamp = self.session_start.strftime('%Y%m%d_%H%M%S')
        
        # 组合新文件名
        timestamped_name = f"{name}_{timestamp}{ext}"
        
        return timestamped_name
        
    def _write_detailed_log(self, log_entry: Dict[str, Any]) -> None:
        """写入详细的日志条目"""
        full_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{full_timestamp}] === 第{log_entry['entry_id']}条记录 ===\n")
            f.write(f"交互类型: {log_entry['type']}\n")
            f.write(f"模型输入:\n{log_entry['prompt']}\n")
            f.write(f"模型输出:\n{log_entry['response']}\n")
            
            if 'intent_category' in log_entry:
                f.write(f"意图分类: {log_entry['intent_category']}\n")
                f.write(f"意图描述: {log_entry['intent_description']}\n")
                
            f.write("-" * 50 + "\n")