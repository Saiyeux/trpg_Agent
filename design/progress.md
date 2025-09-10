# TRPG多模型分工系统开发进度

## ⚡ 关键认知：高耦合系统的开发策略

**核心问题**: 模块间高度耦合，单独开发任何一个模块都无法验证  
**解决方案**: 垂直切片 + Mock隔离 + 渐进集成

## 开发策略总览

### 阶段式开发路径
```
Phase 0: 接口定义     → Phase 1: 垂直MVP    → Phase 2: 水平扩展   → Phase 3: 智能优化
  (1周)                  (2周)              (2-3周)           (2-3周)
全接口定义完成          单个功能端到端        多功能支持          RAG/AI优化
```

### 验证策略层次
```
Level 1: Mock全部依赖  → Level 2: 真实执行引擎 → Level 3: 真实状态 → Level 4: 全集成
接口兼容性验证           执行逻辑验证          状态管理验证        端到端验证
```

---

## Phase 0: 接口定义阶段 (1周) ✋ **当前阶段**

### 目标
消除模块间接口不确定性，建立稳固的开发基础

### 核心任务
```python
# 1. 核心数据结构定义
class Intent:
    type: str           # "执行"/"查询"/"探索"/"推理" 
    category: str       # "攻击"/"搜索"等具体分类
    action: str         # 用户行动描述
    target: str         # 目标对象
    parameters: dict    # 扩展参数

class ExecutionResult:
    success: bool               # 执行是否成功
    action_taken: str          # 具体执行的行动
    state_changes: List[StateChange]  # 状态变更列表
    dice_results: List[DiceRoll]      # 骰子结果
    failure_reason: str        # 失败原因(如果失败)

class StateChange:
    target: str         # 变更目标: "player"/"world"/"npc_name"
    action: str         # 操作类型: "add"/"remove"/"modify"
    property: str       # 属性名: "hp"/"items"/"location"
    value: Any         # 新值或变化量
```

### Mock框架建设
```python
# tools/mocks/ 目录结构
├── mock_game_state.py       # GameState Mock实现
├── mock_rag_retriever.py    # RAG检索 Mock实现  
├── mock_scene_generator.py  # 场景生成 Mock实现
└── integration_levels.py    # 4级集成测试定义
```

### 验证标准
- [ ] 所有接口定义编译通过
- [ ] Mock框架能够模拟完整数据流
- [ ] Level 1集成测试(全Mock)通过

---

## Phase 1: 垂直MVP切片 (2周)

### 目标  
实现单一功能的完整端到端流程 - "攻击哥布林"

### 实现范围
```
用户: "我攻击哥布林"
  ↓ IntentClassifier (仅支持攻击识别)
Intent{type:"执行", category:"攻击", target:"哥布林"}  
  ↓ ExecutionEngine + AttackFunction (硬编码匹配)
ExecutionResult{success:true, action_taken:"攻击哥布林造成5点伤害", state_changes:[...]}
  ↓ GameState (仅HP管理)
哥布林HP: 15→10
  ↓ SceneGenerator (基于ExecutionResult模板)
"你挥剑击中了哥布林，造成5点伤害。哥布林痛苦地咆哮着，还剩10点生命值。"
```

### 关键组件最小实现
- **IntentClassifier**: 仅识别"攻击"关键词
- **AttackFunction**: 基础伤害计算(1d6+力量调整)
- **GameState**: 仅角色HP和存活状态
- **SceneGenerator**: 基于ExecutionResult的模板生成

### 验证标准
- [ ] Level 2集成测试通过(真实ExecutionEngine)
- [ ] 端到端攻击流程完整执行
- [ ] AI回避问题得到解决(给出具体伤害数值)

---

## Phase 2: 水平扩展 (2-3周)

### 目标
扩展到5个核心Function，覆盖主要游戏机制

### 新增Function
1. **SearchFunction** - 搜索调查物品/环境
2. **UseItemFunction** - 使用背包中的物品  
3. **MoveFunction** - 角色位置移动
4. **StatusFunction** - 查看角色/世界状态
5. **RestFunction** - 休息恢复

### 扩展GameState
```python
class PlayerState:
    hp: int, max_hp: int
    mp: int, max_mp: int  
    attributes: Dict[str, int]  # 六大属性
    inventory: List[Item]       # 背包系统
    location: str              # 当前位置

class WorldState:
    locations: Dict[str, Location]  # 地图系统
    npcs: Dict[str, NPC]           # NPC状态
    items: Dict[str, List[Item]]   # 环境物品
```

### 验证标准
- [ ] Level 3集成测试通过(真实State管理)
- [ ] 5种Function都能正确执行和给出结果
- [ ] 状态变更能正确持久化

---

## Phase 3: 状态系统完善 (2周)

### 目标
完整的角色系统、装备系统、状态效果系统

### 扩展内容
- 装备系统(武器/防具/饰品槽位)
- 状态效果(中毒/魅惑/加速等)
- 技能系统(主动/被动技能)
- 地图系统(连通性/隐藏区域)

### 验证标准
- [ ] 复杂状态交互正确处理
- [ ] 装备影响战斗计算
- [ ] 状态效果正确叠加和消除

---

## Phase 4: RAG智能化 (2-3周)

### 目标
从硬编码Function匹配升级到智能检索

### 核心升级
- 向量化Function库和历史执行记录
- 语义相似度检索算法
- 动态优先级调整和学习机制
- 新Function的自动注册和分类

### 验证标准
- [ ] Level 4全集成测试通过
- [ ] RAG检索准确率>85%
- [ ] 支持动态Function扩展

---

## 关键风险控制

### 🚨 依赖关系风险
**风险**: Intent设计错误导致后续所有模块重构  
**控制**: Phase 0充分的接口设计和Review

### 🚨 集成复杂度风险  
**风险**: 多个模块同时有bug时难以定位  
**控制**: 渐进式集成，每次只增加一个真实模块

### 🚨 性能风险
**风险**: 复杂状态管理导致响应延迟  
**控制**: 每个Phase都要做性能基准测试

---

## 验证工具集

### 测试分类
```bash
# 接口兼容性测试
python tools/test_interfaces.py

# 单功能端到端测试  
python tools/test_e2e_attack.py

# 多功能集成测试
python tools/test_multi_functions.py

# 性能基准测试
python tools/benchmark_execution.py

# 回避问题专项测试
python tools/test_concrete_responses.py
```

### CI/CD流程
每个Phase完成后必须通过：
1. 单元测试套件(90%+覆盖率)
2. 对应Level的集成测试  
3. 性能基准不退化
4. AI回避问题测试通过

---

**当前状态**: Phase 0 - 接口定义阶段  
**下一步**: 定义Intent/ExecutionResult/StateChange核心数据结构  
**关键成功指标**: 消除所有模块间的接口不确定性