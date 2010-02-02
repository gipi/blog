import re

def slugify(value):
	return re.compile(r"[ _'`]").sub('-', value).lower()
