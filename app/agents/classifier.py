"""
重庆劳动法案件分类器 Agent
"""

from typing import Dict, Any, List
from .base import BaseAgent, AgentCapability
from .chongqing_labor_law import ChongqingLaborLawAgent


class CaseClassifierAgent(BaseAgent):
    """案件分类器 Agent"""
    
    def __init__(self, llm_client, knowledge_base):
        capability = AgentCapability(
            domain="classification",
            expertise_level=9,
            supported_tasks=["case_classification", "jurisdiction_determination"],
            required_knowledge=["legal_categories", "jurisdiction_rules"]
        )
        super().__init__(
            agent_id="classifier_001",
            agent_name="案件分类器",
            capability=capability,
            llm_client=llm_client,
            knowledge_base=knowledge_base
        )
    
    async def analyze(self, case_data: Dict[str, Any], blackboard=None) -> Dict[str, Any]:
        """分析案件并分类"""
        # 1. 从知识库获取分类体系
        classification_system = self.knowledge_base.get("legal_categories") if self.knowledge_base else []
        
        # 2. 构建分类提示
        prompt = f"""
        你作为法律案件分类专家，需要根据案件描述进行分类：
        
        案件描述：
        {case_data.get('description', case_data.get('facts', ''))}
        
        可用分类体系：
        {classification_system}
        
        请按以下步骤分析：
        1. 确定是否为劳动法案件
        2. 确定具体劳动纠纷类型（工资、加班、工伤、解雇等）
        3. 判断是否属于重庆管辖范围
        4. 返回分类结果
        """
        
        # 3. 调用 LLM 进行分类
        classification_result = await self.llm_client.generate_text(prompt)
        
        # 4. 解析结果
        return self._parse_classification_result(classification_result)
    
    def _parse_classification_result(self, result_text: str) -> Dict[str, Any]:
        """解析分类结果"""
        # 简化实现：实际项目中需要更健壮的解析
        return {
            "domain": "劳动法",
            "case_type": "工资纠纷",
            "jurisdiction": "重庆",
            "confidence": 0.95
        }
    
    async def collaborate(
        self,
        other_agents: List[BaseAgent],
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """与重庆劳动法专家协作"""
        # 获取重庆劳动法专家意见
        labor_agent = next((a for a in other_agents if isinstance(a, ChongqingLaborLawAgent)), None)
        if labor_agent:
            labor_opinion = await labor_agent.analyze(case_data)
            return {
                "classification": "劳动法案件",
                "labor_opinion": labor_opinion
            }
        return await self.analyze(case_data)
    
    def _integrate_opinions(self, opinions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """综合多个分类意见"""
        # 简单实现：取多数意见
        domains = [op["domain"] for op in opinions]
        most_common = max(set(domains), key=domains.count)
        return {
            "domain": most_common,
            "case_type": "综合类型",
            "confidence": 0.9
        }
    
    async def handle_query(self, sender_id: str, content: Dict[str, Any]):
        """处理查询消息"""
        # 实现查询处理逻辑
        pass
