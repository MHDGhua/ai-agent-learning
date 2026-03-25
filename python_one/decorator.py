def logger(func):
    def wrapper():
        print('logging execution')
        func()
        print('done logging')
    return wrapper

@logger
def sample():
    print('--inside sample function')

sample()