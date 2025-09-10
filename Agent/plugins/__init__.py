"""
插件实现模块

提供各种功能接口的具体实现，支持插件化架构。
实现可插拔的功能扩展，便于添加新的AI后端和存储方案。

主要插件:
- LightRAG记忆插件
- 执行模块插件（预留）
"""

__version__ = "1.0.0"

# 插件注册中心
class PluginRegistry:
    """插件注册中心"""
    _plugins = {}
    
    @classmethod
    def register(cls, interface_name: str, plugin_class):
        """注册插件实现"""
        cls._plugins[interface_name] = plugin_class
        
    @classmethod  
    def get_plugin(cls, interface_name: str):
        """获取插件实例"""
        return cls._plugins.get(interface_name)
    
    @classmethod
    def list_plugins(cls):
        """列出所有已注册的插件"""
        return list(cls._plugins.keys())

__all__ = [
    'PluginRegistry'
]