from openai import OpenAI

# 初始化客户端，指定 DeepSeek 的 base_url
client = OpenAI(
    api_key="sk-xbvHs5kal7MDP5xpiunwjR2X6ViVmMB9ppLMKppsaaBvpf8N",
    base_url="https://api.deepseek.com",
)

# 发送聊天请求
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

# 打印回复内容
print(response.choices[0].message.content)