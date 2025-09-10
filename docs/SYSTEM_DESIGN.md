# 系统架构文档

## 核心架构

```
trpg_Agent/
├── main.py                      # 入口点
├── Agent/                       # 核心系统
│   ├── core/
│   │   ├── game_engine.py       # 游戏引擎 - 主控制器
│   │   └── game_state.py        # 状态管理 - 游戏状态
│   ├── plugins/                 # 内存插件系统
│   │   ├── lightrag_plugin.py   # RAG内存插件 (主力)
│   │   ├── api_memory_plugin.py # API存储插件
│   │   └── simple_memory_plugin.py # 简单内存插件
│   ├── api/
│   │   └── conversation_api.py   # 对话API接口
│   └── utils/
│       ├── intent_analyzer.py    # 意图分析
│       ├── action_dispatcher.py  # 行动分发
│       └── logger.py            # 日志记录
├── storage/                     # 数据存储
│   ├── conversations/           # 对话数据
│   ├── lightrag_storage/        # RAG数据库
│   └── api_conversations/       # API对话数据
└── tools/                       # 测试和工具
    └── test/                    # 测试脚本
```

## 数据流

### 游戏主循环
```
用户输入 → 意图分析 → RAG检索 → 场景生成 → 状态更新 → 显示结果
```

### RAG内存系统
```
对话历史 → 向量化 → 存储 → 检索 → 上下文增强 → AI生成
```

## 关键组件

### 1. 游戏引擎 (`Agent/core/game_engine.py`)
- 主控制循环
- AI模型调用协调
- 插件系统管理

### 2. RAG插件 (`Agent/plugins/lightrag_plugin.py`)  
- LightRAG集成
- 向量存储和检索
- 上下文增强

### 3. 对话API (`Agent/api/conversation_api.py`)
- RESTful API接口
- 对话数据管理
- 外部系统集成

## 配置系统

### 主配置 (`config/settings.py`)
```python
AI_CONFIG = {
    "type": "ollama",           # AI后端类型
    "model": "qwen2.5:3b",      # 模型名称
    "context_limit": 32000      # 上下文限制
}

MEMORY_CONFIG = {
    "type": "lightrag",         # 内存插件类型
    "storage_path": "storage/lightrag_storage"
}
```

## 当前问题

### 1. AI结果回避 (高优先级)
**位置**: `Agent/plugins/lightrag_plugin.py:80-109`
**问题**: 场景生成AI不给出具体行动结果
**原因**: Prompt设计缺陷，缺少执行结果概念

### 2. RAG检索准确率 (中优先级)  
**位置**: `Agent/plugins/lightrag_plugin.py`
**问题**: 检索相关性需要提升
**原因**: 嵌入模型和检索算法需要优化

## 技术栈

### 当前技术栈
- **Python**: 3.8+
- **AI后端**: Ollama/LM Studio  
- **RAG**: LightRAG
- **存储**: 本地文件系统
- **API**: FastAPI

### 依赖管理
```bash
# 核心依赖
pip install -r requirements.txt

# 测试和开发
pip install pytest pytest-asyncio
```

## 扩展计划

### v1.1.1 (当前)
- 修复AI结果回避问题
- 优化RAG检索准确率
- 稳定API存储功能

### v1.2.0 (下个版本)
- 完整Web API接口
- 性能监控系统  
- 多模型分工架构

---
*最后更新: 2025-09-10*