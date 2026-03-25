import re
from first_agent.weather_tool import get_weather
from azure_llm import call_llm

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
    prompt = f'''你是一个智能助手，可以使用以下工具：
- get_weather(city): 查询指定城市的天气

用户问题：{user_input}

请严格按照以下示例的格式回答，每一步都要输出 Thought、Action、Action Input，最后输出 Final Answer。

示例：
用户：北京天气
Thought: 用户想查询北京的天气，我需要使用 get_weather 工具。
Action: get_weather
Action Input: 北京
Observation: 北京 当前天气：晴，温度 23℃
Thought: 我已经得到天气信息，可以回答用户了。
Final Answer: 北京 当前天气：晴，温度 23℃

现在请根据用户问题开始回答，注意只输出格式中的内容，不要输出额外解释。
'''
     
    for step in range(max_steps):
        step = 0
        print(f'\n--- 第 {step+1} 次推理 ---')
        llm_output = call_llm(prompt)
        print(f'LLM 输出:\n{llm_output}')

        if 'Final Answer:' in llm_output:
            #.split() 将字符串按照指定的分隔符 把其中的所有 'Final Answer:' 切割成多个部分，返回一个列表。
            #[-1]索引最后一个元素，也是最终的结果
            #.strip() 移除字符串首尾的空白字符（包括空格、换行符等）
            return llm_output.split('Final Answer:')[-1].strip()

        action, action_input = extract_action(llm_output)
        if not action:
            return '错误：LLM 输出格式不正确，无法解析 Action。'

        if action not in tools:
            return f'错误：未知工具 "{action}"，可用工具：{", ".join(tools.keys())}'

        observation = tools[action](action_input)
        print(f'执行工具 {action}({action_input}) -> 观察: {observation}')
        prompt += f'\nObservation: {observation}\n'
    return '超过最大步数，未能得到最终答案。'

if __name__ == '__main__':
    print('ReAct Agent 启动，输入 \'exit\' 退出')
    while True:
        user_input = input('\n你：')
        if user_input.lower() == 'exit':
            break
        answer = react_agent(user_input)
        print('Agent：', answer)