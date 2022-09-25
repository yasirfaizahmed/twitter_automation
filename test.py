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



def dec(fun):
  def inner(*args, **kwargs):
    fun(*args, **kwargs)
    # print(args, kwargs)
  return inner

@dec
def test_fun(g=9):
  print(g)

test_fun()
