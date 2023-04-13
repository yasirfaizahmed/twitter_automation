# flake8: noqa

import cv2
import invoke

invoke.run('scrot test.png')

template = cv2.imread('start_tweet.png')

test = cv2.imread('test.png')

res = cv2.matchTemplate(test, template, cv2.TM_CCOEFF_NORMED)

min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
top_left = max_loc
bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])

cv2.rectangle(test, top_left, bottom_right, (0, 0, 255), 2)
cv2.imwrite('res.png',test)