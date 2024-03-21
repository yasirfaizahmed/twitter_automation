from APIs.Selenium.selenium_steps import CollectUserTweetData
from APIs.Selenium.selenium_steps import Login

right = ["zoo_bear", "RoflGandhi_", 'asadowaisi', "dhruv_rathee", "TheDeshBhakt", "khanumarfa", "ShyamMeeraSingh", "_sayema", "Baajis1"]
wrong = ["MrSinha_", "SureshChavhanke", "SushantBSinha", "SushantBSinha", "KapilMishra_IND", "SudarshanNewsTV", "TigerRajaSingh", "noconversion", "TeamHinduOrg"]

Login(botname="default_bot")()


for user in right:
  CollectUserTweetData(user_profile=f"https://twitter.com/{user}", number_of_tweets=5000, file_name=user)()

