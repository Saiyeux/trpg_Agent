# 状态管理系统设计

## 核心状态结构

### GameState
```python
class GameState:
    player: PlayerState         # 玩家状态
    world: WorldState          # 世界状态  
    concepts: ConceptRegistry  # 动态概念库
    history: List[GameEvent]   # 历史记录
    turn_count: int           # 回合计数
```

### PlayerState  
```python
class PlayerState:
    # 基础属性 (D&D风格)
    attributes: Dict[str, int]  # 力量/敏捷/体质/智力/感知/魅力
    
    # 数值状态
    hp: int                    # 生命值
    mp: int                    # 法力值
    ac: int                    # 护甲等级
    
    # 动态效果
    effects: List[StatusEffect] # 魅惑/着火/隐身等
    
    # 物品系统
    inventory: Inventory       # 背包
    equipment: Equipment       # 装备
    
    # 技能系统
    skills: List[Skill]        # 已学技能
    abilities: List[Ability]   # 特殊能力
```

### WorldState
```python
class WorldState:
    current_location: Location
    locations: Dict[str, Location]  # 地图系统
    npcs: Dict[str, NPC]           # NPC状态
    global_flags: Dict[str, bool]  # 全局标志
    environment: Environment       # 环境状态
```

## 动态概念系统

```python
class ConceptRegistry:
    def create_concept(self, type: str, name: str, 
                      description: str, properties: dict) -> Concept
    def query_concept(self, name: str) -> Optional[Concept] 
    def update_concept(self, name: str, properties: dict)
    def delete_concept(self, name: str)
```

### 概念类型
- **技能**: 动态创建的技能和法术
- **状态效果**: 临时或永久的角色状态
- **物品**: 运行时生成的装备和道具
- **地点**: 新发现的地图位置
- **规则**: 临时的游戏机制

## 状态同步机制

### 原子操作
```python
class StateTransaction:
    def begin_transaction()
    def add_change(change: StateChange)
    def commit() -> bool
    def rollback()
```

### 持久化策略
- 实时保存关键状态变更
- 定期完整状态快照
- 支持状态回滚和版本管理

## 扩展接口
- 插件化的状态扩展机制
- 可配置的持久化策略
- 状态变更事件监听系统