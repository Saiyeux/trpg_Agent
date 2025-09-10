# 模型间信息传递协议

## 通信架构

### ModelBridge
```python
class ModelBridge:
    def __init__(self):
        self.intent_model = IntentModel()      # Layer 1
        self.execution_engine = ExecutionEngine() # Layer 2  
        self.scene_model = SceneModel()        # Layer 3
        
    def process_turn(self, user_input: str) -> str:
        # 1. 意图识别
        intent = self.intent_model.classify(user_input)
        
        # 2. 执行引擎处理
        result = self.execution_engine.process(intent)
        
        # 3. 场景生成
        response = self.scene_model.generate(result)
        
        return response
```

## 数据传递格式

### Layer 1 → Layer 2
```python
class IntentMessage:
    intent: Intent
    confidence: float
    raw_input: str
    context: Dict[str, Any]
```

### Layer 2 → Layer 3  
```python
class ExecutionMessage:
    execution_result: ExecutionResult
    original_intent: Intent
    state_snapshot: GameState
    rag_context: str
```

### 错误处理协议
```python
class ErrorMessage:
    layer: str              # 出错层级
    error_type: str         # 错误类型
    message: str           # 错误描述  
    fallback_data: Any     # 降级数据
```

## 上下文管理

### ContextManager
```python
class ContextManager:
    def build_context(self, intent: Intent, state: GameState) -> Context:
        return Context(
            current_scene=state.current_scene,
            recent_history=state.get_recent_history(5),
            player_state=state.player.to_dict(),
            world_state=state.world.get_relevant_info(),
            rag_memory=self.query_rag_memory(intent)
        )
```

## Prompt模板系统

### 意图识别Prompt
```python
INTENT_PROMPT = """
分析玩家行动并输出JSON格式结果:
玩家输入: {user_input}
当前场景: {current_scene}

输出格式:
{
  "type": "执行/查询/探索/推理",
  "category": "具体分类",
  "action": "行动描述", 
  "target": "目标对象",
  "parameters": {}
}
"""
```

### 场景生成Prompt
```python
SCENE_PROMPT = """
你是TRPG的城主(DM)，根据执行结果生成回复:

历史上下文: {history}
玩家行动: {player_action}
执行结果: {execution_result}
当前状态: {game_state}

要求:
1. 基于执行结果给出具体回复
2. 回答玩家的具体问题 
3. 保持故事连贯性
4. 描述状态变化
"""
```

## 性能优化

### 异步处理
```python
class AsyncModelBridge:
    async def process_turn_async(self, user_input: str) -> str:
        # 并行处理可并行的部分
        intent_task = asyncio.create_task(
            self.intent_model.classify_async(user_input)
        )
        context_task = asyncio.create_task(
            self.context_manager.build_context_async()
        )
        
        intent, context = await asyncio.gather(intent_task, context_task)
        # ... 继续串行处理
```

### 缓存策略
- 意图分类结果缓存
- 频繁查询的状态缓存  
- 生成结果的部分复用

## 扩展接口
- 可插拔的模型实现
- 自定义Prompt模板
- 灵活的上下文构建策略