
# def get_initial(name):
#     initial = name[0:10]
#     return initial
# first_name = input('please enter your first name :')
# last_name = input('please enter your last name :')

# print(get_initial(first_name))
# print(get_initial(last_name))

# print(get_initial(first_name)+get_initial(last_name))


from datetime import datetime 
index = 0

def print_time(index):
    print('NO.',index)
    print(datetime.now())
    print()

first_name = 'x'

for index in range(0,10):
    print_time(index)
