# TRPG-Agent

基于大语言模型的桌游角色扮演游戏系统。支持智能场景生成、意图识别和多AI后端，为玩家提供沉浸式的TRPG体验。

## ✨ 主要特性

- 🎭 **智能场景生成** - AI驱动的动态场景描述和故事推进
- 🤖 **意图识别系统** - 自动分析玩家行为意图并分类统计
- 📊 **数据统计分析** - 详细的游戏行为分析和趋势报告
- 🔧 **多AI后端支持** - 支持Ollama和LM Studio两种AI服务
- 📝 **详细日志记录** - 完整的游戏过程和AI交互记录
- ⚙️ **灵活配置系统** - 可配置的AI模型和游戏参数

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 运行中的AI服务 (Ollama 或 LM Studio)

### 安装依赖

```bash
pip install requests
```

### 启动游戏

```bash
# 首次使用，配置系统
python main.py config

# 启动游戏
python main.py

# 调试模式
python main.py --debug
```

## 🎮 使用方法

### 基本游戏流程

1. **角色创建** - 输入你的角色名
2. **场景互动** - 描述你想执行的行动
3. **AI响应** - 系统分析意图并生成场景
4. **持续冒险** - 在AI构建的世界中探索

### 游戏命令

游戏中可用的特殊命令：

- `help` / `帮助` - 显示帮助信息
- `stats` / `统计` - 显示意图统计
- `status` / `状态` - 显示游戏状态
- `config` / `配置` - 显示当前配置
- `quit` / `退出` - 退出游戏

### 行动示例

```
你的行动: 探索前方的神秘洞穴
你的行动: 与酒馆老板交谈，询问当地传说
你的行动: 检查背包中的物品
你的行动: 尝试学习新的魔法技能
```

## 🔧 配置说明

### AI后端配置

系统支持两种AI后端：

#### Ollama
- 本地运行的开源AI服务
- 支持多模型切换
- 适合轻量化部署

```json
{
  "api": {"type": "ollama"},
  "ollama": {
    "base_url": "http://localhost:11434/api/generate",
    "model": "qwen2.5:3b",
    "context_limit": 32000
  }
}
```

#### LM Studio
- 图形界面的AI模型管理器
- 支持高质量大模型
- 128K长上下文支持

```json
{
  "api": {"type": "lm_studio"},
  "lm_studio": {
    "base_url": "http://localhost:1234/v1/chat/completions",
    "context_limit": 128000
  }
}
```

### 推荐模型

| 用途 | Ollama推荐 | LM Studio推荐 |
|------|------------|---------------|
| 中文TRPG | qwen2.5:7b | hermes-3-llama-3.1-8b |
| 英文创作 | llama3.1:8b | nous-hermes-2-mixtral-8x7b |
| 长期记忆 | qwen2.5:14b | hermes-3-llama-3.1-70b |

## 📁 项目结构

```
ai_trpg/
├── main.py                 # 主程序入口
├── config/                 # 配置文件目录
│   └── game_config.json    # 主配置文件
├── logs/                   # 日志文件目录
└── ai_trpg/               # 核心包
    ├── core/              # 核心模块
    │   ├── game_engine.py  # 游戏引擎
    │   └── game_state.py   # 状态管理
    ├── ai/                # AI交互模块
    │   └── model_client.py # AI客户端
    ├── utils/             # 工具模块
    │   ├── intent_analyzer.py  # 意图分析
    │   ├── logger.py          # 日志记录
    │   └── action_dispatcher.py # 行动分发
    └── config/            # 配置模块
        └── settings.py     # 配置管理
```

## 📊 功能特性详解

### 意图识别系统

系统能够识别和分类玩家的各种行动意图：

- **探索类** - 探索新区域、调查物品
- **社交类** - 与NPC对话、交易、学习
- **战斗类** - 攻击敌人、使用技能
- **其他类** - 休息、制作、移动等

### 智能上下文管理

根据不同AI模型的能力自动调整历史记录：

- **短上下文模型** (32K) - 保留最近3-5轮对话
- **长上下文模型** (128K) - 保留整场游戏历史

### 详细日志系统

记录完整的游戏过程：

- AI模型的输入输出
- 玩家意图分析结果
- 游戏事件和状态变化
- 会话统计和分析报告

## 🔍 故障排除

### 常见问题

1. **AI服务连接失败**
   ```
   解决方案: 确保Ollama或LM Studio服务正常运行
   检查配置文件中的URL地址是否正确
   ```

2. **模型响应慢**
   ```
   解决方案: 尝试使用更小的模型或减少历史记录数量
   检查系统资源使用情况
   ```

3. **意图识别不准确**
   ```
   解决方案: 尝试更大的模型或调整prompt描述
   查看日志了解具体的AI响应内容
   ```

### 调试模式

使用调试模式获取详细错误信息：

```bash
python main.py --debug
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 🙏 致谢

- 感谢Ollama和LM Studio提供优秀的AI服务
- 感谢所有开源模型的贡献者

---

**开始你的AI-TRPG冒险之旅吧！** 🎲✨