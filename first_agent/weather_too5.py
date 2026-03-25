#这是一个天气调用函数，调用的是Azure的天气API

import os
import requests
from dotenv import load_dotenv

#加载环境变量
load_dotenv()

#用os.getenv()获取环境变量中的天气密钥
AZURE_MAPS_KEY = os.getenv('AZURE_MAPS_KEY')

#官方文档的标准API接口
WEATHER_URL = "https://atlas.microsoft.com/weather/currentConditions/json"
CITY_COORDS = {
    "北京": "39.9042,116.4074",
    "上海": "31.2304,121.4737",
    "广州": "23.1291,113.2644",
    "深圳": "22.5431,114.0579",
    }

def get_weather(city: str) -> str:
  
   #检查API密钥
    if not AZURE_MAPS_KEY:
        return "错误：未配置 Azure Maps 密钥，请在 .env 文件中设置 AZURE_MAPS_KEY" 
    #获取城市坐标
    coord = CITY_COORDS.get(city)
    if not coord:
        supported = "、".join(CITY_COORDS.keys())
        return f"暂不支持城市 {city}，目前支持：{supported}" 
    #构造API请求
    #需要什么参数就在API文档里面看，自己构建参数头
    params = {
        "query": coord,               # 经纬度
        "api-version": "1.0",         # API 版本
        "subscription-key": AZURE_MAPS_KEY,
        "unit": "metric"              # 单位：摄氏度
    }
    try:     
        #向API 发送GET请求 标准格式：requests.get(URL, params=参数, timeout=超时秒数)
        resp = requests.get(WEATHER_URL, params=params, timeout=5)
        #防御性检查，与except配套，负责检查 HTTP 状态码
        resp.raise_for_status()       # 如果状态码不是 200，抛出异常
        #解析返回的JSON
        data = resp.json()   
        #请求的参数有什么，就查什么
        #results是文档规定了的键， data['results'] 是取results的数据，且判断不为空 
        if 'results' in data and data['results']:
            #results是一个键，他的值是一个列表，列表的第一个数据是一个字典a
            r = data['results'][0]
            #取字典a的键temperature,他的值又是一个字典，所以需要再用.get(value)
            temp = r.get('temperature', {}).get('value')
            #防御性写法，如果phrase不存在，则返回'未知'
            phrase = r.get('phrase', '未知')
            #f-string格式，字符串中可以插数值
            return f'{city} 当前天气：{phrase}，温度 {temp}℃'
        else:
            return f'未查到 {city} 的天气信息'    
    #捕获网络异常   
    except requests.exceptions.RequestException as e:
        return f'天气查询失败（网络请求错误）：{str(e)}'
    except Exception as e:
        return f'天气查询失败：{str(e)}'
    
if __name__ == "__main__":
    print(get_weather("北京"))