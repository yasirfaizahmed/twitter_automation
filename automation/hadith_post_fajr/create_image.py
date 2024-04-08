"""
Author: Yasir Faiz Ahmed
Contact: yasirfaizahmed.n@gmail.com
Date: April 8, 2024
Description: This is a automation script to post chron based hadith dialy.
"""

from Quote2Image import Convert, GenerateColors


def create_image(content: str, author: str):
	# Generate Fg and Bg Color
	fg, bg = GenerateColors()

	img = Convert(
		quote=content,
		author=author,
		fg=fg,
		bg=bg,
		font_size=32,
		font_type="/home/xd/Documents/python_codes/twitter_automation/resources/fonts/AnotherFlight-m752.ttf",
		width=1080,
		height=450,
		watermark_text="Yasir_f_Ahmed",
	)

	# Save The Image as a Png file
	img.save("_Generated/hello.png")
