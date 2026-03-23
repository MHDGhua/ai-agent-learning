
# sentence = input('what is your name?: ' )
# print(sentence.upper())
# print(sentence.lower())
# print(sentence.capitalize())
# print(sentence.count('t'))


# first_name = 'Xia'
# last_name = 'jf'
# output = f'hello,{first_name} {last_name}'
# print(output)

# output_1 = input('please enter a number_1 :')
# output_2 = input('please enter a number_2 :')
# print(float(output_1) + float(output_2))

from datetime import datetime,timedelta

current_date = datetime.now()  #调用现在时间函数
print('Today is ' + str(current_date))

one_time = timedelta(days=1)
two_time = timedelta(days=2)  #时间差函数

yesterday = current_date - one_time
qian_tian = current_date - two_time
tomorrow = current_date + one_time

print('yesterday is ' + str(yesterday))
print('qian_tian is ' + str(qian_tian))
print('tomorrow is ' + str(tomorrow))

print('day is ' + str(current_date.day)) 
print('mon is ' + str(current_date.month))
print('yesr is ' + str(current_date.year))  

birthday = input('When is you r birthday(dd/mm/yyyy)? : ') #因为是输入字符串，所以需要转换成日期类型
birthday_date = datetime.strptime(birthday, '%d/%m/%Y')  #存储年月日 转换日期类型函数
y_birthday_date = birthday_date - one_time
print('birthday is :' + str(birthday_date))
print('y_birthday is :' + str(y_birthday_date))