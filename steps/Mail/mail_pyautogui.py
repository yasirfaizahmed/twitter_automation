__author__ = "yasir faiz ahmed"
__authors__ = ["yasir faiz ahmed"]
__contact__ = "yasirfaizahmed.n@gmail.com"
__copyright__ = "Copyright 2022 TwitterAutomation"
__credits__ = ["yasir"]
__date__ = "28/12/2022"
__deprecated__ = False
__email__ = "yasirfaizahmed.n@gmail.com"
__license__ = ""
__maintainer__ = "developer"
__status__ = "Development"
__version__ = "0.0.1"


import pyautogui
import time
pyautogui.FAILSAFE = False


first = "albert"
last = "einstein"
mail = "alberteinstein456"


def mail_creation_script(first, last, mail):

  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('enter')

  time.sleep(8)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.write(mail)
  time.sleep(3)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('enter')
  time.sleep(0.5)
  for _ in range(5):
    time.sleep(0.5)
    pyautogui.press('down')
  pyautogui.press('enter')
  time.sleep(0.5)

  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('right')
  time.sleep(0.5)

  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.write(first)
  time.sleep(0.5)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.write(last)
  time.sleep(0.5)

  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('enter')
  time.sleep(0.5)
  pyautogui.write("india")
  time.sleep(0.5)
  pyautogui.press('enter')
  time.sleep(0.5)

  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.write("11")
  time.sleep(0.5)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.write("11")
  time.sleep(0.5)
  pyautogui.press('tab')
  time.sleep(0.5)

  pyautogui.write("1991")
  time.sleep(0.5)

  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.write("professorsnipexd28c16")
  time.sleep(0.5)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.write("professorsnipexd28c16")
  time.sleep(0.5)

  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('space')
  time.sleep(0.5)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('space')
  time.sleep(0.5)
  pyautogui.write("professorsnipexd@gmail.com")
  time.sleep(0.5)

  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('enter')
  time.sleep(5)

  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('enter')
  time.sleep(0.5)

  time.sleep(20)
  pyautogui.press('tab')
  time.sleep(0.5)
  pyautogui.press('enter')
  time.sleep(0.5)

  pyautogui.moveTo(2361, 400)
  pyautogui.mouseDown(2361, 400, 'left')
  pyautogui.mouseUp(2361, 400, 'left')
