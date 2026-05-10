#!/usr/bin/env python3
"""
红蓝对抗机制使用示例
演示如何使用系统提供的红蓝对抗功能
"""

import asyncio
import json
import sys
from typing import Dict, Any

# 导入系统组件
from app.services.arbitration_analyzer import ArbitrationAnalyzer
from app.agents.coordinator import CoordinatorAgent
from app.services.llm_client import LLMClient

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


async def demonstrate_opposition_mechanism():
    """演示红蓝对抗机制的使用"""
    
    print("=== 红蓝对抗机制使用示例 ===\n")
    
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
    
    # 1. 执行基本分析
    print("1. 执行基本案件分析:")
    analyzer = ArbitrationAnalyzer()
    
    try:
        analysis = await analyzer.analyze_case(case_data)
        
        print(f"   - 风险等级: {analysis.risk_level.value}")
        print(f"   - 成功率: {analysis.success_probability.value}")
        print(f"   - 成本估算: ¥{analysis.cost_estimate['total_cost']}")
        print(f"   - 法律依据: {', '.join(analysis.legal_basis[:2])}...")
        print(f"   - 处理建议: {', '.join(analysis.recommendations[:2])}...")
        print()
        
    except Exception as e:
        print(f"   基本分析失败: {str(e)}")
        return
    
    # 2. 启用红蓝对抗审查
    print("2. 启用红蓝对抗审查:")
    analysis_with_opposition = None
    
    try:
        # 创建协调器（用于红蓝对抗）
        llm_client = LLMClient()
        coordinator = CoordinatorAgent(llm_client, None)
        
        # 执行带对抗审查的分析
        analysis_with_opposition = await analyzer.analyze_case(case_data, coordinator)
        
        print("   对抗审查结果:")
        print(f"   - 红方律师分析: {analysis_with_opposition.opposition_review['red_lawyer_analysis'].get('role', '未知')}")
        print(f"   - 蓝方律师分析: {analysis_with_opposition.opposition_review['blue_lawyer_analysis'].get('role', '未知')}")
        print(f"   - 发现漏洞数量: {len(analysis_with_opposition.opposition_review['vulnerabilities_found'])}")
        print(f"   - 成功率提升: +{analysis_with_opposition.opposition_review['success_probability_improvement']:.2%}")
        
        # 显示具体漏洞
        if analysis_with_opposition.opposition_review['vulnerabilities_found']:
            print("\n   发现的漏洞:")
            for i, vuln in enumerate(analysis_with_opposition.opposition_review['vulnerabilities_found'][:3], 1):
                print(f"     {i}. 类型: {vuln.get('vulnerability_type') if isinstance(vuln, dict) else vuln.vulnerability_type}")
                print(f"        描述: {vuln.get('description') if isinstance(vuln, dict) else vuln.description}")
                print(f"        严重程度: {vuln.get('severity') if isinstance(vuln, dict) else vuln.severity}")
                print(f"        建议修复: {vuln.get('suggested_fix') if isinstance(vuln, dict) else vuln.suggested_fix}")
        
        # 显示改进建议
        if analysis_with_opposition.opposition_review['improvement_suggestions']:
            print("\n   改进建议:")
            for i, suggestion in enumerate(analysis_with_opposition.opposition_review['improvement_suggestions'][:3], 1):
                print(f"     {i}. {suggestion}")
                
        # 显示最终建议
        if analysis_with_opposition.opposition_review['final_recommendation']:
            print(f"\n   最终建议: {analysis_with_opposition.opposition_review['final_recommendation'][:100]}...")
        
        print()
        
    except Exception as e:
        print(f"   对抗审查失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 3. 展示对比效果
    print("3. 对比分析效果:")
    print("   基本分析结果:")
    print(f"     - 风险等级: {analysis.risk_level.value}")
    print(f"     - 成功率: {analysis.success_probability.value}")
    print(f"     - 成本估算: ¥{analysis.cost_estimate['total_cost']}")
    
    if analysis_with_opposition and analysis_with_opposition.opposition_review:
        print("\n   对抗审查后结果:")
        print(f"     - 风险等级: {analysis.risk_level.value}")
        print(f"     - 成功率: {analysis.success_probability.value}")
        print(f"     - 成本估算: ¥{analysis.cost_estimate['total_cost']}")
        print(f"     - 成功率提升: +{analysis_with_opposition.opposition_review['success_probability_improvement']:.2%}")
        print("     - 通过对抗审查，发现了潜在问题并提出了改进建议")
    
    print("\n=== 使用示例结束 ===")


if __name__ == "__main__":
    asyncio.run(demonstrate_opposition_mechanism())
