from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import os

# Configure tesseract path (if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\poppler-24.08.0\Library\bin'  # Update this to your actual Poppler path

def convert_pdf_to_image(pdf_path):
    images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
    image_path = pdf_path.replace(".pdf", "_page1.jpg")
    images[0].save(image_path, 'JPEG')
    return image_path

def check_ocr_fields(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

    text = pytesseract.image_to_string(thresh)

    essential_fields = ['invoice', 'date', 'total', 'tax']
    missing = [field for field in essential_fields if field not in text.lower()]
    passed = len(missing) < 2

    return passed, text, missing

def check_suspicious_keywords(text):
    suspicious_keywords = ['edited', 'fake', 'photoshop', 'clone', 'altered']
    found = [kw for kw in suspicious_keywords if kw in text.lower()]
    passed = len(found) == 0
    return passed, found

def check_ela(image_path, quality=90):
    ela_output = image_path.replace(".jpg", "_ela.jpg")
    original = Image.open(image_path).convert('RGB')
    temp_jpg = image_path.replace(".jpg", "_temp.jpg")
    original.save(temp_jpg, 'JPEG', quality=quality)

    resaved = Image.open(temp_jpg)
    ela_image = ImageChops.difference(original, resaved)

    extrema = ela_image.getextrema()
    max_diff = max([e[1] for e in extrema])
    if max_diff == 0:
        max_diff = 1

    scale = 255.0 / max_diff
    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)
    ela_image.save(ela_output)

    suspicious = max_diff > 20
    passed = not suspicious

    return passed, ela_output

def full_invoice_check(file_path):
    is_pdf = file_path.lower().endswith('.pdf')
    if is_pdf:
        image_path = convert_pdf_to_image(file_path)
    else:
        image_path = file_path

    # Step 1: OCR Field Check
    ocr_passed, text, missing = check_ocr_fields(image_path)
    if not ocr_passed:
        return f"🚫 Invoice failed OCR field check. Missing: {missing}", None

    # Step 2: Suspicious Keyword Check
    keyword_passed, found_keywords = check_suspicious_keywords(text)
    if not keyword_passed:
        return f"🚫 Invoice contains suspicious keywords: {found_keywords}", None

    # Step 3: ELA Forgery Check
    ela_passed, ela_image = check_ela(image_path)
    if not ela_passed:
        return "🚫 Invoice failed Error Level Analysis (possible alteration)", ela_image

    return "✅ Invoice passed all checks and seems authentic.", ela_image
