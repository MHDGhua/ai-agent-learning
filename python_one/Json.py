import json

person_dict = {'first':'x','last':'jf'}
print('在字典中插入键值对:')
person_dict['city'] = 'nc'   #在字典中 插入 键值对

person_json = json.dumps(person_dict)  #json是一种字典，把字典转为json格式
print(person_json)
print(person_json[0])

language_list = ['c','java','c++']
print('在字典中插入列表:')
person_dict['language'] = language_list  #在字典中 插入 列表

print(person_dict)

staff_dict = {'name1':'zs','name2':'ls','name3':'ww'}
# staff_dict = {}
print('在字典中插入字典:')
staff_dict['program'] = person_dict  #在字典中 插入 字典
person_json = json.dumps(staff_dict)
print(staff_dict)
