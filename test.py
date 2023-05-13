# flake8: noqa

# import cv2
# import invoke

# invoke.run('scrot test.png')

# template = cv2.imread('start_tweet.png')

# test = cv2.imread('test.png')

# res = cv2.matchTemplate(test, template, cv2.TM_CCOEFF_NORMED)

# min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
# top_left = max_loc
# bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])

# cv2.rectangle(test, top_left, bottom_right, (0, 0, 255), 2)
# cv2.imwrite('res.png',test)

# from log_handling.log_handling import fun
# fun()

############# testing likes ##############
# from steps.Selenium.selenium_steps import ReportProfile
# for _ in range(5):
#     ReportProfile(user_profile='url to a profile', report_category='')()


# ############# testing geticoncoordinates cv API ########
# from steps.CV.cv_steps import GetIconCoordinates

# GetIconCoordinates(icon_name='tweet_button', threshold=0.9, debug_mode=True)()


############## testing selenium_steps.Tweet ##############
# from steps.Selenium.selenium_steps import Tweet

# from scripts.scripts_config import BotMetadata

# bnd = BotMetadata()


