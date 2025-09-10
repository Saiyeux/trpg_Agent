# 🚀 AI-TRPG 快速开发指南

## 📍 当前开发状态

**版本**: v1.0.0 ✅ (已完成)  
**最后更新**: 2025-09-10  
**下一个版本**: v2.0.0 (规划中)

## 🎯 项目结构速览

```
ai_trpg/
├── main.py                    # 入口程序
├── config/game_config.json    # 配置文件
├── logs/                      # 日志文件 (运行时生成)
├── docs/                      # 文档目录
│   ├── SYSTEM_DESIGN.md       # 详细系统设计
│   ├── TODO.md               # 完整开发计划
│   └── QUICK_START.md         # 本文件
└── ai_trpg/                  # 核心包
    ├── core/                 # 游戏引擎
    ├── ai/                   # AI客户端  
    ├── utils/                # 工具模块
    └── config/               # 配置管理
```

## 🔥 立即开始开发

### 启动现有系统
```bash
# 运行游戏测试
python main.py

# 配置系统
python main.py config

# 调试模式
python main.py --debug
```

### 查看日志分析
```bash
# 查看最新日志
ls -la logs/
cat logs/trpg_game_*.log
```

## ⚡ 核心问题识别

### 🚨 需要立即解决的问题

1. **AI回避具体结果问题** (优先级: 🔴 HIGH)
   - **位置**: `ai_trpg/ai/model_client.py:80-109`
   - **问题**: 场景生成AI不给出玩家行动的具体结果
   - **表现**: 玩家问"找到什么"时，AI只描述氛围不给答案
   - **原因**: Prompt设计缺陷，缺少"执行结果"概念

2. **JSON解析偶发失败** (优先级: 🟡 MEDIUM) 
   - **位置**: `ai_trpg/core/game_engine.py:265-306`
   - **状态**: 已修复但需要测试验证
   - **解决方案**: 已添加Markdown代码块解析

## 🎯 下一步开发重点

### Phase 1: 修复核心问题 (预计1-2天)

**即刻开始的任务**:

1. **修复场景生成Prompt** 📝
   ```python
   # 文件: ai_trpg/ai/model_client.py:generate_scene()
   # 当前问题: 缺少行动执行结果
   # 需要修改: 添加明确的"执行玩家行动并给出结果"指令
   ```

2. **改进上下文传递** 🔄
   ```python
   # 文件: ai_trpg/core/game_engine.py:298-328
   # 当前问题: 场景生成时只传递"生成新场景"
   # 需要修改: 传递玩家具体行动和期望结果
   ```

### Phase 2: RAG功能集成 (预计1-2周)

**技术栈选择**:
- 向量数据库: ChromaDB (轻量级，易部署)
- 嵌入模型: sentence-transformers (支持中文)
- 存储方案: 本地文件 + SQLite

**关键文件**:
- 新建: `ai_trpg/rag/vector_store.py`
- 新建: `ai_trpg/rag/retriever.py`
- 修改: `ai_trpg/core/game_engine.py`

### Phase 3: 多模型分工 (预计2-3周)

**模型分工**:
- 意图识别: qwen2.5:3B (快)
- 文本生成: Hermes-4-14B (质量高)
- 执行推理: CodeLlama (逻辑强)

## 🔧 开发环境设置

### 依赖检查
```bash
# 当前依赖
pip list | grep requests

# RAG扩展依赖 (Phase 2需要)
# pip install chromadb sentence-transformers
```

### 配置文件
```bash
# 检查配置
cat config/game_config.json

# 测试不同模型
# 修改 "api.type" 为 "lm_studio" 测试大模型
```

## 🐛 已知问题和解决方案

### ✅ 已修复
- [x] JSON解析Markdown包装问题
- [x] 界面换行符显示问题  
- [x] 日志文件时间戳问题

### ❌ 待修复
- [ ] **AI回避具体结果** - 需要改进Prompt设计
- [ ] **长期记忆限制** - 需要RAG功能
- [ ] **上下文窗口不足** - 需要智能检索

## 📋 开发检查清单

### 开始新开发会话时检查:
```bash
# 1. 确认项目状态
python main.py --help

# 2. 查看最新日志
ls -la logs/ | tail -3

# 3. 检查配置
python main.py --validate-config

# 4. 运行快速测试
python main.py config
```

### 核心文件修改优先级:
1. 🔴 `ai_trpg/ai/model_client.py` - 修复场景生成Prompt
2. 🔴 `ai_trpg/core/game_engine.py` - 改进上下文传递
3. 🟡 添加RAG模块 - 新建`ai_trpg/rag/`目录
4. 🟢 多模型分工 - 扩展`ai_trpg/ai/`模块

## 🎯 成功指标

### v1.1 (修复版)目标:
- [ ] AI能给出玩家行动的具体结果
- [ ] 玩家询问"找到什么"时得到明确答案
- [ ] JSON解析成功率 > 95%

### v2.0 (RAG版)目标:
- [ ] 支持长期记忆 (>100轮对话)
- [ ] 语义检索准确率 > 85%
- [ ] 响应速度 < 3秒

---

## 💡 快速问题定位

**如果遇到问题，按此顺序检查**:
1. 查看最新日志: `tail -50 logs/trpg_game_*.log`
2. 检查配置: `python main.py --validate-config`
3. 测试AI连接: 确保Ollama/LM Studio运行
4. 查看详细错误: `python main.py --debug`

**关键日志位置**:
- AI交互日志: 搜索 `"模型输入"` 和 `"模型输出"`
- 错误日志: 搜索 `"出错"` 和 `"失败"`
- 意图分析: 搜索 `"意图分类: 解析错误"`

---

*快速上手，立即开发！* 🚀