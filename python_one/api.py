import requests
import json
from pathlib import Path

#这里把url删掉了，密钥也删掉了
SUBSCRIPTION_KEY = '1111'
vision_service_address = '2222'
image_path = Path('image') / 'a.png'
image_data = open(image_path,"rb").read()
parameters = {
    'visualFeatures': 'Description,Color',  # 注意：Color首字母大写
    'language': 'en'
}
# ✅ 请求头
headers = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY
}
try:
    # ✅ 使用with语句打开文件（微软推荐）
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    
    print(f"正在分析图片: {image_path}")
    print(f"图片大小: {len(image_data)} 字节")
    
    # ✅ 发送请求
    response = requests.post(
        vision_service_address,
        headers=headers,
        params=parameters,
        data=image_data
    )
    
    # ✅ 检查响应
    response.raise_for_status()
    
    # ✅ 解析结果
    results = response.json()
    print("✅ 分析成功！")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
except FileNotFoundError:
    print(f"❌ 错误：找不到图片文件 {image_path}")
    print("请确认：")
    print("1. 图片文件是否存在？")
    print("2. 路径是否正确？")
    print(f"当前目录: {Path.cwd()}")
    
except requests.exceptions.HTTPError as e:
    print(f"❌ API调用错误: {e}")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
except Exception as e:
    print(f"❌ 其他错误: {e}")