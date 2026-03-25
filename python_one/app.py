import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 获取环境变量
password = os.getenv('PASSWORD')
print(password)