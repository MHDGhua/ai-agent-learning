"""
重庆劳动法赔偿计算引擎
"""

class ChongqingLaborCalculator:
    """重庆特色劳动法计算引擎"""
    
    # 2026年重庆劳动法参数
    MIN_WAGE = 2100  # 最低工资标准（元/月）
    AVG_WAGE = 7850  # 职工月平均工资
    HIGH_TEMP_ALLOWANCE = 25  # 高温津贴（元/天）
    
    @staticmethod
    def normalize_service_years(years: float) -> float:
        """经济补偿年限：不满半年按0.5，满半年不满一年按1。"""
        if years <= 0:
            return 0
        whole_years = int(years)
        remainder = years - whole_years
        if remainder == 0:
            return float(whole_years)
        return whole_years + (0.5 if remainder < 0.5 else 1.0)

    @staticmethod
    def calculate_severance(salary: float, years: float, reason: str) -> float:
        """计算经济补偿金（重庆标准）
        
        :param salary: 离职前12个月平均工资
        :param years: 工作年限（不满半年按0.5，满半年不满一年按1）
        :param reason: 解除原因（合法解除/违法解除）
        :return: 经济补偿金
        """
        normalized_years = ChongqingLaborCalculator.normalize_service_years(years)
        # 法定上限：月工资高于当地上年度职工月平均工资三倍的，按三倍封顶。
        capped_salary = min(salary, ChongqingLaborCalculator.AVG_WAGE * 3)
        
        if "违法" in reason:
            # 违法解除：2N
            return round(capped_salary * normalized_years * 2, 2)
        else:
            # 合法解除：N
            return round(capped_salary * normalized_years, 2)
    
    @staticmethod
    def calculate_overtime(hours: float, day_type: str, salary: float) -> float:
        """计算加班费（重庆标准）
        
        :param hours: 加班小时数
        :param day_type: 加班类型（平日/休息日/节假日）
        :param salary: 月工资
        :return: 加班费
        """
        hourly_wage = salary / 21.75 / 8  # 重庆采用21.75天月计薪日
        
        if day_type == "平日":
            return hours * hourly_wage * 1.5
        elif day_type == "休息日":
            return hours * hourly_wage * 2
        elif day_type == "节假日":
            return hours * hourly_wage * 3
        else:
            return hours * hourly_wage * 1.5  # 默认按平日加班
    
    @staticmethod
    def calculate_work_injury(level: int, salary: float) -> float:
        """计算工伤赔偿（重庆标准）
        
        :param level: 伤残等级（1-10）
        :param salary: 月工资
        :return: 一次性伤残补助金
        """
        # 重庆工伤赔偿系数
        coefficients = {
            1: 27, 2: 25, 3: 23, 4: 21, 5: 18,
            6: 16, 7: 13, 8: 11, 9: 9, 10: 7
        }
        return salary * coefficients.get(level, 0)
