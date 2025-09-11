#!/usr/bin/env python3
"""
动态搜索系统测试

验证AI动态生成物品和概念管理功能，确保不再依赖写死的内容列表。
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


def test_dynamic_search():
    """测试动态搜索功能"""
    print("🔍 动态搜索系统测试开始...")
    
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
    
    # 2. 检查初始概念状态
    print(f"\n--- 初始概念状态 ---")
    initial_concepts = game_state.concepts.get_all_concepts()
    print(f"初始概念数量: {len(initial_concepts)}")
    initial_items = game_state.concepts.get_concepts_by_type("item")
    print(f"初始物品概念: {len(initial_items)}")
    for item in initial_items:
        print(f"  - {item.name}: {item.description}")
    
    # 3. 执行多次搜索测试
    search_scenarios = [
        "我搜索周围",
        "我搜索房间角落",
        "我搜索宝箱", 
        "我搜索森林",
        "我搜索古老的遗迹"
    ]
    
    results = []
    
    for i, scenario in enumerate(search_scenarios, 1):
        print(f"\n--- 测试 {i}: {scenario} ---")
        
        # 记录测试前状态
        concepts_before = len(game_state.concepts.get_all_concepts())
        items_before = len(game_state.concepts.get_concepts_by_type("item"))
        
        # 执行搜索
        response = model_bridge.process_user_input(scenario)
        print(f"AI回复: {response}")
        
        # 记录测试后状态
        concepts_after = len(game_state.concepts.get_all_concepts())
        items_after = len(game_state.concepts.get_concepts_by_type("item"))
        
        # 分析结果
        new_concepts = concepts_after - concepts_before
        new_items = items_after - items_before
        
        result = {
            'scenario': scenario,
            'response': response,
            'new_concepts': new_concepts,
            'new_items': new_items,
            'concepts_total': concepts_after,
            'items_total': items_after,
            'has_static_content': any(keyword in response for keyword in [
                "生锈的匕首", "治疗药水", "古老的地图", "金币"
            ])
        }
        results.append(result)
        
        print(f"新增概念: {new_concepts}, 新增物品: {new_items}")
        if new_items > 0:
            # 显示新生成的物品
            all_items = game_state.concepts.get_concepts_by_type("item")
            latest_items = sorted(all_items, key=lambda x: x.created_turn, reverse=True)[:new_items]
            for item in latest_items:
                print(f"✨ 新物品: {item.name} - {item.description}")
                print(f"   属性: {item.properties}")
        
        if result['has_static_content']:
            print("⚠️  检测到可能的静态内容！")
    
    # 4. 生成测试报告
    print(f"\n" + "="*60)
    print("动态搜索系统测试报告")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试场景: {len(search_scenarios)}个")
    
    total_new_concepts = sum(r['new_concepts'] for r in results)
    total_new_items = sum(r['new_items'] for r in results)
    static_content_count = sum(1 for r in results if r['has_static_content'])
    
    print(f"总新增概念: {total_new_concepts}")
    print(f"总新增物品: {total_new_items}")
    print(f"静态内容检测: {static_content_count}/{len(results)} 个测试")
    
    # 评估动态性
    if static_content_count == 0:
        print("✅ 完全动态生成，无静态内容")
    elif static_content_count <= len(results) // 2:
        print("⚠️  部分动态，仍有少量静态内容")
    else:
        print("❌ 主要依赖静态内容，动态生成失效")
    
    # 评估创造性
    if total_new_items >= len(results) // 2:
        print("✅ 创造性良好，能够生成新物品")
    else:
        print("⚠️  创造性不足，生成新物品较少")
    
    # 5. 显示最终概念状态
    print(f"\n--- 最终概念状态 ---")
    final_concepts = game_state.concepts.get_all_concepts()
    final_items = game_state.concepts.get_concepts_by_type("item")
    print(f"最终概念数量: {len(final_concepts)}")
    print(f"最终物品概念: {len(final_items)}")
    
    print(f"\n所有生成的物品:")
    for item in final_items:
        created_mark = "🆕" if item.created_turn > 0 else "📦"
        print(f"  {created_mark} {item.name}: {item.description}")
        if item.properties:
            rarity = item.properties.get('rarity', 'common')
            value = item.properties.get('value', 'unknown')
            print(f"     稀有度: {rarity}, 价值: {value}")
    
    # 6. 保存详细测试结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"tools/dynamic_search_test_{timestamp}.json"
    
    test_data = {
        'test_metadata': {
            'timestamp': datetime.now().isoformat(),
            'total_scenarios': len(search_scenarios),
            'ai_service': ai_config.name
        },
        'results': results,
        'statistics': {
            'total_new_concepts': total_new_concepts,
            'total_new_items': total_new_items,
            'static_content_rate': static_content_count / len(results),
            'creativity_score': total_new_items / len(results)
        },
        'final_concepts': [concept.to_dict() for concept in final_concepts]
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 详细测试结果已保存到: {results_file}")
    
    return static_content_count == 0 and total_new_items > 0


if __name__ == "__main__":
    try:
        success = test_dynamic_search()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)