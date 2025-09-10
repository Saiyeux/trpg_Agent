# AI-TRPG 开发进度

## 当前状态
- **版本**: v1.1.0 (with RAG)
- **最后更新**: 2025-09-10

## 项目结构
```
trpg_Agent/
├── main.py              # 入口
├── Agent/               # 核心系统
│   ├── core/            # 游戏引擎
│   ├── plugins/         # 内存插件 (RAG)
│   ├── api/             # 对话API
│   └── utils/           # 工具模块
├── storage/             # 数据存储
└── tools/               # 测试工具
```

## 快速启动
```bash
python main.py           # 运行游戏
python main.py --debug   # 调试模式
ls logs/                 # 查看日志
```

## 待办事项

### 🔴 高优先级
- [ ] 修复AI回避结果问题 (`Agent/plugins/lightrag_plugin.py`)
- [ ] 优化RAG检索准确率
- [ ] 测试API存储集成

### 🟡 中优先级  
- [ ] 完善对话API (`Agent/api/conversation_api.py`)
- [ ] 添加存储性能监控
- [ ] 改进意图分析准确率

### 🟢 低优先级
- [ ] 多模型分工架构
- [ ] Web界面开发
- [ ] 多语言支持

## 关键文件
- `Agent/plugins/lightrag_plugin.py` - RAG内存插件
- `Agent/plugins/api_memory_plugin.py` - API存储插件  
- `Agent/core/game_engine.py` - 游戏引擎
- `Agent/api/conversation_api.py` - 对话API

## 问题定位
```bash
tail -50 logs/trpg_game_*.log  # 查看日志
python main.py --debug         # 调试模式
```