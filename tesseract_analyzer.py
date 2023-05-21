from PIL import Image
import pytesseract
import os

class TextAnalyzer:
	def __init__(self):
		pass

	def analyze_text(self, image):
		return_str = "Invalid image, nothing found!"
		if os.path.isfile(image):
			return_str = pytesseract.image_to_string(Image.open(image))
		return return_str