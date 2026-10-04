from APIs.Selenium.selenium_steps import Tweet, Login

# for i in range(10):
# 	Tweet(tweet_content="testing... iter: {}".format(i))()

Login(botname="default_bot")()
Tweet(
	"testing...",
	media_files=["/home/xd/Downloads/moon.jpeg"],
	bot_name="default_bot",
	use_pyautogui=False,
)()
