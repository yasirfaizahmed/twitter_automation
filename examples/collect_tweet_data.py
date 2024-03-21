from APIs.Selenium.selenium_steps import CollectUserTweetData
from APIs.Selenium.selenium_steps import Login

Login(botname="default_bot")()

CollectUserTweetData(user_profile=f"https://twitter.com/X", number_of_tweets=5000, file_name='X')()
