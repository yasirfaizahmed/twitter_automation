from APIs.Selenium.selenium_steps import CollectUserTweetData
from APIs.Selenium.selenium_steps import Login

Login(botname="default_bot")()
CollectUserTweetData(user_profile='https://twitter.com/elonmusk', number_of_tweets=50)()
