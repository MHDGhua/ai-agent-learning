import re
from weather_tool import get_weather
from azure_llm import call_llm
from logger_config import logger
from rag_tool import retrieve_documents
import json

# 可用工具字典
tools = {
    "get_weather": get_weather,
    "retrieve_documents": retrieve_documents,
}

def extract_action(llm_output: str):
    """从 LLM 输出中解析 Action 和 Action Input"""
    action_match = re.search(r'Action:\s*(.+?)(?:\n|$)', llm_output)
    action_input_match = re.search(r'Action Input:\s*(.+?)(?:\n|$)', llm_output)
    action = action_match.group(1).strip() if action_match else None
    action_input = action_input_match.group(1).strip() if action_input_match else None
    return action, action_input

def parse_action_input(raw_input):
        try:
        # 尝试解析为 JSON
            d = json.loads(raw_input)
            if 'city' in d:
                return d['city']
            else:
                return raw_input
        except:
            return raw_input

def react_agent(user_input: str, max_steps: int = 3):

    prompt = f"""你是一个智能助手，可以使用以下工具：

    - get_weather(city): 查询指定城市的实时天气。参数 city 为城市名（例如 "北京"、"上海"）。
    - retrieve_documents(query): 从你的个人知识库中检索与 query 最相关的文档片段，用于回答需要私有知识的问题。

    用户问题：{user_input}

    请严格按照以下格式回答，每一步都要输出 Thought、Action、Action Input，最后输出 Final Answer。注意 Action Input 必须是工具要求的参数格式（如城市名直接写，不要加引号或 JSON）。

    示例：
    用户：北京天气
    Thought: 用户想查询北京的天气，我需要使用 get_weather 工具。
    Action: get_weather
    Action Input: 北京
    Observation: 北京 当前天气：晴，温度 23℃
    Thought: 我已经得到天气信息，可以回答用户了。
    Final Answer: 北京 当前天气：晴，温度 23℃

    现在请根据用户问题开始回答，不要输出 Observation 行，Observation 将由系统自动添加。
    示例：
    用户：北京天气
    Thought: 用户想查询北京的天气，我需要使用 get_weather 工具。
    Action: get_weather
    Action Input: 北京
"""
    
    for step in range(max_steps):
        step += 1 
        logger.info(f'--- 第 {step} 次推理 ---')

        llm_output = call_llm(prompt)
        if not llm_output.strip():
            # 如果第二轮输出为空，且已经执行过工具，则返回最后一次观察结果
            if observation:   # 注意：你需要保存最后一次的 observation 变量
                return observation
            else:
                return "模型未返回有效内容，请重试。"
        #print(f"[DEBUG] LLM 输出: {llm_output}")
        logger.info(f'开始打印LLM输出 \nLLM 输出:\n{llm_output} \nLLM的输出打印结束 ')

        if 'Final Answer:' in llm_output:
            #.split() 将字符串按照指定的分隔符 把其中的所有 'Final Answer:' 切割成多个部分，返回一个列表。
            #[-1]索引最后一个元素，也是最终的结果
            #.strip() 移除 字符串首尾的空白字符（包括空格、换行符等）
            return llm_output.split('Final Answer:')[-1].strip()
        
        action, action_input = extract_action(llm_output) #用正则表达式提取出以Action:和 Action Input: 开头的两行内容。  
        action_input = parse_action_input(action_input)
        if action is None:
            return "错误：模型未指定动作。"
        if action not in tools:
            logger.info(f'错误：未知工具 "{action}"，可用工具：{", ".join(tools.keys())}')
        if action in tools:
            try:
                observation = tools[action](action_input) # 调用tool字典中 被解析出的action这个函数（get_weather; 并传参为解析出的action_input; 被赋值给 observation，然后被拼接到提示词中，供 LLM 下一轮推理使用。
                logger.info(f'执行工具 {action}({action_input}) -> 观察: {observation}')
            except Exception as e:
                logger.error(f"工具 {action} 调用失败: {e}")
                observation = f"工具调用失败：{str(e)}"
        prompt += f"\nObservation: {observation}\n"
        prompt += "请根据上述观察结果，直接输出 Final Answer，不要再重复 Thought、Action 等步骤。\n"
        continue   # 继续循环，让模型生成 Final Answer
        logger.debug(f"更新后的提示词:\n{prompt}")
    logger.warning(f"达到最大步数 {max_steps}，最后 LLM 输出为:\n{llm_output}")
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