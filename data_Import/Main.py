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

def extract_text(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        logging.error(f"Error extracting text from {image_path}: {e}")
        return ""

def detect_colored_boxes(image_path):
    try:
        img = cv2.imread(image_path)
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Define color ranges for blue, green, and red boxes
        blue_lower = np.array([100, 100, 100])
        blue_upper = np.array([140, 255, 255])
        green_lower = np.array([35, 100, 100])
        green_upper = np.array([85, 255, 255])
        red_lower1 = np.array([0, 100, 100])
        red_upper1 = np.array([10, 255, 255])
        red_lower2 = np.array([160, 100, 100])
        red_upper2 = np.array([180, 255, 255])

        # Create masks for blue, green, and red
        blue_mask = cv2.inRange(hsv_img, blue_lower, blue_upper)
        green_mask = cv2.inRange(hsv_img, green_lower, green_upper)
        red_mask1 = cv2.inRange(hsv_img, red_lower1, red_upper1)
        red_mask2 = cv2.inRange(hsv_img, red_lower2, red_upper2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)

        # Detect contours for each color
        contours_blue, _ = cv2.findContours(blue_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_green, _ = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_red, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        return contours_blue, contours_green, contours_red
    except Exception as e:
        logging.error(f"Error detecting colored boxes in {image_path}: {e}")
        return [], [], []

def process_images(directory_path, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS Questions (id INTEGER PRIMARY KEY, question TEXT, correct_answer TEXT)''')

        for filename in os.listdir(directory_path):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(directory_path, filename)
                logging.info(f"Processing image: {image_path}\n")
                text = extract_text(image_path)
                contours_blue, contours_green, contours_red = detect_colored_boxes(image_path)

                question = None
                answers = []
                correct_answer = None

                if contours_blue:
                    x, y, w, h = cv2.boundingRect(contours_blue[0])
                    question = text[y:y+h]

                for cnt in contours_green + contours_red:
                    x, y, w, h = cv2.boundingRect(cnt)
                    answer_text = text[y:y+h]
                    if cnt in contours_green:
                        correct_answer = answer_text
                    answers.append(answer_text)
                logging.debug(f"answers: {answers}")
                if question and correct_answer:
                    cursor.execute('''INSERT INTO Questions (question, correct_answer) VALUES (?, ?)''', (question, correct_answer))

        conn.commit()
        conn.close()
        
    except Exception as e:
        logging.error(f"Error processing images: {e}")
    
# Define the directory containing images and the database path
directory_path = "C:\\Users\\nico_\\Dropbox\\Morne_App\\Source_img"
db_path = 'path_to_your_database.db'

# Process the images and insert text into the database
process_images(directory_path, db_path)
