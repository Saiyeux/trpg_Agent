#!/usr/bin/env python3
"""
真实AI集成端到端测试

使用真实的AI服务（Ollama/LM Studio）进行完整的TRPG游戏流程测试，
分析AI响应质量和游戏体验。
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Agent.config.ai_config import detect_and_configure_ai, create_ai_client_from_config
from Agent.implementations.model_bridge import RealModelBridge
from Agent.implementations.execution_engine import RealExecutionEngine
from Agent.implementations.game_state import RealGameState


class AITestAnalyzer:
    """AI测试分析器"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
    
    def add_test_result(self, test_name: str, user_input: str, ai_response: str, 
                       call_history: List[Dict], execution_history: List[Dict],
                       game_state_before: Dict, game_state_after: Dict):
        """添加测试结果"""
        result = {
            'test_name': test_name,
            'timestamp': time.time(),
            'user_input': user_input,
            'ai_response': ai_response,
            'call_history': call_history,
            'execution_history': execution_history,
            'game_state_before': game_state_before,
            'game_state_after': game_state_after,
            'analysis': self._analyze_response(user_input, ai_response, call_history)
        }
        self.test_results.append(result)
    
    def _analyze_response(self, user_input: str, ai_response: str, call_history: List[Dict]) -> Dict[str, Any]:
        """分析AI响应质量"""
        analysis = {
            'response_length': len(ai_response),
            'has_concrete_results': False,
            'has_vague_language': False,
            'mentions_numbers': False,
            'mentions_damage': False,
            'mentions_hp': False,
            'ai_layers_called': len(call_history),
            'total_response_time': sum(call.get('response_time', 0) for call in call_history),
            'quality_score': 0
        }
        
        # 检查具体结果 vs 模糊语言
        concrete_keywords = ['伤害', '点', '血量', '生命值', '击中', '失误', '成功', '失败', '造成', '降至', '从', '到', '发现了', '没有发现']
        vague_keywords = ['似乎', '可能', '也许', '感受到', '氛围', '仿佛', '好像', '大概', '应该', '或许', '感觉', '看起来', '听起来']
        
        response_lower = ai_response.lower()
        analysis['has_concrete_results'] = any(keyword in ai_response for keyword in concrete_keywords)
        analysis['has_vague_language'] = any(keyword in ai_response for keyword in vague_keywords)
        analysis['mentions_numbers'] = any(char.isdigit() for char in ai_response)
        analysis['mentions_damage'] = '伤害' in ai_response
        analysis['mentions_hp'] = any(hp_word in ai_response for hp_word in ['血量', '生命值', 'HP', 'hp'])
        
        # 计算质量分数 (0-100)
        score = 30  # 基础分
        if analysis['has_concrete_results']: score += 25  # 提高具体结果权重
        if analysis['mentions_numbers']: score += 20    # 提高数值权重
        if analysis['mentions_damage']: score += 10
        if analysis['mentions_hp']: score += 10
        if not analysis['has_vague_language']: score += 25  # 大幅提高无模糊语言权重
        if analysis['ai_layers_called'] == 3: score += 5   # 降低技术指标权重
        if analysis['response_length'] > 50: score += 3    # 降低长度权重
        if analysis['total_response_time'] < 10: score += 2  # 降低速度权重
        
        analysis['quality_score'] = min(100, score)
        return analysis
    
    def generate_report(self) -> str:
        """生成测试报告"""
        if not self.test_results:
            return "没有测试数据"
        
        total_time = time.time() - self.start_time
        avg_quality = sum(result['analysis']['quality_score'] for result in self.test_results) / len(self.test_results)
        
        report = []
        report.append("=" * 80)
        report.append("真实AI集成测试报告")
        report.append("=" * 80)
        report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"总耗时: {total_time:.2f}秒")
        report.append(f"测试案例: {len(self.test_results)}个")
        report.append(f"平均质量得分: {avg_quality:.1f}/100")
        report.append("")
        
        # 详细测试结果
        for i, result in enumerate(self.test_results, 1):
            analysis = result['analysis']
            report.append(f"测试 {i}: {result['test_name']}")
            report.append("-" * 40)
            report.append(f"用户输入: {result['user_input']}")
            report.append(f"AI回复: {result['ai_response']}")
            report.append(f"质量得分: {analysis['quality_score']}/100")
            report.append(f"AI调用层数: {analysis['ai_layers_called']}")
            report.append(f"响应时间: {analysis['total_response_time']:.2f}秒")
            
            # 质量分析
            quality_items = []
            if analysis['has_concrete_results']: quality_items.append("✅ 包含具体结果")
            if analysis['mentions_numbers']: quality_items.append("✅ 提及具体数值")
            if analysis['mentions_damage']: quality_items.append("✅ 描述伤害")
            if analysis['mentions_hp']: quality_items.append("✅ 提及生命值")
            if not analysis['has_vague_language']: quality_items.append("✅ 无模糊表述")
            else: quality_items.append("⚠️  包含模糊表述")
            
            report.append("质量指标: " + ", ".join(quality_items))
            report.append("")
        
        # 总结和建议
        report.append("=" * 40)
        report.append("测试总结")
        report.append("=" * 40)
        
        if avg_quality >= 80:
            report.append("🎉 AI响应质量优秀！")
        elif avg_quality >= 60:
            report.append("✅ AI响应质量良好")
        else:
            report.append("⚠️  AI响应质量需要改进")
        
        # 统计分析
        concrete_count = sum(1 for r in self.test_results if r['analysis']['has_concrete_results'])
        vague_count = sum(1 for r in self.test_results if r['analysis']['has_vague_language'])
        
        report.append(f"具体结果率: {concrete_count}/{len(self.test_results)} ({concrete_count/len(self.test_results)*100:.1f}%)")
        report.append(f"模糊表述率: {vague_count}/{len(self.test_results)} ({vague_count/len(self.test_results)*100:.1f}%)")
        
        return "\n".join(report)
    
    def save_detailed_results(self, filepath: str):
        """保存详细测试结果到JSON文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'test_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_tests': len(self.test_results),
                    'total_time': time.time() - self.start_time
                },
                'results': self.test_results
            }, f, ensure_ascii=False, indent=2)


def run_real_ai_tests():
    """运行真实AI集成测试"""
    print("开始真实AI集成测试...")
    
    # 1. 检测AI服务
    print("\n--- 检测AI服务 ---")
    ai_config = detect_and_configure_ai()
    if not ai_config:
        print("❌ 没有可用的AI服务，测试终止")
        return False
    
    print(f"✅ 使用AI服务: {ai_config.name}")
    
    # 2. 初始化组件
    print("\n--- 初始化测试组件 ---")
    model_client = create_ai_client_from_config(ai_config)
    execution_engine = RealExecutionEngine()
    game_state = RealGameState()
    
    # 创建真实的ModelBridge
    model_bridge = RealModelBridge(
        model_client=model_client,
        execution_engine=execution_engine,
        game_state=game_state
    )
    
    print("✅ 所有组件初始化完成")
    
    # 3. 创建测试分析器
    analyzer = AITestAnalyzer()
    
    # 4. 定义测试场景
    test_scenarios = [
        {
            'name': '攻击哥布林',
            'input': '我攻击哥布林',
            'description': '基础攻击测试，验证AI是否能给出具体伤害结果'
        },
        {
            'name': '再次攻击',
            'input': '我继续攻击哥布林',
            'description': '连续攻击测试，验证状态持续性'
        },
        {
            'name': '使用武器攻击',
            'input': '我用剑攻击哥布林',
            'description': '指定武器攻击测试'
        },
        {
            'name': '搜索环境',
            'input': '我搜索周围',
            'description': '搜索功能测试'
        },
        {
            'name': '检查状态',
            'input': '查看我的状态',
            'description': '状态查询测试（目前可能不支持）'
        }
    ]
    
    # 5. 执行测试
    print(f"\n--- 执行 {len(test_scenarios)} 个测试场景 ---")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n测试 {i}/{len(test_scenarios)}: {scenario['name']}")
        print(f"输入: {scenario['input']}")
        
        # 记录测试前状态
        state_before = game_state.to_dict()
        
        # 执行测试
        start_time = time.time()
        response = model_bridge.process_user_input(scenario['input'])
        end_time = time.time()
        
        # 记录测试后状态
        state_after = game_state.to_dict()
        
        print(f"回复: {response}")
        print(f"耗时: {end_time - start_time:.2f}秒")
        
        # 获取调用历史
        call_history = model_bridge.get_call_history()
        execution_history = execution_engine.get_execution_history()
        
        # 添加响应时间到调用历史
        for call in call_history:
            if 'timestamp' in call:
                call['response_time'] = call.get('response_time', 1.0)
        
        # 记录测试结果
        analyzer.add_test_result(
            test_name=scenario['name'],
            user_input=scenario['input'],
            ai_response=response,
            call_history=call_history.copy(),
            execution_history=execution_history.copy(),
            game_state_before=state_before,
            game_state_after=state_after
        )
        
        # 清空历史，准备下一个测试
        model_bridge.clear_history()
        execution_engine.clear_history()
        
        # 短暂休息，避免请求过快
        time.sleep(1)
    
    # 6. 生成测试报告
    print("\n--- 生成测试报告 ---")
    report = analyzer.generate_report()
    print(report)
    
    # 7. 保存详细结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    report_file = f"test_report_{timestamp}.txt"
    
    analyzer.save_detailed_results(results_file)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 详细结果已保存到: {results_file}")
    print(f"✅ 测试报告已保存到: {report_file}")
    
    return True


if __name__ == "__main__":
    try:
        success = run_real_ai_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)