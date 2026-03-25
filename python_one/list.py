
# from array import array
# jay = array('d')    # ???  不清楚
# jay.append(99)
# print(jay)


person_1 = {}                  #   字典 {}  person{}
person_1['last'] = 'jf'        #   往字典里插值 person[] = ''
person_1['first'] = 'xia'

person_2 = {'first' :'l','last' :'jy' }  
#字典 person = {'first' : 'jx', 'second' : 'yr'} 键值对
print(person_1)
print(person_2)                #  打印字典

people = [person_1]            #  列表[] 往列表里 插字典
print(people)                  #  打印列表

people.append({'aa' : 'bb'})   #  往列表里 拼接字典
people.append({'cc' : 'ee'})   #  往列表里 拼接字典
print(people)                  #  打印列表
print(people[0])               #  索引 打印列表1

presenters = people[0:2]       #  从0开始 数两个
print(presenters)

print(len(presenters))         #  数 数量 2
print(len(people))




