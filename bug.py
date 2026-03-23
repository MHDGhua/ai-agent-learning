x = 42
y = 0
try:
     print(x / y)
except ZeroDivisionError as e:
     print('cannot be zero')
else:
    print('finally')
finally:
     pass
