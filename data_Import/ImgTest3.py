import pytesseract
from PIL import Image
import cv2
import numpy as np
import os
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        # Apply Gaussian blur to reduce noise
        img = cv2.GaussianBlur(img, (5, 5), 0)
        # Apply adaptive thresholding to enhance contrast
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        # Apply dilation and erosion to enhance text clarity
        kernel = np.ones((2, 2), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)
        return img
    except Exception as e:
        logging.error(f"Error preprocessing image {image_path}: {e}")
        return None

def extract_text(image):
    try:
        # Configure Tesseract
        custom_config = r'--oem 3 --psm 6'
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
                if preprocessed_image is not None:
                    text = extract_text(preprocessed_image)
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
