import pytesseract
from PIL import Image
import os
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        logging.error(f"Error extracting text from {image_path}: {e}")
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
                text = extract_text(image_path)
                cursor.execute('''INSERT INTO ImageText (filename, text) VALUES (?, ?)''', (filename, text))

        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error processing images: {e}")

# Define the directory containing images and the database path
directory_path = "C:\\Users\\nico_\\Dropbox\\Morne_App\\Source_img"
db_path = 'path_to_your_database.db'

# Process the images and insert text into the database
process_images(directory_path, db_path)
