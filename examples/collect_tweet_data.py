from APIs.Selenium.selenium_steps import CollectUserTweetData
from APIs.Selenium.selenium_steps import Login

Login(botname="default_bot")()

# CollectUserTweetData(user_profile="https://twitter.com/MrSinha_", number_of_tweets=500)()
CollectUserTweetData(user_profile="https://twitter.com/SureshChavhanke", number_of_tweets=500)()
CollectUserTweetData(user_profile="https://twitter.com/SushantBSinha", number_of_tweets=500)()
CollectUserTweetData(user_profile="https://twitter.com/KapilMishra_IND", number_of_tweets=500)()
CollectUserTweetData(user_profile="https://twitter.com/SudarshanNewsTV", number_of_tweets=500)()

CollectUserTweetData(user_profile="https://twitter.com/TigerRajaSingh", number_of_tweets=500)()
CollectUserTweetData(user_profile="https://twitter.com/noconversion", number_of_tweets=500)()
CollectUserTweetData(user_profile="https://twitter.com/TeamHinduOrg", number_of_tweets=500)()
