#!/usr/bin/env python3
"""
劳动仲裁功能使用示例
演示如何使用系统提供的仲裁功能
"""

import asyncio
import json
import sys
from typing import Dict, Any

# 导入系统组件
from app.services.arbitration_document_generator import ArbitrationDocumentGenerator, DocumentType
from app.services.arbitration_analyzer import ArbitrationAnalyzer

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


async def demonstrate_arbitration_features():
    """演示仲裁功能的使用"""
    
    print("=== 劳动仲裁辅助功能使用示例 ===\n")
    
    # 模拟一个具体的案件场景
    case_data = {
        "case_type": "加班费纠纷",
        "facts": "申请人自2022年入职重庆某某科技有限公司，担任软件工程师，每月加班约20小时，公司未支付加班费。根据劳动合同约定，加班需支付1.5倍工资。",
        "evidence": [
            "劳动合同（显示加班工资计算方式）",
            "考勤记录（显示加班时间）",
            "工资条（显示未支付加班费）",
            "公司内部邮件（确认加班安排）"
        ],
        "applicant_info": {
            "name": "张三",
            "position": "软件工程师",
            "work_years": 3,
            "monthly_salary": 15000,
            "contact": "138XXXXXXXX"
        },
        "evidence_quality": "优秀",
        "applicant_background": "普通员工"
    }
    
    print("案件基本情况:")
    print(f"  案件类型: {case_data['case_type']}")
    print(f"  案件事实: {case_data['facts'][:100]}...")
    print(f"  证据材料: {len(case_data['evidence'])}项")
    print()
    
    # 1. 案件分析
    print("1. 案件综合分析:")
    analyzer = ArbitrationAnalyzer()
    analysis = await analyzer.analyze_case(case_data)
    
    print(f"   - 风险等级: {analysis.risk_level.value}")
    print(f"   - 主要风险因素: {', '.join(analysis.risk_factors[:2])}...")
    print(f"   - 成功率: {analysis.success_probability.value}")
    print(f"   - 成本估算: ¥{analysis.cost_estimate['total_cost']}")
    print(f"   - 法律依据: {', '.join(analysis.legal_basis[:2])}...")
    print(f"   - 处理建议: {', '.join(analysis.recommendations[:2])}...")
    print()
    
    # 2. 成本估算
    print("2. 仲裁成本估算:")
    cost_estimate = await analyzer.estimate_cost(case_data)
    print(f"   - 仲裁费: ¥{cost_estimate['arbitration_fee']}")
    print(f"   - 律师费: ¥{cost_estimate['lawyer_fee']}")
    print(f"   - 其他费用: ¥{cost_estimate['other_costs']}")
    print(f"   - 总费用: ¥{cost_estimate['total_cost']}")
    print()
    
    # 3. 成功率预测
    print("3. 仲裁成功率预测:")
    success_prediction = await analyzer.predict_success_rate(case_data)
    print(f"   - 预测成功率: {success_prediction['success_probability']}")
    print(f"   - 置信度: {success_prediction['confidence']}")
    print(f"   - 关键因素: {', '.join(success_prediction['key_factors'])}")
    print()
    
    # 4. 生成仲裁文书
    print("4. 仲裁文书生成:")
    generator = ArbitrationDocumentGenerator()
    
    # 生成仲裁申请书
    try:
        application_content = await generator.generate_arbitration_document(
            DocumentType.ARBITRATION_APPLICATION, 
            case_data
        )
        print("   - 仲裁申请书生成成功")
        print(f"     内容长度: {len(application_content)} 字符")
        print(f"     预览: {application_content[:200]}...")
    except Exception as e:
        print(f"   - 仲裁申请书生成失败: {str(e)}")
    
    # 生成证据清单
    try:
        evidence_content = await generator.generate_arbitration_document(
            DocumentType.EVIDENCE_LIST, 
            case_data
        )
        print("   - 证据清单生成成功")
        print(f"     内容长度: {len(evidence_content)} 字符")
        print(f"     预览: {evidence_content[:200]}...")
    except Exception as e:
        print(f"   - 证据清单生成失败: {str(e)}")
    
    print("\n=== 使用示例结束 ===")


if __name__ == "__main__":
    asyncio.run(demonstrate_arbitration_features())
