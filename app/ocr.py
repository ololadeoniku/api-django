import pathlib
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
from PIL import Image

BASE_DIR = pathlib.Path(__file__).parent
IMG_DIR = BASE_DIR / "images"
image_path = IMG_DIR / "Screenshot 2017-09-15 10.59.00.png"

image = Image.open(image_path)

preds = pytesseract.image_to_string(image)

print(preds)