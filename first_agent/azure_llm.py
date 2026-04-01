import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
load_dotenv()  #加载环境变量

ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
API_KEY = os.getenv('AZURE_OPENAI_KEY')
DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT')
client = AzureOpenAI(    #AzureOpenAI的配置
    azure_endpoint=ENDPOINT,
    api_key=API_KEY,
    api_version="2024-12-01-preview"
)
#把问题交给大模型之后，内部就不管了，让他自己给我们返回的答案，这是他自身的算法给的
#重试
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm(prompt: str) -> str:  #调用模型的函数：prompt 是用户输入的内容、上下文提示
    if not all([ENDPOINT, API_KEY, DEPLOYMENT_NAME]):
        return ' 错误:Azure OpenAI配置不完整'
    print(f"[DEBUG] call_llm 收到的 prompt 长度: {len(prompt)}")
    print(f"[DEBUG] prompt 前 200 字符: {prompt[:200]}")
    try:
        response = client.chat.completions.create(  #向大模型发送一个聊天请求;   API规定 响应参数格式
            model=DEPLOYMENT_NAME,
            messages=[
                {'role':'system',  'content': '你是一个智能助手，能够根据用户问题决定使用工具并回答。'}, #设置AI助手的规则
                {'role':'user', 'content': prompt}  
            ],
            max_completion_tokens=1500  
        ) 
        content = response.choices[0].message.content
        print(f"[DEBUG] 模型返回内容长度: {len(content)}")
        print(f"[DEBUG] 模型返回内容: {content}")
        return content # .choices 是一个列表，包含模型生成的一个或多个候选回复,表示选第一个答案[0]。通常情况下只有一个（除非你在请求中设置了 n 参数大于 1）。
    except Exception as e:
        print(f"[DEBUG] 调用异常: {e}")
        raise   # 让 tenacity 捕获重试
    


#测试 逻辑是：
#当这个文件直接被运行时，_name_会被自动赋值为_main_,所以等式成立，执行打印 
#当文件被导入时，_name_被赋值为文件名，等式不成立，不执行打印 
#_x_两个下划线是内置变量的含义
if __name__ == '__main__':
    print(call_llm('重庆的天气'))


