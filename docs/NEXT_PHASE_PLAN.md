# 下一阶段开发计划

## 当前状态
- **版本**: v1.2.0 (准备阶段)
- **最后更新**: 2025-09-12
- **已完成**: 状态管理接口设计、执行引擎扩展性、可填充数据框架

## 核心架构改进

### 新增文本生成与状态解析流程
```
用户输入 → 意图识别 → 执行引擎 → 状态变更 → 文本生成模块 → 双重输出
                                                    ↓
                                              用户显示 + 状态解析
                                                    ↓
                                              动态内容生成 (可选)
```

## 高优先级任务 (本阶段完成)

### 1. 集成现有系统 🔴
- **目标**: 将新的状态管理器集成到现有执行引擎
- **文件**: `Agent/core/execution_engine.py`
- **内容**: 
  - 使用 `FillableStateManager` 替代现有状态变更逻辑
  - 集成 `StateTransactionManager` 实现事务性状态变更
  - 更新所有Function类使用新的状态管理接口

### 2. 实现动态内容生成Function 🔴  
- **目标**: AI生成内容后能够更新游戏数据框架
- **文件**: `Agent/implementations/content_generation_functions.py`
- **内容**:
  - `ContentGenerationFunction` 基类
  - `LocationGenerationFunction` - 生成新城市/位置
  - `NPCGenerationFunction` - 生成新NPC
  - `ItemGenerationFunction` - 生成新物品
  - 内容验证和质量控制机制

### 3. 创建文本生成模块 🔴
- **目标**: 独立的LM Studio文本生成服务
- **文件**: `Agent/ai/text_generator.py`
- **功能**:
  - 连接LM Studio端点
  - 接收执行结果和状态变更
  - 生成用户友好的文字描述
  - 非格式化prompt，自然语言交互

### 4. 实现文本解析状态变更功能 🔴
- **目标**: 解析AI生成的文本，提取隐含的状态变更
- **文件**: `Agent/ai/response_parser.py` 
- **功能**:
  - 解析文本中的地图添加指令
  - 识别物品获取描述
  - 检测环境变化暗示
  - 触发对应的ContentGenerationFunction

### 5. 完整系统测试验证 🔴
- **目标**: 验证新架构的完整流程
- **工具**: 扩展 `testing/runner.py`
- **测试场景**:
  - 状态变更→文本生成→解析→动态内容生成
  - 事务性状态管理
  - 错误处理和回滚

## 中优先级任务 (下一阶段)

### 6. 状态持久化 🟡
- 将状态变更保存到文件/数据库
- 支持游戏存档和读档

### 7. 内容生成模板 🟡
- 为不同类型内容创建生成模板
- 保证AI生成内容的一致性和质量

### 8. 回滚机制完善 🟡
- 完善StateTransactionManager的回滚逻辑
- 支持复杂状态变更的撤销

## 技术实现细节

### 文本生成模块架构
```python
class TextGenerator:
    def generate_response(self, execution_result, state_changes) -> TextResponse
    def connect_lm_studio(self, endpoint) -> bool
    def format_context(self, game_state, changes) -> str

class ResponseParser:
    def parse_for_state_changes(self, text) -> List[StateChangeIntent]
    def extract_content_generation_requests(self, text) -> List[ContentRequest]
```

### 集成点
1. **执行引擎**: 执行完成后调用文本生成
2. **响应处理**: 解析文本后触发动态内容生成
3. **状态管理**: 所有变更通过统一接口处理

## 成功指标
- [ ] 状态变更能触发自然文本描述
- [ ] AI生成文本能被解析为状态变更
- [ ] 动态生成的内容能正确集成到游戏世界
- [ ] 完整流程的端到端测试通过
- [ ] 错误处理和回滚机制正常工作

## 风险点
1. **文本解析准确性**: AI生成文本的解析可能不稳定
2. **状态一致性**: 动态生成内容可能导致状态冲突  
3. **性能影响**: 双重AI调用可能影响响应速度

## 下一阶段预览
- Web界面开发
- 多模型分工优化
- 玩家自定义内容系统