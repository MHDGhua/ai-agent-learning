
# province = input('enter province :')
# if province == 'jx':
#     tax = .07
# elif province == 'hn':
#     tax = .09
# print(tax)


# province = input('enter province :')
# if province == 'jx' \
#     or province == 'hn':
#     tax = .07
# elif province == 'cq':
#     tax = .09
# print(tax)


# province = input('enter province :')
# if province in('jx','hn','cq'):
#     tax = .07
# elif province == 'xz':
#     tax = .09
# else:
#     tax = 0
# print(tax)

gpa = input('what is your number ? :')
if float(gpa) <= 2 or float(gpa) >= 5:
    honur_roll = False
elif float(gpa) <= 4.9 and float(gpa) >= 2.1:
    honur_roll = True
if honur_roll:
    print('good')