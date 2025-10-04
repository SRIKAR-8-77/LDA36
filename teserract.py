import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np

# Set the path to your Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\srikar Reddy\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def ocr_from_pdf(pdf_path):

    try:
        print("Converting PDF pages to images...")
        images = convert_from_path(pdf_path, dpi=300)
        
        if not images:
            return "Could not convert PDF to image. Is the PDF valid?"

        full_text = "" 

        for i, pil_image in enumerate(images):
            print(f"--- Processing Page {i + 1} ---")
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

            print("Pre-processing image...")
            gray_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            _, threshold_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            print("Extracting text with Tesseract OCR...")
            extracted_text = pytesseract.image_to_string(threshold_image)
            full_text += f"--- Page {i + 1} ---\n" + extracted_text + "\n\n"
        
        return full_text

    except Exception as e:
        return f"An error occurred: {e}"
