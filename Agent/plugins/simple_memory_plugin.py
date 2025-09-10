"""
简单记忆插件实现

基于文件存储的简单记忆实现，提供基础的对话存储和检索功能。
不依赖复杂的RAG框架，适合快速原型和测试。

主要功能:
- JSON格式对话存储
- 关键词匹配检索
- 简单的上下文摘要
- 文件统计功能
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from ..interfaces.memory_interface import MemoryInterface, ConversationTurn, RetrievalResult


class SimpleMemoryPlugin(MemoryInterface):
    """
    简单记忆插件实现
    
    使用JSON文件存储对话记录，提供基本的文本检索功能。
    适合开发和测试阶段使用，后续可以升级到更强大的RAG实现。
    """
    
    @staticmethod
    def store_turn(storage_path: str, turn_data: ConversationTurn) -> bool:
        """存储单轮对话数据"""
        try:
            # 确保存储目录存在
            os.makedirs(storage_path, exist_ok=True)
            
            # 准备数据
            turn_record = {
                "user_input": turn_data.user_input,
                "ai_response": turn_data.ai_response,
                "turn": turn_data.turn,
                "timestamp": turn_data.timestamp,
                "scene": turn_data.scene,
                "metadata": turn_data.metadata or {}
            }
            
            # 保存到对话记录文件
            conversation_file = os.path.join(storage_path, "conversation.jsonl")
            with open(conversation_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(turn_record, ensure_ascii=False) + "\n")
            
            # 更新索引文件（用于快速检索）
            index_file = os.path.join(storage_path, "search_index.json")
            index = SimpleMemoryPlugin._load_index(index_file)
            
            # 提取关键词
            keywords = SimpleMemoryPlugin._extract_keywords(turn_data.user_input + " " + turn_data.ai_response)
            
            # 更新索引
            for keyword in keywords:
                if keyword not in index:
                    index[keyword] = []
                index[keyword].append({
                    "turn": turn_data.turn,
                    "timestamp": turn_data.timestamp,
                    "relevance": 1.0  # 基础相关度
                })
            
            # 保存索引
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error storing turn data: {e}")
            return False
    
    @staticmethod
    def query_relevant(storage_path: str, query: str, limit: int = 3) -> List[RetrievalResult]:
        """查询相关历史记录"""
        try:
            # 加载索引
            index_file = os.path.join(storage_path, "search_index.json")
            index = SimpleMemoryPlugin._load_index(index_file)
            
            # 提取查询关键词
            query_keywords = SimpleMemoryPlugin._extract_keywords(query)
            
            # 查找匹配的记录
            matches = {}
            for keyword in query_keywords:
                if keyword in index:
                    for record in index[keyword]:
                        turn_id = record["turn"]
                        if turn_id not in matches:
                            matches[turn_id] = {
                                "turn": turn_id,
                                "timestamp": record["timestamp"],
                                "relevance": 0.0
                            }
                        matches[turn_id]["relevance"] += 1.0
            
            # 按相关度排序
            sorted_matches = sorted(matches.values(), key=lambda x: x["relevance"], reverse=True)
            
            # 加载实际对话内容
            results = []
            conversation_file = os.path.join(storage_path, "conversation.jsonl")
            
            if os.path.exists(conversation_file):
                with open(conversation_file, "r", encoding="utf-8") as f:
                    conversations = [json.loads(line.strip()) for line in f if line.strip()]
                
                # 根据匹配结果构建返回数据
                for match in sorted_matches[:limit]:
                    for conv in conversations:
                        if conv["turn"] == match["turn"]:
                            content = f"玩家: {conv['user_input'][:100]}... AI: {conv['ai_response'][:100]}..."
                            results.append(RetrievalResult(
                                content=content,
                                relevance=match["relevance"] / len(query_keywords),  # 标准化相关度
                                turn=conv["turn"],
                                timestamp=conv["timestamp"],
                                metadata={"scene": conv.get("scene", "未知")}
                            ))
                            break
            
            return results
            
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
            
            # 构建摘要
            context_parts = []
            for line in recent_lines:
                conv = json.loads(line.strip())
                summary = f"回合{conv['turn']}: {conv['user_input'][:50]}... -> {conv['ai_response'][:50]}..."
                context_parts.append(summary)
            
            return "\n".join(context_parts)
            
        except Exception as e:
            print(f"Error getting recent context: {e}")
            return "获取上下文失败"
    
    @staticmethod
    def initialize_storage(storage_path: str) -> bool:
        """初始化存储路径"""
        try:
            # 创建目录
            os.makedirs(storage_path, exist_ok=True)
            
            # 创建会话信息文件
            session_info = {
                "created_at": datetime.now().isoformat(),
                "memory_type": "simple",
                "version": "1.0.0"
            }
            
            info_file = os.path.join(storage_path, "session_info.json")
            with open(info_file, "w", encoding="utf-8") as f:
                json.dump(session_info, f, indent=2, ensure_ascii=False)
            
            # 初始化空索引
            index_file = os.path.join(storage_path, "search_index.json")
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
            
            return True
            
        except Exception as e:
            print(f"Error initializing storage: {e}")
            return False
    
    @staticmethod
    def storage_exists(storage_path: str) -> bool:
        """检查存储路径是否存在"""
        return os.path.exists(storage_path) and os.path.exists(os.path.join(storage_path, "session_info.json"))
    
    @staticmethod
    def get_storage_stats(storage_path: str) -> Dict[str, Any]:
        """获取存储统计信息"""
        try:
            stats = {
                "total_turns": 0,
                "storage_size": 0,
                "created_at": None,
                "last_updated": None
            }
            
            # 读取会话信息
            info_file = os.path.join(storage_path, "session_info.json")
            if os.path.exists(info_file):
                with open(info_file, "r", encoding="utf-8") as f:
                    info = json.load(f)
                    stats["created_at"] = info.get("created_at")
            
            # 统计对话数量
            conversation_file = os.path.join(storage_path, "conversation.jsonl")
            if os.path.exists(conversation_file):
                with open(conversation_file, "r", encoding="utf-8") as f:
                    stats["total_turns"] = len(f.readlines())
                stats["last_updated"] = datetime.fromtimestamp(
                    os.path.getmtime(conversation_file)
                ).isoformat()
            
            # 计算存储大小
            if os.path.exists(storage_path):
                total_size = 0
                for root, dirs, files in os.walk(storage_path):
                    for file in files:
                        total_size += os.path.getsize(os.path.join(root, file))
                stats["storage_size"] = total_size
            
            return stats
            
        except Exception as e:
            print(f"Error getting storage stats: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def _load_index(index_file: str) -> Dict[str, Any]:
        """加载搜索索引"""
        try:
            if os.path.exists(index_file):
                with open(index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        except:
            return {}
    
    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取：去除标点，分词，过滤停用词
        # 这里使用基本实现，可以后续改进
        text = re.sub(r'[^\w\s]', '', text.lower())
        words = text.split()
        
        # 过滤长度和停用词
        stopwords = {'的', '是', '在', '了', '和', '与', '或', '但', '而', '你', '我', '他', '她', '它', '们', '这', '那', '要', '不', '也', '就', '都', '会', '能', '可以', '可能', '应该', '必须', '将', '把', '被', '给', '从', '到', '为', '由', '因为', '所以', '如果', '虽然', '但是', '然而', '因此', '只是', '还是', '或者', '以及', '等等'}
        
        keywords = []
        for word in words:
            if len(word) > 1 and word not in stopwords:
                keywords.append(word)
        
        return list(set(keywords))  # 去重


# 插件已被 ApiMemoryPlugin 替代，注册已移除
# from . import PluginRegistry
# PluginRegistry.register("memory", SimpleMemoryPlugin)