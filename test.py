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
from steps.selenium.selenium_steps import Like, Login, LikePosts, RetweetPosts, Retweet
# from scripts.scripts_config import Configs
import time

# Like(post_url="https://twitter.com/Zii_creates/status/1607392172357324800", by_all_bots=True)()
Retweet(post_url="https://twitter.com/Zii_creates/status/1607392172357324800", by_all_bots=True)()
Login()()
time.sleep(15)
# Like(post_url='https://twitter.com/Zii_creates/status/1578453689249181697?s=20&t=qgeepYVe_qTvhmBA6W2ZUw',
#      config=Configs)()
# time.sleep(10)


RetweetPosts(user_profile="https://twitter.com/I_am_Based_", number_of_posts=1000)()

################################# testing Logging SocketHandlers #################################
# import logging

# logging.warning("this is a info")
# r = logging.LogRecord(name="TA", level=0,
#                       pathname="",
#                       lineno=0,
#                       msg="hello ", args="", exc_info=None)


# class streamlogging(logging.StreamHandler):

#   def __init_(self, **kwargs):
#     super().__init__(**kwargs)


# fd = open("/home/xd/Documents/Python_codes/twitter_aut/log.txt", 'w')
# sl = streamlogging(stream=fd)
# logger = logging.getLogger(name="TA")



################################# logging filehandler #################
# import logging

# logger = logging.getLogger(name="TA")
# logger.setLevel(level=logging.INFO)

# fh = logging.FileHandler('SPOT.log')
# fh.setLevel(logging.INFO)

# logger.addHandler(fh)

# logger.warning("hello")

