import os


class CVConfigMeta(type):
  # A metaclass for cvconfigs to set attrs as the file paths of the template icons
  def __new__(cls, name, bases, attrs):
    __td = attrs.get('template_src_dir', None)
    if __td:
      for file in os.scandir(attrs.get('template_src_dir', None)):
        attrs[os.path.basename(file.path).split('.')[0]] = file.path
    new_class = super().__new__(cls, name, bases, attrs)
    return new_class


class CVConfig(metaclass=CVConfigMeta):
  template_src_dir = 'template_images'
