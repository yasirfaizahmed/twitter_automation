# references:
# 1. https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
# 2. https://stackoverflow.com/questions/9187388/possible-to-prevent-init-from-being-called
# 3. https://stackoverflow.com/questions/58386188/how-to-not-run-init-based-on-new-method

class Singleton(type):
  instances = {}

  def __call__(cls, *args, **kwargs):
    if cls not in cls.instances:
      cls.instances[cls] = cls.__new__(cls, *args, **kwargs)    # obj = cls.__new__(cls, *args, **kwargs)
      if isinstance(cls.instances[cls], cls):
        cls.instances[cls].__init__(*args, **kwargs)
    elif kwargs.get('_run_init', None) is not None:
      if isinstance(cls.instances[cls], cls):
        del kwargs['_run_init']
        cls.instances[cls].__init__(*args, **kwargs)

    return cls.instances[cls]


if __name__ == '__main__':
  class A(metaclass=Singleton):
    def __init__(self):
      print("init 'A' runs :(")

  a1 = A()   # init runs
  a2 = A()   # init will not run

  a3 = A(_run_init=True)   # init will run

  print(a1 is a2 is a3)    # True

  print(id(a1) == id(a2) == id(a3))    # True
