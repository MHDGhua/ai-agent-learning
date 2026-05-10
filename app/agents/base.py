"""
Agent 基类定义
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, TYPE_CHECKING

from .communication import AgentMessage

if TYPE_CHECKING:
    from app.core.blackboard import CaseBlackboard


@dataclass
class AgentCapability:
    """Agent 能力描述"""
    domain: str
    expertise_level: int
    supported_tasks: List[str]
    required_knowledge: List[str]


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
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.capability = capability
        self.llm_client = llm_client
        self.knowledge_base = knowledge_base
        self.communication_bus = None

    @abstractmethod
    async def analyze(
        self,
        case_data: Dict[str, Any],
        blackboard: Optional['CaseBlackboard'] = None,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def collaborate(
        self,
        other_agents: List['BaseAgent'],
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass

    def register_to_bus(self, communication_bus):
        self.communication_bus = communication_bus

    async def send_message(self, receiver_id: str, content: Dict[str, Any]):
        if self.communication_bus:
            message = AgentMessage(
                sender=self.agent_id,
                receiver=receiver_id,
                message_type="query",
                content=content
            )
            await self.communication_bus.send_message(message)
