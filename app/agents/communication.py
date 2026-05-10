"""
Agent 通信机制
"""

import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AgentMessage:
    """Agent 消息格式"""
    sender: str               # 发送者 Agent ID
    receiver: str             # 接收者 Agent ID  
    message_type: str         # 消息类型：query, response, broadcast
    content: Dict[str, Any]  # 消息内容
    priority: int = 1         # 优先级 (1-5, 1最高)
    requires_response: bool = False  # 是否需要回复


class AgentCommunicationBus:
    """Agent 通信总线"""
    
    def __init__(self):
        self.agents = {}  # agent_id -> Agent实例
        self.message_queue = asyncio.Queue()
        self.message_handlers = {}
        
        # 启动消息分发协程
        asyncio.create_task(self._message_dispatcher())
    
    async def register_agent(self, agent: 'BaseAgent'):
        """注册 Agent"""
        self.agents[agent.agent_id] = agent
        agent.register_to_bus(self)
    
    async def send_message(self, message: AgentMessage):
        """发送消息"""
        await self.message_queue.put(message)
    
    async def broadcast(self, sender: str, content: Dict[str, Any], priority: int = 3):
        """广播消息"""
        for agent_id in self.agents:
            if agent_id != sender:
                message = AgentMessage(
                    sender=sender,
                    receiver=agent_id,
                    message_type="broadcast",
                    content=content,
                    priority=priority
                )
                await self.send_message(message)
    
    async def _message_dispatcher(self):
        """消息分发器"""
        while True:
            message = await self.message_queue.get()
            receiver = self.agents.get(message.receiver)
            
            if receiver:
                # 根据消息类型调用不同的处理函数
                if message.message_type == "query":
                    asyncio.create_task(
                        receiver.handle_query(message.sender, message.content)
                    )
                elif message.message_type == "response":
                    asyncio.create_task(
                        receiver.handle_response(message.sender, message.content)
                    )
                elif message.message_type == "broadcast":
                    asyncio.create_task(
                        receiver.handle_broadcast(message.sender, message.content)
                    )
            
            self.message_queue.task_done()
    
    def register_message_handler(self, message_type: str, handler: callable):
        """注册自定义消息处理器"""
        self.message_handlers[message_type] = handler
    
    async def handle_custom_message(self, message: AgentMessage):
        """处理自定义消息"""
        handler = self.message_handlers.get(message.message_type)
        if handler:
            await handler(message)