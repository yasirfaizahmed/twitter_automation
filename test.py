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
from steps.selenium.selenium_steps import Like, Login, LikePosts, RetweetPosts
from scripts.scripts_config import Configs
import time

Login(Config=Configs)()
time.sleep(15)
# Like(post_url='https://twitter.com/Zii_creates/status/1578453689249181697?s=20&t=qgeepYVe_qTvhmBA6W2ZUw',
#      config=Configs)()
# time.sleep(10)


RetweetPosts(user_profile="https://twitter.com/Zii_creates", number_of_posts=1000,
             config=Configs)()


