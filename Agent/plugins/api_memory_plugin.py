"""
API导向的记忆插件实现

专为后端服务设计的记忆存储系统，优化了JSON格式以支持前端API调用。
提供历史对话显示、分页查询、TXT导出等功能。

主要功能:
- 单一JSONL文件存储，减少复杂度
- 支持分页查询历史记录
- 提供多种格式导出（TXT、HTML、Markdown）
- 优化的数据结构便于前端处理
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import uuid

from ..interfaces.memory_interface import MemoryInterface, ConversationTurn, RetrievalResult


class ApiMemoryPlugin(MemoryInterface):
    """
    API导向的记忆插件
    
    专为后端服务设计，提供前端友好的数据格式和API支持。
    单一文件存储，高效查询，支持多种导出格式。
    """
    
    @staticmethod
    def store_turn(storage_path: str, turn_data: ConversationTurn) -> bool:
        """存储单轮对话数据"""
        try:
            # 确保存储目录存在
            os.makedirs(storage_path, exist_ok=True)
            
            # 生成唯一ID
            turn_id = f"turn_{turn_data.turn:03d}_{uuid.uuid4().hex[:8]}"
            
            # 构建优化的记录格式
            record = {
                "id": turn_id,
                "turn": turn_data.turn,
                "timestamp": turn_data.timestamp,
                "player": turn_data.metadata.get("player_name", "未知玩家") if turn_data.metadata else "未知玩家",
                "scene": turn_data.scene,
                "user_input": turn_data.user_input,
                "ai_response": turn_data.ai_response,
                "keywords": ApiMemoryPlugin._extract_keywords(turn_data.user_input + " " + turn_data.ai_response),
                "metadata": turn_data.metadata or {}
            }
            
            # 追加到主文件
            conversation_file = os.path.join(storage_path, "conversation.jsonl")
            with open(conversation_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            
            # 更新会话摘要信息
            ApiMemoryPlugin._update_session_summary(storage_path, record)
            
            return True
            
        except Exception as e:
            print(f"Error storing turn data: {e}")
            return False
    
    @staticmethod
    def query_relevant(storage_path: str, query: str, limit: int = 3) -> List[RetrievalResult]:
        """查询相关历史记录"""
        try:
            conversation_file = os.path.join(storage_path, "conversation.jsonl")
            if not os.path.exists(conversation_file):
                return []
            
            query_keywords = set(ApiMemoryPlugin._extract_keywords(query))
            matches = []
            
            with open(conversation_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line.strip())
                        record_keywords = set(record.get("keywords", []))
                        
                        # 计算关键词重叠度
                        overlap = len(query_keywords & record_keywords)
                        if overlap > 0:
                            relevance = overlap / len(query_keywords | record_keywords)
                            content = f"【{record['scene']}】玩家: {record['user_input'][:50]}... AI: {record['ai_response'][:50]}..."
                            
                            matches.append(RetrievalResult(
                                content=content,
                                relevance=relevance,
                                turn=record["turn"],
                                timestamp=record["timestamp"],
                                metadata={
                                    "id": record["id"],
                                    "scene": record["scene"],
                                    "full_input": record["user_input"],
                                    "full_response": record["ai_response"]
                                }
                            ))
            
            # 按相关度排序并返回
            matches.sort(key=lambda x: x.relevance, reverse=True)
            return matches[:limit]
            
        except Exception as e:
            print(f"Error querying relevant data: {e}")
            return []
    
    @staticmethod  
    def get_recent_context(storage_path: str, turns: int = 5) -> str:
        """获取最近N轮的上下文摘要"""
        try:
            conversation_file = os.path.join(storage_path, "conversation.jsonl")
            if not os.path.exists(conversation_file):
                return "暂无历史记录"
            
            # 读取最近的记录
            with open(conversation_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                recent_lines = lines[-turns:] if len(lines) > turns else lines
            
            # 构建上下文摘要
            context_parts = []
            for line in recent_lines:
                if line.strip():
                    record = json.loads(line.strip())
                    summary = f"回合{record['turn']}: {record['user_input'][:30]}... -> {record['ai_response'][:30]}..."
                    context_parts.append(summary)
            
            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"Error getting recent context: {e}")
            return "获取上下文失败"
    
    @staticmethod
    def initialize_storage(storage_path: str) -> bool:
        """初始化存储路径"""
        try:
            os.makedirs(storage_path, exist_ok=True)
            
            # 创建会话摘要文件
            session_info = {
                "session_id": os.path.basename(storage_path),
                "created_at": datetime.now().isoformat(),
                "memory_type": "api_optimized",
                "version": "2.0.0",
                "total_turns": 0,
                "last_updated": None,
                "player_name": None
            }
            
            info_file = os.path.join(storage_path, "session_summary.json")
            with open(info_file, "w", encoding="utf-8") as f:
                json.dump(session_info, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error initializing storage: {e}")
            return False
    
    @staticmethod
    def storage_exists(storage_path: str) -> bool:
        """检查存储路径是否存在"""
        return os.path.exists(storage_path) and os.path.exists(os.path.join(storage_path, "session_summary.json"))
    
    @staticmethod
    def get_storage_stats(storage_path: str) -> Dict[str, Any]:
        """获取存储统计信息"""
        try:
            # 读取会话摘要
            summary_file = os.path.join(storage_path, "session_summary.json")
            if os.path.exists(summary_file):
                with open(summary_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            
            return {"error": "Session summary not found"}
            
        except Exception as e:
            return {"error": str(e)}
    
    # === API专用方法 ===
    
    @staticmethod
    def get_conversation_history(storage_path: str, page: int = 1, page_size: int = 20, reverse: bool = True) -> Dict[str, Any]:
        """
        获取分页的对话历史（API专用）
        
        Args:
            storage_path: 存储路径
            page: 页码（从1开始）
            page_size: 每页条数
            reverse: 是否倒序（最新的在前）
            
        Returns:
            包含对话数据和分页信息的字典
        """
        try:
            conversation_file = os.path.join(storage_path, "conversation.jsonl")
            if not os.path.exists(conversation_file):
                return {"conversations": [], "total": 0, "page": page, "page_size": page_size}
            
            # 读取所有记录
            conversations = []
            with open(conversation_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        conversations.append(json.loads(line.strip()))
            
            total = len(conversations)
            
            # 排序
            if reverse:
                conversations = conversations[::-1]
            
            # 分页
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            page_conversations = conversations[start_idx:end_idx]
            
            return {
                "conversations": page_conversations,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def export_to_txt(storage_path: str, format_type: str = "readable") -> str:
        """
        导出对话记录为TXT格式（API专用）
        
        Args:
            storage_path: 存储路径
            format_type: 导出格式 ("readable", "compact", "markdown")
            
        Returns:
            格式化的文本内容
        """
        try:
            conversation_file = os.path.join(storage_path, "conversation.jsonl")
            if not os.path.exists(conversation_file):
                return "# 暂无对话记录\n"
            
            # 获取会话信息
            session_info = ApiMemoryPlugin.get_storage_stats(storage_path)
            
            # 构建文本内容
            if format_type == "markdown":
                return ApiMemoryPlugin._export_markdown(conversation_file, session_info)
            elif format_type == "compact":
                return ApiMemoryPlugin._export_compact(conversation_file, session_info)
            else:  # readable
                return ApiMemoryPlugin._export_readable(conversation_file, session_info)
                
        except Exception as e:
            return f"# 导出失败\n错误: {str(e)}\n"
    
    @staticmethod
    def search_conversations(storage_path: str, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索对话记录（API专用）
        
        Args:
            storage_path: 存储路径
            keyword: 搜索关键词
            limit: 返回条数限制
            
        Returns:
            匹配的对话记录列表
        """
        try:
            conversation_file = os.path.join(storage_path, "conversation.jsonl")
            if not os.path.exists(conversation_file):
                return []
            
            matches = []
            keyword_lower = keyword.lower()
            
            with open(conversation_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line.strip())
                        
                        # 搜索用户输入、AI回复、场景
                        if (keyword_lower in record["user_input"].lower() or 
                            keyword_lower in record["ai_response"].lower() or 
                            keyword_lower in record["scene"].lower()):
                            
                            matches.append(record)
                            
                            if len(matches) >= limit:
                                break
            
            return matches
            
        except Exception as e:
            print(f"Error searching conversations: {e}")
            return []
    
    # === 私有方法 ===
    
    @staticmethod
    def _update_session_summary(storage_path: str, record: Dict[str, Any]) -> None:
        """更新会话摘要信息"""
        try:
            summary_file = os.path.join(storage_path, "session_summary.json")
            
            if os.path.exists(summary_file):
                with open(summary_file, "r", encoding="utf-8") as f:
                    summary = json.load(f)
            else:
                summary = {"total_turns": 0}
            
            # 更新统计信息
            summary["total_turns"] = record["turn"]
            summary["last_updated"] = record["timestamp"]
            summary["player_name"] = record["player"]
            
            # 计算存储大小
            conversation_file = os.path.join(storage_path, "conversation.jsonl")
            if os.path.exists(conversation_file):
                summary["storage_size"] = os.path.getsize(conversation_file)
            
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error updating session summary: {e}")
    
    @staticmethod
    def _export_readable(conversation_file: str, session_info: Dict[str, Any]) -> str:
        """导出为可读格式"""
        lines = [
            f"# TRPG对话记录",
            f"# 会话ID: {session_info.get('session_id', '未知')}",
            f"# 玩家: {session_info.get('player_name', '未知')}",
            f"# 创建时间: {session_info.get('created_at', '未知')[:19].replace('T', ' ')}",
            f"# 总回合数: {session_info.get('total_turns', 0)}",
            "",
        ]
        
        with open(conversation_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line.strip())
                    lines.extend([
                        f"[回合{record['turn']}] {record['timestamp'][:19].replace('T', ' ')}",
                        f"场景: {record['scene']}",
                        f"玩家: {record['user_input']}",
                        f"DM: {record['ai_response']}",
                        ""
                    ])
        
        return "\n".join(lines)
    
    @staticmethod
    def _export_compact(conversation_file: str, session_info: Dict[str, Any]) -> str:
        """导出为紧凑格式"""
        lines = [f"# {session_info.get('player_name', '玩家')}的TRPG记录 ({session_info.get('total_turns', 0)}回合)", ""]
        
        with open(conversation_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line.strip())
                    lines.append(f"T{record['turn']} P:{record['user_input']} D:{record['ai_response']}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _export_markdown(conversation_file: str, session_info: Dict[str, Any]) -> str:
        """导出为Markdown格式"""
        lines = [
            f"# TRPG对话记录",
            "",
            f"**会话信息**:",
            f"- 玩家: {session_info.get('player_name', '未知')}",
            f"- 创建时间: {session_info.get('created_at', '未知')[:19].replace('T', ' ')}",
            f"- 总回合数: {session_info.get('total_turns', 0)}",
            "",
            "---",
            "",
        ]
        
        with open(conversation_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line.strip())
                    lines.extend([
                        f"## 回合 {record['turn']} - {record['scene']}",
                        "",
                        f"**玩家行动**: {record['user_input']}",
                        "",
                        f"**DM回应**: {record['ai_response']}",
                        "",
                        f"*时间: {record['timestamp'][:19].replace('T', ' ')}*",
                        "",
                        "---",
                        "",
                    ])
        
        return "\n".join(lines)
    
    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """提取关键词（同原实现）"""
        text = re.sub(r'[^\w\s]', '', text.lower())
        words = text.split()
        
        stopwords = {'的', '是', '在', '了', '和', '与', '或', '但', '而', '你', '我', '他', '她', '它', '们', '这', '那', '要', '不', '也', '就', '都', '会', '能', '可以', '可能', '应该', '必须', '将', '把', '被', '给', '从', '到', '为', '由', '因为', '所以', '如果', '虽然', '但是', '然而', '因此', '只是', '还是', '或者', '以及', '等等'}
        
        keywords = []
        for word in words:
            if len(word) > 1 and word not in stopwords:
                keywords.append(word)
        
        return list(set(keywords[:10]))  # 限制关键词数量


# 注册新插件
from . import PluginRegistry
PluginRegistry.register("memory", ApiMemoryPlugin)