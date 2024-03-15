from APIs.Selenium.selenium_steps import Tweet

for i in range(10):
	Tweet(tweet_content="testing... iter: {}".format(i))()
