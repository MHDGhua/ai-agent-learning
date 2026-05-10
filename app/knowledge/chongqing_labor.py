"""
重庆劳动法知识库管理
"""

class ChongqingLaborKnowledge:
    """重庆劳动法知识库"""
    
    def __init__(self):
        self.regulations = {
            "min_wage": 2100,  # 重庆最低工资标准
            "max_ot_hours": 36,  # 最大加班小时数
            "high_temp_allowance": 25,  # 高温津贴(元/天)
            "work_injury_rates": {  # 工伤赔偿系数
                "level1": 27,
                "level2": 25,
                "level3": 23
            }
        }
        
        self.precedents = []  # 重庆劳动法判例库
    
    def add_precedent(self, case_data: dict):
        """添加重庆劳动法判例"""
        self.precedents.append(case_data)
    
    def find_similar_cases(self, case_description: str, top_k: int = 3) -> list:
        """查找相似重庆劳动法判例"""
        # 简化实现 - 实际应使用向量搜索
        return self.precedents[:top_k]
    
    def calculate_compensation(self, salary: float, years: int, reason: str) -> float:
        """计算重庆劳动法经济补偿金"""
        # N: 工作年限
        # 违法解除: 2N
        # 合法解除: N
        multiplier = 2 if "违法" in reason else 1
        return salary * years * multiplier
    
    def calculate_overtime_pay(self, hours: float, salary: float) -> float:
        """计算重庆加班费"""
        # 平日加班: 1.5倍
        # 休息日加班: 2倍
        # 法定假日: 3倍
        return hours * salary / 21.75 / 8 * 1.5