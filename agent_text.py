
#模拟agent
user_message = input('你想查询什么？')
tool = ['天气查询','时间查询','播放音乐']

if '天气' in user_message:
    print('正在查询当前天气······')
    selected_tool = tool[0] 
    result = {'北京':'23摄氏度'}
    print(result)

elif'时间' in user_message:
    selected_tool = tool[1] 
    result = {'上海':'2026-3-23-23.17'}
    print(result)

elif'音乐' in user_message:
    selected_tool = tool[2] 
    result = {'网易云':'一直很安静'}
    print(result)

else:
    print('抱歉')
    print('done')