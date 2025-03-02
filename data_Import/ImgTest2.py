import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import os
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    try:
        img = Image.open(image_path)
        # Convert image to grayscale
        img = img.convert('L')
        # Apply sharpening filter
        img = img.filter(ImageFilter.SHARPEN)
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2)
        return img
    except Exception as e:
        logging.error(f"Error preprocessing image {image_path}: {e}")
        return None

def extract_text(image):
    try:
        # Configure Tesseract
        custom_config = r'--oem 3 --psm 6 -l eng' #--dpi 300
        text = pytesseract.image_to_string(image, config=custom_config)
        return text
    except Exception as e:
        logging.error(f"Error extracting text: {e}")
        return ""

def process_images(directory_path, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS ImageText (id INTEGER PRIMARY KEY, filename TEXT, text TEXT)''')

        for filename in os.listdir(directory_path):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(directory_path, filename)
                logging.info(f"Processing image: {image_path}")
                preprocessed_image = preprocess_image(image_path)
                if preprocessed_image:
                    text = extract_text(preprocessed_image)
                    cursor.execute('''INSERT INTO ImageText (filename, text) VALUES (?, ?)''', (filename, text))

        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error processing images: {e}")

# Define the directory containing images and the database path
directory_path = "C:\\Users\\nico_\\Dropbox\\Morne_App\\Source_img"
db_path = 'Question_DB.db'

# Process the images and insert text into the database
process_images(directory_path, db_path)
