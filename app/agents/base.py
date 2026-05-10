"""
Agent 基类定义
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from .communication import AgentMessage


@dataclass
class AgentCapability:
    """Agent 能力描述"""
    domain: str                    # 法律领域
    expertise_level: int           # 专业等级 1-10
    supported_tasks: List[str]     # 支持的任务类型
    required_knowledge: List[str]  # 所需知识库


class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        capability: AgentCapability,
        llm_client: Any,
        knowledge_base: Any
    ):
        """
        初始化 Agent
        
        :param agent_id: Agent 唯一标识符
        :param agent_name: Agent 名称
        :param capability: Agent 能力描述
        :param llm_client: LLM 客户端实例
        :param knowledge_base: 知识库实例
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.capability = capability
        self.llm_client = llm_client
        self.knowledge_base = knowledge_base
        self.communication_bus = None
    
    @abstractmethod
    async def analyze(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析案件，返回分析结果
        
        :param case_data: 案件数据
        :return: 分析结果
        """
        pass
    
    @abstractmethod
    async def collaborate(
        self, 
        other_agents: List['BaseAgent'], 
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        与其他 Agent 协作分析
        
        :param other_agents: 其他 Agent 列表
        :param case_data: 案件数据
        :return: 协作分析结果
        """
        pass
    
    def register_to_bus(self, communication_bus):
        """
        注册到通信总线
        
        :param communication_bus: 通信总线实例
        """
        self.communication_bus = communication_bus
    
    async def send_message(self, receiver_id: str, content: Dict[str, Any]):
        """
        发送消息给其他 Agent
        
        :param receiver_id: 接收者 Agent ID
        :param content: 消息内容
        """
        if self.communication_bus:
            message = AgentMessage(
                sender=self.agent_id,
                receiver=receiver_id,
                message_type="query",
                content=content
            )
            await self.communication_bus.send_message(message)
