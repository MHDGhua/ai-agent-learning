"""
重庆劳动仲裁建议生成器
"""

class ChongqingArbitrationAdvisor:
    """重庆劳动仲裁策略建议"""
    
    # 重庆仲裁委倾向性策略
    ARBITRATION_STYLE = """
    重庆劳动仲裁特点：
    1. 高度重视加班费计算准确性
    2. 严格执行高温津贴支付
    3. 对违法解雇案件倾向支持劳动者
    4. 工伤认定标准较为宽松
    """
    
    @staticmethod
    def generate_strategy(case_type: str, strength: float) -> dict:
        """生成仲裁策略
        
        :param case_type: 案件类型（工资/加班/工伤/解雇）
        :param strength: 证据强度（0-1）
        :return: 仲裁策略
        """
        strategies = {
            "工资": {
                "strong": "直接申请仲裁，要求全额支付+25%赔偿金",
                "medium": "先发律师函，协商不成再仲裁",
                "weak": "收集银行流水等证据后再申请"
            },
            "加班": {
                "strong": "主张3年内的所有加班费",
                "medium": "主张2年内的加班费",
                "weak": "从发现权益受损之日起计算"
            },
            "工伤": {
                "strong": "直接申请工伤认定+赔偿",
                "medium": "先申请工伤认定再索赔",
                "weak": "收集劳动关系证据后再申请"
            },
            "解雇": {
                "strong": "主张2N赔偿+代通知金",
                "medium": "主张N+1赔偿",
                "weak": "主张经济补偿金"
            }
        }
        
        # 根据证据强度选择策略
        strength_key = "strong" if strength > 0.8 else "medium" if strength > 0.5 else "weak"
        
        return {
            "case_type": case_type,
            "strategy": strategies[case_type][strength_key],
            "success_rate": min(strength * 0.9 + 0.3, 0.95),  # 基础成功率30%，最高95%
            "recommended_evidence": ChongqingArbitrationAdvisor._get_evidence(case_type)
        }
    
    @staticmethod
    def _get_evidence(case_type: str) -> list:
        """推荐收集的证据类型"""
        evidence_map = {
            "工资": ["劳动合同", "银行流水", "工资条", "社保缴费记录"],
            "加班": ["考勤记录", "加班审批单", "工作沟通记录", "证人证言"],
            "工伤": ["工伤认定书", "医疗记录", "劳动关系证明", "事故证明"],
            "解雇": ["解除通知", "劳动合同", "工作交接记录", "录音录像"]
        }
        return evidence_map.get(case_type, [])