import re
from weather_tool import get_weather
from azure_llm import call_llm
from logger_config import logger

# 可用工具字典
tools = {
    'get_weather': get_weather,
}

def extract_action(llm_output: str):
    """从 LLM 输出中解析 Action 和 Action Input"""
    action_match = re.search(r'Action:\s*(.+?)(?:\n|$)', llm_output)
    action_input_match = re.search(r'Action Input:\s*(.+?)(?:\n|$)', llm_output)
    action = action_match.group(1).strip() if action_match else None
    action_input = action_input_match.group(1).strip() if action_input_match else None
    return action, action_input

def react_agent(user_input: str, max_steps: int = 3):

    prompt = f"""你是一个智能助手，可以使用以下工具：

- get_weather(city): 查询指定城市的实时天气。参数 city 为城市名。
- calculator(expression): 计算数学表达式。参数 expression 为字符串，如 "2+3"。

用户问题：{user_input}

请按以下格式回答：
Thought: 你思考的过程
Action: 要调用的工具名称（必须是上述工具之一，如果不需要工具则写 None）
Action Input: 工具的参数（如果 Action 是 None，则此项为空）
Observation: 工具返回的结果（由系统提供，你不需要输出）
（如果需要，重复以上三步，最后输出 Final Answer）
Final Answer: 你的最终回答

注意：Observation 行由系统自动添加，你在回答中不要写 Observation。"""
   
    for step in range(max_steps):
        step += 1 
        logger.info(f'--- 第 {step} 次推理 ---')

        llm_output = call_llm(prompt)
        #print(f"[DEBUG] LLM 输出: {llm_output}")
        logger.info(f'开始打印LLM输出 \nLLM 输出:\n{llm_output} \nLLM的输出打印结束 ')

        if 'Final Answer:' in llm_output:
            #.split() 将字符串按照指定的分隔符 把其中的所有 'Final Answer:' 切割成多个部分，返回一个列表。
            #[-1]索引最后一个元素，也是最终的结果
            #.strip() 移除 字符串首尾的空白字符（包括空格、换行符等）
            return llm_output.split('Final Answer:')[-1].strip()
        
        action, action_input = extract_action(llm_output) #用正则表达式提取出以Action:和 Action Input: 开头的两行内容。  
        if not action:
            logger.info(f'错误：LLM 输出格式不正确，无法解析 Action。')
        if action not in tools:
            logger.info(f'错误：未知工具 "{action}"，可用工具：{", ".join(tools.keys())}')
        
        try:
            observation = tools[action](action_input) # 调用tool字典中 被解析出的action这个函数（get_weather; 并传参为解析出的action_input; 被赋值给 observation，然后被拼接到提示词中，供 LLM 下一轮推理使用。
            logger.info(f'执行工具 {action}({action_input}) -> 观察: {observation}')
        except Exception as e:
            logger.error(f"工具 {action} 调用失败: {e}")
            observation = f"工具调用失败：{str(e)}"
        prompt += f'\n Observation: {observation} \n'
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