import re
from weather_tool import get_weather
from azure_llm import call_llm
from logger_config import logger
from rag_tool import retrieve_documents
import json
from rag_tool import retrieve_documents


tools = {
    "get_weather": get_weather,
    "retrieve_documents": retrieve_documents,
}

def extract_action(llm_output: str):
    action_match = re.search(r'Action:\s*(.+?)(?:\n|$)', llm_output)
    action_input_match = re.search(r'Action Input:\s*(.+?)(?:\n|$)', llm_output)
    action = action_match.group(1).strip() if action_match else None
    action_input = action_input_match.group(1).strip() if action_input_match else None
    return action, action_input

def parse_action_input(raw_input):
        try:
            d = json.loads(raw_input)
            if 'city' in d:
                return d['city']
            else:
                return raw_input
        except:
            return raw_input

def react_agent(user_input: str, max_steps: int = 4):

    prompt = f"""你是一个智能助手，可以使用以下工具：

1. get_weather(city)  
   - 功能：查询指定城市的实时天气  
   - 参数：城市名称（如“北京”）

2. retrieve_documents(query)  
   - 功能：从我的私人知识库中检索与问题相关的信息  
   - 参数：搜索关键词或短语（如“毕业论文 系统架构”）

用户问题：{user_input}

请严格按照以下格式回答，不要输出任何额外解释：

Thought: 你思考的过程（是否需要调用工具？调用哪个？）
Action: 工具名称（必须是 get_weather 或 retrieve_documents，如果不需要工具则写 None）
Action Input: 工具参数（如果 Action 为 None，则此处留空）
Observation: 工具返回的结果（由系统自动填充，你不需要写这一行）
（如果需要，重复 Thought/Action/Action Input，直到获得足够信息）
Final Answer: 对用户问题的最终回答

重要规则：
- 如果用户问天气，必须调用 get_weather。
- 如果用户问私人笔记、文档、毕业论文等私有知识，必须调用 retrieve_documents。
- 如果用户问其他问题（如闲聊），Action 写 None，直接给出 Final Answer。
- 不要自己编造 Observation，Observation 会由系统提供。
- 每次只调用一个工具，观察结果后再决定下一步。
- 最终答案应基于工具返回的真实数据，不要虚构。
"""
    
    for step in range(max_steps):
        step += 1 
        logger.info(f'--- 第 {step} 次推理 ---')
        llm_output = call_llm(prompt)
        if not llm_output.strip():
            if observation: 
                return observation
            else:
                return "模型未返回有效内容，请重试。"
        #logger.info(f'开始打印LLM输出 \nLLM 输出:\n{llm_output} \nLLM的输出打印结束 ')

        if 'Final Answer:' in llm_output:
            return llm_output.split('Final Answer:')[-1].strip()
        
        action, action_input = extract_action(llm_output) #用正则表达式提取出以Action:和 Action Input: 开头的两行内容。  
        action_input = parse_action_input(action_input)
        if action is None:
            return "错误：模型未指定动作。"
        if action not in tools:
            logger.error(f'错误：未知工具 "{action}"，可用工具：{", ".join(tools.keys())}')
        if action in tools:
            try:
                observation = tools[action](action_input) 
            except Exception as e:
                logger.error(f"工具 {action} 调用失败: {e}")
                observation = f"工具调用失败：{str(e)}"
        prompt += f"\nObservation: {observation}\n"
        logger.error(f"更新后的提示词:\n{prompt}")
        logger.warning(f"达到最大步数 {max_steps}，最后 LLM 输出为:\n{llm_output}")
        continue  
    return '超过最大步数，未能得到最终答案。'

if __name__ == '__main__':
    logger.info('ReAct Agent 启动，输入 \'exit\' 退出')
    while True:
        user_input = input('\n你：')
        logger.debug(f'{user_input}')
        if user_input.lower() == '1':
            break
        answer = react_agent(user_input)
        logger.info(f'Agent：{answer}')