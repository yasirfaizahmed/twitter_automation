"""
Author: Andrew Dunai <andrew@dun.ai>
Original code & symbol collection: Changaco <https://changaco.oy.lc/unicode-progress-bars/>
Example GIF: https://habrastorage.org/files/c28/461/630/c28461630bdf46d18be788352a2ef468.gif
Example screenshot: http://public.dun.ai/public/screenshots/148456797191.jpg (left & right widget)
>>> print progress(1, 100, 42, 10)
⎹████▂▁▁▁▁▁⎸
>>> print progress(1, 10, 3, 20, style=1)
⎹⣿⣿⣿⣿⣦⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⎸
>>> print progress(50, 100, 80, 10, style=16)
⎹██████▏▏▏▏⎸
>>> print progress(1, 5, 4.2, 15, style=4, before='<', after='>')
<■■■■■■■■■■■■□□□>
>>> print progress(0.1, 1.0, 0.42, 10, style=6, before='[', after=']')
[■■■▩□□□□□□]
>>> print progress(1, 100, 34, 5, style=6, before='Battery: ', after='')
Battery: ■▩□□□
"""

bar_styles = [
	"▁▂▃▄▅▆▇█",
	"⣀⣄⣤⣦⣶⣷⣿",
	"⣀⣄⣆⣇⣧⣷⣿",
	"○◔◐◕⬤",
	"□◱◧▣■",
	"□◱▨▩■",
	"□▨▩■",
	"□◱▥▦■",
	"░▒▓█",
	"░█",
	"⬜⬛",
	"▱▰",
	"▭◼",
	"▯▮",
	"◯⬤",
	"⚪⚫",
	"▏▎▍▌▋▊▉█",
]


def progress(min, max, current, width, style=0, before="⎹", after="⎸"):
	"""
	:param min: minimum (starting) bar value
	:param max: maximum (ending) bar value
	:param current: current bar progress value
	:param width: size of resulting bar in characters (excluding `before` and `after`)
	:param style: index of palette, `0 <= style < len(bar_styles)`
	:param before: string to prepend to result
	:param after: string  to append to result
	:return: string of length `width + len(before) + len(after)`
	"""
	style = bar_styles[style]
	q_max = len(style) * width
	ratio = float(current - min) / (max - min)
	q_current = int(ratio * q_max)
	return (
		before
		+ "".join(
			[
				style[-1]
				if x <= q_current
				else style[q_current - x]
				if x - q_current < len(style)
				else style[0]
				for x in [y * len(style) for y in range(1, width + 1)]
			]
		)
		+ after
	)
