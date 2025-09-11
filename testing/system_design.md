# 引导文档式测试系统架构设计

## 设计理念

根据`docs/routine.md`的要求，重构测试框架为：
**引导文档 → 用户操作 → 记录日志 → 分析日志** 的交互式测试流程

## 系统架构

### 核心组件

```
testing/
├── runner.py              # 🎯 统一测试执行入口
├── guides/                # 📋 测试引导文档
│   ├── intent_classification.md
│   ├── execution_engine.md  
│   ├── scene_generation.md
│   ├── dynamic_content.md
│   └── full_integration.md
├── logs/                  # 📊 测试日志存储
│   ├── YYYYMMDD_HHMMSS/   # 按时间戳分组
│   │   ├── test_session.json
│   │   ├── intent_tests.log
│   │   ├── execution_tests.log
│   │   └── scene_tests.log
├── analyzers/             # 🔍 自动分析工具
│   ├── intent_analyzer.py
│   ├── content_analyzer.py
│   ├── performance_analyzer.py
│   └── report_generator.py
├── common/                # 🛠️ 公共工具
│   ├── test_utils.py
│   ├── ai_setup.py
│   ├── logger.py
│   └── interactive_ui.py
└── templates/             # 📄 模板文件
    ├── guide_template.md
    └── report_template.html
```

## 详细设计

### 1. 测试执行器 (runner.py)

```python
class InteractiveTestRunner:
    \"\"\"交互式测试执行器\"\"\"
    
    def start(self):
        \"\"\"启动交互式测试界面\"\"\"
        print("🎮 TRPG Agent 测试系统")
        print("请选择要测试的模块:")
        print("1. 意图识别系统")
        print("2. 执行引擎")  
        print("3. 场景生成")
        print("4. 动态内容生成")
        print("5. 完整集成测试")
        
    def run_module_test(self, module: str):
        \"\"\"运行指定模块的测试\"\"\"
        # 1. 显示引导文档
        # 2. 用户交互执行测试
        # 3. 记录测试日志
        # 4. 自动分析结果
        
    def show_guide(self, guide_file: str):
        \"\"\"显示测试引导文档\"\"\"
        
    def collect_user_input(self) -> List[str]:
        \"\"\"收集用户测试输入\"\"\"
        
    def execute_tests(self, inputs: List[str]) -> TestSession:
        \"\"\"执行测试并记录日志\"\"\"
        
    def analyze_results(self, session: TestSession) -> TestReport:
        \"\"\"分析测试结果\"\"\"
```

### 2. 测试引导文档格式

#### 标准引导文档模板

```markdown
# {模块名称} 测试指南

## 模块说明
{模块功能介绍}

## 测试目标
- [ ] 目标1
- [ ] 目标2

## 测试步骤

### 步骤1: {步骤名称}
**说明**: {步骤描述}  
**输入建议**: 
- "示例输入1"
- "示例输入2"

**预期结果**: {预期的输出}

### 步骤2: ...

## 测试检查点
- [ ] 检查点1
- [ ] 检查点2

## 常见问题
Q: 问题1?  
A: 解答1

## 完成标准
- 所有检查点都通过
- 没有异常或错误
- 结果符合预期
```

### 3. 日志记录系统

#### 统一日志格式

```python
@dataclass
class TestLog:
    timestamp: str
    module: str           # "intent_classification"
    test_case: str        # "基本攻击意图"
    user_input: str       # "我攻击哥布林"
    system_output: str    # AI回复
    execution_time: float # 执行时间
    success: bool         # 是否成功
    error_message: str    # 错误信息
    metadata: Dict[str, Any]  # 额外信息

@dataclass  
class TestSession:
    session_id: str
    start_time: str
    end_time: str
    module: str
    test_logs: List[TestLog]
    summary: Dict[str, Any]
```

#### 日志存储结构

```
logs/20250911_143022/
├── session_info.json      # 测试会话基本信息
├── intent_tests.jsonl     # 意图识别测试日志(每行一个JSON)
├── execution_tests.jsonl  # 执行引擎测试日志
├── scene_tests.jsonl      # 场景生成测试日志  
├── performance.json       # 性能指标
└── user_feedback.txt      # 用户反馈记录
```

