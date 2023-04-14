# references:
# 1. https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
# 2. https://stackoverflow.com/questions/9187388/possible-to-prevent-init-from-being-called
# 3. https://stackoverflow.com/questions/58386188/how-to-not-run-init-based-on-new-method

class Singleton(type):
  instances = {}

  def __call__(cls, *args, **kwargs):
    if cls not in cls.instances:
      cls.instances[cls] = cls.__new__(cls, *args, **kwargs)    # obj = cls.__new__(cls, *args, **kwargs)
    if kwargs.get('skip_init', None) is None:
      if isinstance(cls.instances[cls], cls):
        cls.instances[cls].__init__(*args, **kwargs)

    return cls.instances[cls]


if __name__ == '__main__':
  class A(metaclass=Singleton):
    def __init__(self):
      print("init 'A' runs :(")

  if A() is A(skip_init=True):
    print("{} and {} are the same object".format(a(), a()))
