"""
对话历史API接口

提供对话历史的RESTful API接口，供前端页面和客户端应用调用。
支持历史查看、搜索、分页和多格式导出功能。

API端点:
- GET /api/conversations/history - 获取分页历史记录
- GET /api/conversations/search - 搜索对话记录
- GET /api/conversations/export - 导出对话记录
- GET /api/sessions - 获取会话列表
- GET /api/sessions/{session_id}/stats - 获取会话统计
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import json


class ConversationAPI:
    """
    对话历史API服务类
    
    提供前端所需的所有对话历史相关API功能。
    基于ApiMemoryPlugin实现，确保数据一致性。
    """
    
    def __init__(self, storage_base_path: str = "storage/conversations"):
        """
        初始化API服务
        
        Args:
            storage_base_path: 对话存储的根路径
        """
        self.storage_base_path = storage_base_path
    
    # === 历史对话显示API ===
    
    def get_conversation_history(
        self, 
        session_id: str, 
        page: int = 1, 
        page_size: int = 20, 
        order: str = "desc"
    ) -> Dict[str, Any]:
        """
        获取对话历史记录（分页）
        
        Args:
            session_id: 会话ID
            page: 页码（从1开始）
            page_size: 每页记录数
            order: 排序方式 ("desc"=最新在前, "asc"=最旧在前)
            
        Returns:
            API响应格式:
            {
                "success": True,
                "data": {
                    "conversations": [
                        {
                            "id": "turn_001_abc123",
                            "turn": 1,
                            "timestamp": "2025-09-10T15:54:11",
                            "player": "艾莉",
                            "scene": "神秘洞穴入口",
                            "user_input": "你好，我想探索这个神秘的洞穴",
                            "ai_response": "你看到一个阴暗的洞口...",
                            "keywords": ["洞穴", "探索", "神秘"]
                        }
                    ],
                    "pagination": {
                        "page": 1,
                        "page_size": 20,
                        "total": 42,
                        "total_pages": 3
                    }
                }
            }
        """
        try:
            from ..plugins.api_memory_plugin import ApiMemoryPlugin
            
            session_path = os.path.join(self.storage_base_path, session_id)
            if not ApiMemoryPlugin.storage_exists(session_path):
                return {
                    "success": False,
                    "error": "Session not found",
                    "code": "SESSION_NOT_FOUND"
                }
            
            result = ApiMemoryPlugin.get_conversation_history(
                session_path, 
                page=page, 
                page_size=page_size, 
                reverse=(order == "desc")
            )
            
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"],
                    "code": "QUERY_ERROR"
                }
            
            return {
                "success": True,
                "data": {
                    "conversations": result["conversations"],
                    "pagination": {
                        "page": result["page"],
                        "page_size": result["page_size"],
                        "total": result["total"],
                        "total_pages": result["total_pages"]
                    }
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code": "INTERNAL_ERROR"
            }
    
    def search_conversations(
        self, 
        session_id: str, 
        keyword: str, 
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        搜索对话记录
        
        Args:
            session_id: 会话ID
            keyword: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            API响应格式:
            {
                "success": True,
                "data": {
                    "matches": [...],
                    "total": 5,
                    "keyword": "洞穴",
                    "search_time": "2025-09-10T16:00:00"
                }
            }
        """
        try:
            from ..plugins.api_memory_plugin import ApiMemoryPlugin
            
            session_path = os.path.join(self.storage_base_path, session_id)
            if not ApiMemoryPlugin.storage_exists(session_path):
                return {
                    "success": False,
                    "error": "Session not found",
                    "code": "SESSION_NOT_FOUND"
                }
            
            matches = ApiMemoryPlugin.search_conversations(
                session_path, 
                keyword, 
                limit=limit
            )
            
            return {
                "success": True,
                "data": {
                    "matches": matches,
                    "total": len(matches),
                    "keyword": keyword,
                    "search_time": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code": "SEARCH_ERROR"
            }
    
    # === TXT导出API ===
    
    def export_conversation(
        self, 
        session_id: str, 
        format_type: str = "readable",
        download: bool = False
    ) -> Dict[str, Any]:
        """
        导出对话记录
        
        Args:
            session_id: 会话ID
            format_type: 导出格式 ("readable", "compact", "markdown", "json")
            download: 是否作为文件下载
            
        Returns:
            API响应格式:
            {
                "success": True,
                "data": {
                    "content": "# TRPG对话记录\\n...",
                    "format": "readable",
                    "filename": "trpg_session_20250910.txt",
                    "size": 1024
                }
            }
        """
        try:
            from ..plugins.api_memory_plugin import ApiMemoryPlugin
            
            session_path = os.path.join(self.storage_base_path, session_id)
            if not ApiMemoryPlugin.storage_exists(session_path):
                return {
                    "success": False,
                    "error": "Session not found",
                    "code": "SESSION_NOT_FOUND"
                }
            
            # 根据格式类型导出
            if format_type == "json":
                content = self._export_json(session_path)
                file_ext = "json"
            else:
                content = ApiMemoryPlugin.export_to_txt(session_path, format_type)
                file_ext = "md" if format_type == "markdown" else "txt"
            
            # 生成文件名
            session_info = ApiMemoryPlugin.get_storage_stats(session_path)
            player_name = session_info.get("player_name", "player")
            created_date = session_info.get("created_at", "")[:10]
            filename = f"trpg_{player_name}_{created_date}_{session_id}.{file_ext}"
            
            response_data = {
                "content": content,
                "format": format_type,
                "filename": filename,
                "size": len(content.encode('utf-8'))
            }
            
            # 如果是下载模式，添加下载相关信息
            if download:
                response_data["download"] = True
                response_data["mime_type"] = self._get_mime_type(file_ext)
            
            return {
                "success": True,
                "data": response_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code": "EXPORT_ERROR"
            }
    
    # === 会话管理API ===
    
    def list_sessions(self) -> Dict[str, Any]:
        """
        获取所有会话列表
        
        Returns:
            API响应格式:
            {
                "success": True,
                "data": {
                    "sessions": [
                        {
                            "session_id": "trpg_20250910_154311",
                            "player_name": "艾莉",
                            "created_at": "2025-09-10T15:43:11",
                            "last_updated": "2025-09-10T16:30:45",
                            "total_turns": 25,
                            "storage_size": 15360
                        }
                    ],
                    "total": 1
                }
            }
        """
        try:
            sessions = []
            
            if os.path.exists(self.storage_base_path):
                for item in os.listdir(self.storage_base_path):
                    session_path = os.path.join(self.storage_base_path, item)
                    if os.path.isdir(session_path):
                        from ..plugins.api_memory_plugin import ApiMemoryPlugin
                        
                        if ApiMemoryPlugin.storage_exists(session_path):
                            stats = ApiMemoryPlugin.get_storage_stats(session_path)
                            if "error" not in stats:
                                sessions.append({
                                    "session_id": item,
                                    **stats
                                })
            
            # 按最后更新时间排序
            sessions.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
            
            return {
                "success": True,
                "data": {
                    "sessions": sessions,
                    "total": len(sessions)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code": "LIST_ERROR"
            }
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话详细统计信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            API响应格式:
            {
                "success": True,
                "data": {
                    "session_id": "trpg_20250910_154311",
                    "basic_info": {...},
                    "statistics": {
                        "total_turns": 25,
                        "avg_response_length": 156,
                        "most_common_keywords": ["洞穴", "宝藏", "冒险"],
                        "scenes_count": 8
                    }
                }
            }
        """
        try:
            from ..plugins.api_memory_plugin import ApiMemoryPlugin
            
            session_path = os.path.join(self.storage_base_path, session_id)
            if not ApiMemoryPlugin.storage_exists(session_path):
                return {
                    "success": False,
                    "error": "Session not found",
                    "code": "SESSION_NOT_FOUND"
                }
            
            # 获取基础统计
            basic_stats = ApiMemoryPlugin.get_storage_stats(session_path)
            
            # 计算详细统计
            detailed_stats = self._calculate_detailed_stats(session_path)
            
            return {
                "success": True,
                "data": {
                    "session_id": session_id,
                    "basic_info": basic_stats,
                    "statistics": detailed_stats
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code": "STATS_ERROR"
            }
    
    # === 私有方法 ===
    
    def _export_json(self, session_path: str) -> str:
        """导出为JSON格式"""
        conversation_file = os.path.join(session_path, "conversation.jsonl")
        conversations = []
        
        if os.path.exists(conversation_file):
            with open(conversation_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        conversations.append(json.loads(line.strip()))
        
        from ..plugins.api_memory_plugin import ApiMemoryPlugin
        session_info = ApiMemoryPlugin.get_storage_stats(session_path)
        
        export_data = {
            "session_info": session_info,
            "conversations": conversations,
            "exported_at": datetime.now().isoformat()
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def _get_mime_type(self, file_ext: str) -> str:
        """获取文件MIME类型"""
        mime_types = {
            "txt": "text/plain",
            "md": "text/markdown",
            "json": "application/json"
        }
        return mime_types.get(file_ext, "text/plain")
    
    def _calculate_detailed_stats(self, session_path: str) -> Dict[str, Any]:
        """计算详细统计信息"""
        try:
            conversation_file = os.path.join(session_path, "conversation.jsonl")
            if not os.path.exists(conversation_file):
                return {}
            
            total_turns = 0
            total_input_length = 0
            total_response_length = 0
            all_keywords = []
            unique_scenes = set()
            
            with open(conversation_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line.strip())
                        total_turns += 1
                        total_input_length += len(record.get("user_input", ""))
                        total_response_length += len(record.get("ai_response", ""))
                        all_keywords.extend(record.get("keywords", []))
                        unique_scenes.add(record.get("scene", ""))
            
            # 计算统计数据
            from collections import Counter
            keyword_counter = Counter(all_keywords)
            
            return {
                "total_turns": total_turns,
                "avg_input_length": total_input_length // max(total_turns, 1),
                "avg_response_length": total_response_length // max(total_turns, 1),
                "most_common_keywords": [kw for kw, count in keyword_counter.most_common(10)],
                "scenes_count": len(unique_scenes),
                "unique_scenes": list(unique_scenes)
            }
            
        except Exception:
            return {}


# === API路由示例 ===

def setup_conversation_routes(app, api_instance: ConversationAPI):
    """
    设置Flask/FastAPI路由示例
    
    使用示例:
    api = ConversationAPI()
    setup_conversation_routes(flask_app, api)
    """
    
    # Flask路由示例
    @app.route('/api/conversations/history/<session_id>')
    def get_history(session_id):
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        order = request.args.get('order', 'desc')
        
        return api_instance.get_conversation_history(session_id, page, page_size, order)
    
    @app.route('/api/conversations/search/<session_id>')
    def search(session_id):
        keyword = request.args.get('keyword', '')
        limit = int(request.args.get('limit', 10))
        
        return api_instance.search_conversations(session_id, keyword, limit)
    
    @app.route('/api/conversations/export/<session_id>')
    def export(session_id):
        format_type = request.args.get('format', 'readable')
        download = request.args.get('download', 'false').lower() == 'true'
        
        return api_instance.export_conversation(session_id, format_type, download)
    
    @app.route('/api/sessions')
    def list_sessions():
        return api_instance.list_sessions()
    
    @app.route('/api/sessions/<session_id>/stats')
    def session_stats(session_id):
        return api_instance.get_session_stats(session_id)