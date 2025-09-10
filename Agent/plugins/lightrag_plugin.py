"""
LightRAG记忆插件实现

基于LightRAG的知识图谱RAG实现，提供TRPG对话的长期记忆功能。
支持语义检索、上下文增强和跨会话记忆管理。

主要功能:
- 对话数据的知识图谱存储
- 基于语义相似度的历史检索
- 智能上下文摘要生成
- 会话管理和统计功能
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

try:
    from lightrag import LightRAG, QueryParam
    LIGHTRAG_AVAILABLE = True
except ImportError:
    LIGHTRAG_AVAILABLE = False
    LightRAG = None
    QueryParam = None

from ..interfaces.memory_interface import MemoryInterface, ConversationTurn, RetrievalResult


class LightRAGPlugin(MemoryInterface):
    """
    LightRAG记忆插件实现
    
    使用LightRAG构建TRPG对话的知识图谱，提供智能记忆和检索功能。
    支持本地Ollama模型集成，无需外部API服务。
    """
    
    # 类级别的LightRAG实例缓存
    _rag_instances: Dict[str, Any] = {}
    
    @staticmethod
    def _check_availability():
        """检查LightRAG是否可用"""
        if not LIGHTRAG_AVAILABLE:
            raise ImportError("LightRAG not available. Install with: pip install lightrag-hku")
    
    @staticmethod
    def _get_rag_instance(storage_path: str) -> Any:
        """获取或创建LightRAG实例"""
        LightRAGPlugin._check_availability()
        
        # 检查缓存
        if storage_path in LightRAGPlugin._rag_instances:
            return LightRAGPlugin._rag_instances[storage_path]
        
        # 创建新实例
        try:
            # 确保存储目录存在
            os.makedirs(storage_path, exist_ok=True)
            
            # 配置LightRAG（使用默认配置）
            rag = LightRAG(
                working_dir=storage_path,
                # 使用默认的LLM和embedding配置
                # 可以后续通过环境变量或配置文件自定义
            )
            
            # 缓存实例
            LightRAGPlugin._rag_instances[storage_path] = rag
            return rag
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LightRAG: {e}")
    
    @staticmethod
    def store_turn(storage_path: str, turn_data: ConversationTurn) -> bool:
        """存储单轮对话数据"""
        try:
            rag = LightRAGPlugin._get_rag_instance(storage_path)
            
            # 构建对话文本用于存储
            conversation_text = f"""
回合 {turn_data.turn} - {turn_data.timestamp}
场景: {turn_data.scene}

玩家行动: {turn_data.user_input}

AI回应: {turn_data.ai_response}

---
"""
            
            # 异步插入数据到知识图谱
            asyncio.run(rag.ainsert(conversation_text))
            
            # 保存元数据到JSON文件
            metadata_file = os.path.join(storage_path, "turn_metadata.jsonl")
            metadata = {
                "turn": turn_data.turn,
                "timestamp": turn_data.timestamp,
                "scene": turn_data.scene,
                "user_input": turn_data.user_input,
                "ai_response": turn_data.ai_response,
                "metadata": turn_data.metadata or {}
            }
            
            with open(metadata_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(metadata, ensure_ascii=False) + "\n")
            
            return True
            
        except Exception as e:
            print(f"Error storing turn data: {e}")
            return False
    
    @staticmethod
    def query_relevant(storage_path: str, query: str, limit: int = 3) -> List[RetrievalResult]:
        """查询相关历史记录"""
        try:
            rag = LightRAGPlugin._get_rag_instance(storage_path)
            
            # 使用LightRAG进行查询
            result = asyncio.run(rag.aquery(
                query=query,
                param=QueryParam(mode="hybrid")  # 混合检索模式
            ))
            
            # 解析结果并构建RetrievalResult列表
            results = []
            if result:
                # 这里需要根据LightRAG的实际返回格式进行解析
                # 先返回简单格式，后续可以优化
                results.append(RetrievalResult(
                    content=result[:500] if len(result) > 500 else result,
                    relevance=0.9,  # 默认相关度，可以改进
                    turn=0,  # 从实际数据中提取
                    timestamp=datetime.now().isoformat(),
                    metadata={"source": "lightrag_query"}
                ))
            
            return results[:limit]
            
        except Exception as e:
            print(f"Error querying relevant data: {e}")
            return []
    
    @staticmethod  
    def get_recent_context(storage_path: str, turns: int = 5) -> str:
        """获取最近N轮的上下文摘要"""
        try:
            metadata_file = os.path.join(storage_path, "turn_metadata.jsonl")
            
            if not os.path.exists(metadata_file):
                return "暂无历史记录"
            
            # 读取最近的N轮记录
            recent_turns = []
            with open(metadata_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-turns:]:
                    recent_turns.append(json.loads(line.strip()))
            
            # 构建上下文摘要
            context_parts = []
            for turn in recent_turns:
                context_parts.append(f"回合{turn['turn']}: {turn['user_input']} -> {turn['ai_response'][:100]}...")
            
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
                "rag_type": "lightrag",
                "version": "1.0.0"
            }
            
            info_file = os.path.join(storage_path, "session_info.json")
            with open(info_file, "w", encoding="utf-8") as f:
                json.dump(session_info, f, indent=2, ensure_ascii=False)
            
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
            
            # 统计回合数
            metadata_file = os.path.join(storage_path, "turn_metadata.jsonl")
            if os.path.exists(metadata_file):
                with open(metadata_file, "r", encoding="utf-8") as f:
                    stats["total_turns"] = len(f.readlines())
                stats["last_updated"] = datetime.fromtimestamp(
                    os.path.getmtime(metadata_file)
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


# 自动注册插件
if LIGHTRAG_AVAILABLE:
    from . import PluginRegistry
    PluginRegistry.register("memory", LightRAGPlugin)