### 4. 自动分析工具

#### 意图识别分析器
```python
class IntentAnalyzer:
    def analyze_accuracy(self, logs: List[TestLog]) -> Dict[str, float]:
        \"\"\"分析意图识别准确率\"\"\"
        
    def analyze_confidence_distribution(self, logs: List[TestLog]):
        \"\"\"分析置信度分布\"\"\"
        
    def find_misclassified_cases(self, logs: List[TestLog]):
        \"\"\"找出误分类案例\"\"\"
```

#### 内容质量分析器  
```python
class ContentAnalyzer:
    def check_attack_content_leakage(self, logs: List[TestLog]):
        \"\"\"检查非攻击场景是否包含攻击内容\"\"\"
        
    def analyze_creativity_score(self, logs: List[TestLog]):
        \"\"\"分析动态内容的创造性评分\"\"\"
        
    def detect_hardcoded_content(self, logs: List[TestLog]):
        \"\"\"检测是否包含硬编码内容\"\"\"
```

#### 性能分析器
```python
class PerformanceAnalyzer:
    def analyze_response_time(self, logs: List[TestLog]):
        \"\"\"分析响应时间分布\"\"\"
        
    def analyze_ai_usage(self, logs: List[TestLog]):
        \"\"\"分析AI调用次数和成本\"\"\"
```

### 5. 交互式界面

#### 命令行界面设计
```
🎮 TRPG Agent 测试系统
========================================

请选择要测试的模块:
  [1] 意图识别系统 - 测试AI对用户输入的理解能力
  [2] 执行引擎 - 测试游戏逻辑的执行正确性  
  [3] 场景生成 - 测试AI场景描述的质量
  [4] 动态内容 - 测试AI动态创建游戏内容
  [5] 完整集成 - 测试端到端完整流程
  [0] 查看历史测试报告

请输入选择 (1-5): 1

========================================
📋 意图识别系统测试指南
========================================

模块说明: 
意图识别系统负责理解用户的游戏输入，将自然语言转换为
结构化的游戏意图，是三层AI架构的第一层。

测试目标:
  ✓ 验证基本意图分类的准确性
  ✓ 测试复杂语句的理解能力
  ✓ 检查边界情况的处理

请按照指南逐步进行测试...

输入测试语句 (输入 'quit' 结束): 我攻击哥布林

🤖 AI正在处理...
✅ 意图识别结果:
  类别: 攻击
  目标: 哥布林
  置信度: 0.95
  处理时间: 1.2秒

继续输入下一个测试用例...
```

## 实现计划

### 阶段1: 基础框架 (1-2天)
1. 创建目录结构
2. 实现基础的TestRunner类  
3. 设计统一的日志格式
4. 创建第一个测试引导文档

### 阶段2: 核心功能 (2-3天)
1. 实现日志记录和存储
2. 开发基础分析工具
3. 创建交互式用户界面
4. 完善引导文档模板

### 阶段3: 完整测试模块 (2-3天)  
1. 将现有测试脚本转换为引导文档
2. 实现所有分析器
3. 生成HTML测试报告
4. 用户体验优化

## 与现有系统的集成

### 复用现有代码
- **AI配置**: 复用`Agent/config/ai_config.py`的检测和配置逻辑
- **系统初始化**: 提取公共的AI服务初始化代码
- **测试用例**: 迁移现有脚本中的有效测试用例

### 渐进迁移策略
1. **保留现有脚本**: 在新框架完成前继续可用
2. **逐步迁移**: 每完成一个模块就迁移对应的测试
3. **验证等效性**: 确保新框架的测试覆盖不少于现有脚本

## 用户体验设计

### 设计原则
1. **引导性**: 清晰的步骤指导，用户无需了解技术细节
2. **交互性**: 实时反馈和进度显示
3. **可视性**: 直观的结果展示和分析报告
4. **可追溯**: 完整的测试历史和结果对比

### 面向用户
- **开发者**: 详细的技术分析和调试信息
- **测试人员**: 友好的功能验证界面  
- **产品经理**: 高层次的质量报告和趋势分析

这个设计将彻底改变测试方式，从技术导向转向用户导向，提供更好的测试体验和更可靠的质量保障。