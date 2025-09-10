# 意图识别层设计

## 模型配置
- **模型**: qwen2.5:3b (快速轻量)
- **职责**: 分析玩家意图并分类
- **输入**: 用户文本 + 当前场景
- **输出**: 标准Intent对象

## 意图分类

### 四大类型
1. **执行动作类**: 攻击/使用/拾取等动作动词
2. **查询类**: 询问/查看/调查等查询动词  
3. **探索对话类**: 移动/对话/去往等交互动词
4. **推理想象类**: 创新性行为，脱离基本规则

## 数据结构

```python
class Intent:
    type: str           # "执行"/"查询"/"探索"/"推理"
    category: str       # "攻击"/"使用技能"/"移动"等
    action: str         # 具体行动描述
    target: str         # 目标对象
    parameters: dict    # 额外参数
    confidence: float   # 识别置信度
```

## 实现要点
- JSON格式输出，包含Markdown代码块解析
- 支持新概念识别并标记
- 容错处理：解析失败时返回默认结构
- 集成现有IntentAnalyzer的统计功能

## 扩展接口
```python
class IntentClassifier:
    def classify(self, user_input: str, context: str) -> Intent
    def register_category(self, category: str, keywords: List[str])
    def get_confidence_threshold(self) -> float
```