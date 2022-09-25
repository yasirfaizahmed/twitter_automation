class Singleton(object):
  instances = {}

  def __new__(cls, *args, **kwargs):
    if cls not in cls.instances:
      cls.instances[cls] = object.__new__(cls)
    return cls.instances[cls]


if __name__ == '__main__':
  class a(Singleton):
    pass

  if a() is a():
    print("{} and {} are the same object".format(a(), a()))
