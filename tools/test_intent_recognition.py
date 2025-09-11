#!/usr/bin/env python3
"""
意图识别修复测试

验证修复后的意图识别系统能够正确处理对话、交易、状态查询等不同类型的用户输入。
确保不再将所有输入都误判为攻击行为。
"""

import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Agent.config.ai_config import detect_and_configure_ai, create_ai_client_from_config
from Agent.implementations.model_bridge import RealModelBridge
from Agent.implementations.execution_engine import RealExecutionEngine
from Agent.implementations.game_state import RealGameState


def test_intent_recognition():
    """测试意图识别修复效果"""
    print("🎯 意图识别修复测试开始...")
    
    # 1. 初始化系统
    ai_config = detect_and_configure_ai()
    if not ai_config:
        print("❌ 没有可用的AI服务")
        return False
    
    print(f"✅ 使用AI服务: {ai_config.name}")
    
    model_client = create_ai_client_from_config(ai_config)
    execution_engine = RealExecutionEngine()
    game_state = RealGameState()
    
    model_bridge = RealModelBridge(
        model_client=model_client,
        execution_engine=execution_engine,
        game_state=game_state
    )
    
    print("✅ 系统初始化完成")
    
    # 2. 定义测试用例
    test_cases = [
        {
            'input': '和商人对话',
            'expected_category': '对话',
            'expected_target': '商人',
            'description': '基本对话测试'
        },
        {
            'input': '购买商人的物品',
            'expected_category': '交易',
            'expected_target': '商人',
            'description': '基本交易测试'
        },
        {
            'input': '我想买东西',
            'expected_category': '交易',
            'expected_target': '',
            'description': '购买意图测试'
        },
        {
            'input': '查看我的状态',
            'expected_category': '状态查询',
            'expected_target': '',
            'description': '状态查询测试'
        },
        {
            'input': '我攻击哥布林',
            'expected_category': '攻击',
            'expected_target': '哥布林',
            'description': '攻击意图确认'
        },
        {
            'input': '我搜索周围',
            'expected_category': '搜索',
            'expected_target': '周围',
            'description': '搜索意图确认'
        },
        {
            'input': '与商人老约翰交谈',
            'expected_category': '对话',
            'expected_target': '商人老约翰',
            'description': '具体NPC对话'
        },
        {
            'input': '我想花钱买装备',
            'expected_category': '交易',
            'expected_target': '',
            'description': '复杂交易表达'
        }
    ]
    
    print(f"\n--- 执行 {len(test_cases)} 个意图识别测试 ---")
    
    results = []
    correct_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['description']}")
        print(f"输入: \"{test_case['input']}\"")
        print(f"期望类别: {test_case['expected_category']}")
        
        # 测试意图识别（不执行完整流程）
        intent_message = model_bridge.classify_intent(test_case['input'])
        actual_category = intent_message.intent.category
        actual_target = intent_message.intent.target
        
        print(f"实际类别: {actual_category}")
        print(f"识别目标: {actual_target}")
        
        # 判断是否正确
        category_correct = actual_category == test_case['expected_category']
        target_reasonable = (
            not test_case['expected_target'] or  # 期望目标为空
            test_case['expected_target'].lower() in actual_target.lower()  # 目标匹配
        )
        
        is_correct = category_correct and target_reasonable
        correct_count += is_correct
        
        status = "✅ 正确" if is_correct else "❌ 错误"
        print(f"结果: {status}")
        
        if not category_correct:
            print(f"  ⚠️  类别识别错误: 期望 {test_case['expected_category']}, 实际 {actual_category}")
        
        if not target_reasonable and test_case['expected_target']:
            print(f"  ⚠️  目标识别问题: 期望包含 {test_case['expected_target']}, 实际 {actual_target}")
        
        # 记录结果
        results.append({
            'test_case': test_case,
            'actual_category': actual_category,
            'actual_target': actual_target,
            'category_correct': category_correct,
            'target_reasonable': target_reasonable,
            'overall_correct': is_correct,
            'confidence': intent_message.confidence
        })
    
    # 3. 测试完整流程
    print(f"\n--- 完整流程测试 ---")
    
    flow_tests = [
        "和商人对话",
        "购买商人的物品", 
        "查看我的状态"
    ]
    
    for test_input in flow_tests:
        print(f"\n完整测试: {test_input}")
        try:
            response = model_bridge.process_user_input(test_input)
            print(f"AI回复: {response}")
            
            # 检查是否还有攻击相关的错误回复
            attack_indicators = ["攻击", "命中", "伤害", "生命值", "躲开", "血量"]
            has_attack_content = any(indicator in response for indicator in attack_indicators)
            
            if has_attack_content and test_input != "我攻击哥布林":
                print("⚠️  仍然包含攻击相关内容，可能存在问题")
            else:
                print("✅ 回复内容合理")
                
        except Exception as e:
            print(f"❌ 执行错误: {e}")
    
    # 4. 生成测试报告
    print(f"\n" + "="*60)
    print("意图识别修复测试报告")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总测试案例: {len(test_cases)}")
    print(f"正确识别: {correct_count}")
    print(f"准确率: {correct_count/len(test_cases)*100:.1f}%")
    
    # 按类别统计
    category_stats = {}
    for result in results:
        expected = result['test_case']['expected_category']
        if expected not in category_stats:
            category_stats[expected] = {'total': 0, 'correct': 0}
        category_stats[expected]['total'] += 1
        if result['overall_correct']:
            category_stats[expected]['correct'] += 1
    
    print(f"\n按类别统计:")
    for category, stats in category_stats.items():
        accuracy = stats['correct'] / stats['total'] * 100
        print(f"  {category}: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")
    
    # 错误分析
    errors = [r for r in results if not r['overall_correct']]
    if errors:
        print(f"\n错误分析:")
        for error in errors:
            test_case = error['test_case']
            print(f"  输入: \"{test_case['input']}\"")
            print(f"    期望: {test_case['expected_category']} -> 实际: {error['actual_category']}")
    
    # 评估修复效果
    if correct_count == len(test_cases):
        print("\n🎉 意图识别完全修复！")
        success = True
    elif correct_count >= len(test_cases) * 0.8:
        print("\n✅ 意图识别大部分修复，仍有少量问题")
        success = True
    else:
        print("\n❌ 意图识别仍有较多问题，需要进一步修复")
        success = False
    
    # 保存详细结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"tools/intent_test_{timestamp}.json"
    
    test_data = {
        'test_metadata': {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(test_cases),
            'ai_service': ai_config.name,
            'accuracy': correct_count / len(test_cases)
        },
        'results': results,
        'category_stats': category_stats
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 详细测试结果已保存到: {results_file}")
    
    return success


if __name__ == "__main__":
    try:
        success = test_intent_recognition()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)