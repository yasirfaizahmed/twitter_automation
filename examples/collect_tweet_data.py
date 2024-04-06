from APIs.Selenium.selenium_steps import Login
from APIs.Selenium.selenium_steps import CollectUserTweetData

Login(botname="default_bot")()
CollectUserTweetData(user_profile="elonmusk",
                     number_of_tweets=6000,
                     file_format="csv",
                     file_name="elonmusk")()