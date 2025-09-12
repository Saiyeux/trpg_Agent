"""
文本生成模块

使用LM Studio提供文本生成服务，将执行结果和状态变更转换为
用户友好的自然语言描述。
"""

import json
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from ..interfaces.data_structures import ExecutionResult, StateChange


@dataclass 
class TextResponse:
    """文本响应结果"""
    content: str                    # 生成的文本内容
    success: bool                   # 生成是否成功
    error_message: str = ""         # 错误信息
    metadata: Dict[str, Any] = None # 额外元数据
    has_potential_changes: bool = False  # 是否包含潜在状态变更


@dataclass
class LMStudioConfig:
    """LM Studio配置"""
    endpoint: str = "http://localhost:1234"
    model: str = ""  # 自动检测
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30


class TextGenerator:
    """文本生成器 - LM Studio后端"""
    
    def __init__(self, config: LMStudioConfig = None):
        self.config = config or LMStudioConfig()
        self.session = requests.Session()
        self._available_models = []
        self._current_model = None
        
    def initialize(self) -> bool:
        """初始化连接并检测可用模型"""
        try:
            # 检查服务连通性
            response = self.session.get(f"{self.config.endpoint}/v1/models", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                self._available_models = [model["id"] for model in models_data.get("data", [])]
                
                if self._available_models:
                    self._current_model = self._available_models[0]  # 使用第一个可用模型
                    print(f"✅ LM Studio连接成功，使用模型: {self._current_model}")
                    return True
                else:
                    print("❌ LM Studio没有加载模型")
                    return False
            else:
                print(f"❌ LM Studio连接失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ LM Studio初始化失败: {str(e)}")
            return False
    
    def generate_response(self, execution_result: ExecutionResult, 
                         state_changes: List[StateChange], 
                         game_context: Dict[str, Any] = None) -> TextResponse:
        """
        生成用户响应文本
        
        Args:
            execution_result: 执行结果
            state_changes: 状态变更列表
            game_context: 游戏上下文信息
        """
        if not self._current_model:
            return TextResponse(
                content="系统错误：文本生成服务未初始化",
                success=False,
                error_message="No available model"
            )
        
        try:
            # 构建prompt
            prompt = self._build_narrative_prompt(execution_result, state_changes, game_context)
            
            # 调用LM Studio API
            response_data = self._call_lm_studio_api(prompt)
            
            if response_data and "choices" in response_data:
                generated_text = response_data["choices"][0]["message"]["content"].strip()
                
                # 检测是否包含潜在状态变更
                has_changes = self._detect_potential_changes(generated_text)
                
                return TextResponse(
                    content=generated_text,
                    success=True,
                    has_potential_changes=has_changes,
                    metadata={
                        "model": self._current_model,
                        "tokens_used": response_data.get("usage", {}).get("total_tokens", 0)
                    }
                )
            else:
                return TextResponse(
                    content="抱歉，文本生成失败，请重试。",
                    success=False,
                    error_message="Invalid API response"
                )
                
        except Exception as e:
            print(f"文本生成错误: {str(e)}")
            return TextResponse(
                content="系统遇到问题，请稍后重试。",
                success=False,
                error_message=str(e)
            )
    
    def _build_narrative_prompt(self, execution_result: ExecutionResult, 
                               state_changes: List[StateChange],
                               game_context: Dict[str, Any] = None) -> str:
        """构建叙事prompt"""
        
        # 基础上下文
        context_info = ""
        if game_context:
            player_location = game_context.get("player_location", "未知位置")
            player_hp = game_context.get("player_hp", "未知")
            player_mp = game_context.get("player_mp", "未知")
            context_info = f"""
当前游戏状态：
- 玩家位置：{player_location}
- 生命值：{player_hp}
- 魔法值：{player_mp}
"""
        
        # 执行结果描述
        action_description = ""
        if execution_result.success:
            action_description = f"玩家的行动成功执行。类别：{execution_result.intent_category}"
            if execution_result.target:
                action_description += f"，目标：{execution_result.target}"
        else:
            action_description = f"玩家的行动执行失败：{execution_result.error_message}"
        
        # 状态变更描述
        changes_description = ""
        if state_changes:
            changes_list = []
            for change in state_changes:
                change_desc = f"{change.target}的{change.property_name}从{change.old_value}变为{change.new_value}"
                if change.change_reason:
                    change_desc += f"（{change.change_reason}）"
                changes_list.append(change_desc)
            changes_description = "状态变更：" + "；".join(changes_list)
        
        # 构建完整prompt
        prompt = f"""你是一个专业的TRPG（桌面角色扮演游戏）叙事AI。请根据以下游戏执行结果，为玩家生成一段生动、有趣的文字描述。

{context_info}

执行结果：{action_description}

{changes_description}

请求：
1. 用第二人称"你"来叙述，让玩家有代入感
2. 文字要生动有趣，符合奇幻冒险的氛围
3. 自然地融入状态变更，不要生硬地报告数值
4. 如果合适，可以描述环境、NPC反应或暗示后续可能的剧情
5. 长度控制在100-200字
6. 如果你在叙述中提到了新的地点、人物或物品，请在最后用【新增内容：xxx】的格式标注

回复格式：
直接给出叙述文字，不需要其他格式或说明。"""

        return prompt
    
    def _call_lm_studio_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """调用LM Studio API"""
        
        payload = {
            "model": self._current_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": False
        }
        
        try:
            response = self.session.post(
                f"{self.config.endpoint}/v1/chat/completions",
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"LM Studio API错误: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"API调用异常: {str(e)}")
            return None
    
    def _detect_potential_changes(self, text: str) -> bool:
        """检测文本中是否包含潜在的状态变更"""
        
        # 关键词检测
        change_indicators = [
            "【新增内容：",  # 明确标记的新内容
            "发现了", "找到了", "获得了", "得到了",  # 物品获得
            "来到了", "到达了", "进入了", "抵达了",  # 新地点
            "遇见了", "见到了", "碰到了",  # 新NPC
            "建造了", "创建了", "开辟了",  # 新建筑/地点
            "学会了", "掌握了", "习得了",  # 新技能
        ]
        
        text_lower = text.lower()
        for indicator in change_indicators:
            if indicator.lower() in text_lower:
                return True
        
        return False
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return self._available_models.copy()
    
    def switch_model(self, model_name: str) -> bool:
        """切换使用的模型"""
        if model_name in self._available_models:
            self._current_model = model_name
            print(f"✅ 已切换到模型: {model_name}")
            return True
        else:
            print(f"❌ 模型不可用: {model_name}")
            return False
    
    def test_generation(self) -> TextResponse:
        """测试文本生成功能"""
        from ..interfaces.data_structures import Intent
        
        # 创建测试数据
        test_intent = Intent(category="攻击", action="攻击哥布林", target="哥布林")
        test_result = ExecutionResult(
            success=True,
            intent_category="攻击",
            target="哥布林",
            result_description="成功攻击了哥布林",
            state_changes=[]
        )
        
        test_changes = [
            StateChange(
                target="forest_goblin",
                property_name="hp", 
                old_value=30,
                new_value=10,
                change_reason="受到玩家攻击"
            )
        ]
        
        test_context = {
            "player_location": "幽暗森林",
            "player_hp": 100,
            "player_mp": 50
        }
        
        return self.generate_response(test_result, test_changes, test_context)


# 工厂函数
def create_text_generator(endpoint: str = "http://localhost:1234") -> TextGenerator:
    """创建文本生成器实例"""
    config = LMStudioConfig(endpoint=endpoint)
    generator = TextGenerator(config)
    
    if generator.initialize():
        return generator
    else:
        raise ConnectionError("无法连接到LM Studio服务")


# 便利函数 
def quick_generate(execution_result: ExecutionResult, 
                  state_changes: List[StateChange],
                  game_context: Dict[str, Any] = None,
                  endpoint: str = "http://localhost:1234") -> TextResponse:
    """快速文本生成"""
    try:
        generator = create_text_generator(endpoint)
        return generator.generate_response(execution_result, state_changes, game_context)
    except Exception as e:
        return TextResponse(
            content="文本生成服务暂不可用。",
            success=False,
            error_message=str(e)
        )