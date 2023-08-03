class Logger:
	iteration = 0
	shown = True
	
	def __init__(self, format_color: tuple[int, int, int] = (255, 50, 50), bold: bool = True):
		self.format_color = format_color
		self.bold = bold
		# turn the format color into an ansi escape code
		self.format_code = "\033[38;2;{};{};{}m".format(*format_color)
		# add bold if needed
		if bold: self.format_code += "\033[1m"
		# add the escape code
		self.escape_code = "\033[0m"
	
	def __call__(self, _message: any, _raise: bool = False) -> None:
		if not Logger.shown: return
		# print the message to the console
		Logger.iteration += 1
		if _raise: raise Exception(_message)
		print(f"{self.format_code}{Logger.iteration}: {str(_message)}{self.escape_code}")
	
	@classmethod
	def reset(cls) -> None:
		cls.iteration = 0
	
	@classmethod
	def hide(cls) -> None:
		cls.shown = False
	
	@classmethod
	def show(cls) -> None:
		cls.shown = True
	
	@classmethod
	def toggle(cls) -> None:
		cls.shown = not cls.shown
	
	@classmethod
	def log_if_not_shown(cls, _message: str, color = (255, 255, 255)) -> None:
		color_prefix = "\033[38;2;{};{};{}m".format(*color)
		color_suffix = "\033[0m"
		if not cls.shown:
			print(f"{color_prefix}{_message}{color_suffix}")
