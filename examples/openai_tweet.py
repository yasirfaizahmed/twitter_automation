from APIs.Selenium.selenium_steps import OpenaiTweet


OpenaiTweet(
	user_prompt="generate inspirational quote on tags like",
	tags=["hardworking", "godfearing", "teritorial jealousy"],
	by_all_bots=False,
	as_image=True,
)()
