# 执行引擎层设计

## 核心职责
- RAG检索匹配的Functions
- 执行Function并修改GameState
- 生成ExecutionResult

## 四大执行引擎

### 1. 动作执行引擎 (ExecutionEngine)
```
Intent → RAG检索Functions → 条件检查 → 执行Function → 状态修改 → ExecutionResult
```

### 2. 查询引擎 (QueryEngine)  
- 难度判断系统 (5-25难度值)
- 检定系统 (d20 + 修正值)
- 环境和状态影响计算

### 3. 探索引擎 (ExplorationEngine)
- 状态查询和上下文检索  
- 对话和移动处理
- 环境交互逻辑

### 4. 创意引擎 (CreativeEngine)
- 可行性分析
- 动态概念创建
- 创新行为处理

## 核心数据结构

```python
class ExecutionResult:
    success: bool
    action_taken: str
    state_changes: List[StateChange] 
    world_changes: List[str]
    dice_results: List[DiceRoll]
    new_concepts: List[Concept]
    
class StateChange:
    target: str         # player/world/npc
    action: str         # add/remove/modify
    property: str       # 属性名
    value: any          # 新值
```

## Function库架构

```python
@register_function(category="攻击", targets=["敌人"])
class AttackFunction(GameFunction):
    def can_execute(self, intent: Intent, state: GameState) -> bool
    def execute(self, intent: Intent, state: GameState) -> ExecutionResult
    def get_priority(self) -> int
```

## 扩展接口
- 支持运行时注册新Function
- 插件化的引擎扩展机制
- 可配置的优先级和条件系统