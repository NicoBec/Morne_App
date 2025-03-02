import sqlite3
import re

def parse_text_column(text):
    """Parse the text into question number, question text, and four answers."""
    lines = text.split('\n')  # Split the text into lines
    lines = [line.strip() for line in lines if line.strip()]  # Remove blank lines and strip whitespace
    
    if not lines:
        raise ValueError("Error: Text column is empty or improperly formatted.")
    
    # Extract the question number from the first line
    question_number = lines[0]
    
    # Find the question text (lines ending with a '?')
    question_lines = []
    i = 1
    while i < len(lines) and not lines[i].endswith('?'):
        question_lines.append(lines[i])
        i += 1
    if i < len(lines) and lines[i].endswith('?'):
        question_lines.append(lines[i])
        i += 1
    question_text = ' '.join(question_lines)  # Combine question lines into a single string
    
    # Extract four answers
    answers = []
    while i < len(lines) and len(answers) < 4:
        if lines[i].strip():
            answers.append(lines[i].strip())
        i += 1
    
    if len(answers) != 4:
        raise ValueError(f"Error: Expected 4 answers, but found {len(answers)} in text:\n{text}")
    
    return question_number, question_text, *answers

def create_cleaned_data_table(db_path):
    """Create a table for cleaned data if it doesn't already exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the CleanedData table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CleanedData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER UNIQUE,
            question_number TEXT,
            cleaned_question TEXT,
            answer1 TEXT,
            answer2 TEXT,
            answer3 TEXT,
            answer4 TEXT
        )
    """)
    conn.commit()
    conn.close()

def process_imagetext_table(db_path):
    """Process the ImageText table and extract questions and answers."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch all rows from the ImageText table
    cursor.execute("SELECT id, text FROM ImageText")
    rows = cursor.fetchall()
    
    # Prepare to insert parsed data
    cleaned_data = []
    
    for row in rows:
        row_id, text = row
        try:
            # Parse the text column
            question_number, question_text, answer1, answer2, answer3, answer4 = parse_text_column(text)
            cleaned_data.append((row_id, question_number, question_text, answer1, answer2, answer3, answer4))
        except Exception as e:
            print(f"Skipping row {row_id} due to error: {e}")
    
    # Insert cleaned data into the CleanedData table
    for data in cleaned_data:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO CleanedData 
                (question_id, question_number, cleaned_question, answer1, answer2, answer3, answer4)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, data)
        except sqlite3.IntegrityError as e:
            print(f"Failed to insert data for row ID {data[0]}: {e}")
    
    conn.commit()
    conn.close()

def main():
    # Prompt the user for the database path
    db_path = input("Enter the path to the SQLite database file: ")
    
    # Create the cleaned data table if it doesn't exist
    create_cleaned_data_table(db_path)
    
    # Process the ImageText table to clean and extract data
    process_imagetext_table(db_path)
    print(f"Processing complete. Cleaned data has been saved to the database at {db_path}.")

if __name__ == "__main__":
    main()
