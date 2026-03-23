# 模拟用户输入（可以修改这里的文字测试不同场景）
user_message = "北京天气"

# 定义工具列表
tools = ["天气查询", "计算器", "时间查询"]

# 模拟一个简单的意图识别1
if "天气" in user_message:
    selected_tool = tools[0]
    print(f"Agent决定调用：{selected_tool}")
    # 模拟调用天气API（这里仅打印）
    print("调用天气API，获取北京天气...")
    result = "晴天，25度"
elif "计算" in user_message:
    selected_tool = tools[1]
    print(f"Agent决定调用：{selected_tool}")
    result = "计算结果：42"
elif "时间" in user_message:
    selected_tool = tools[2]
    print(f"Agent决定调用：{selected_tool}")
    result = "当前时间：14:30"
else:
    selected_tool = None
    result = "我不理解，请重新输入"

# 输出最终回复
print(f"Agent回复：{result}")
