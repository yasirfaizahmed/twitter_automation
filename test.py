# flake8: noqa



# def singleton(class_):
#     instances = {}
#     def getinstance(*args, **kwargs):
#         if class_ not in instances:
#             instances[class_] = class_(*args, **kwargs)
#         return instances[class_]
#     return getinstance

# @singleton
# class MyClass():
#     pass

# a = MyClass(a=45)



# def dec(fun):
#   def inner(*args, **kwargs):
#     fun(*args, **kwargs)
#     # print(args, kwargs)
#   return inner

# @dec
# def test_fun(g=9):
#   print(g)

# test_fun()

############################## testing login 100 times #########################

# from steps.selenium.selenium_steps import Login
# from scripts.scripts_config import Configs
# import time

# start = time.time()

# for _ in range(100):
#   Login(Config=Configs)()
#   print("{}th login".format(_))

# print("###################### Time took: {}".format(time.time() - start))



############################## testing like #########################
from steps.selenium.selenium_steps import Like, Login
from scripts.scripts_config import Configs
import time

Login(Config=Configs)()
Like(post_url='https://twitter.com/narendramodi/status/1577674742089543680?cxt=HHwWgMDT1bW0g-UrAAAA',
     config=Configs)()
time.sleep(10)
