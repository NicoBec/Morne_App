import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import sqlite3

# Function to load a question from the database
def load_question():
    global current_question_id
    # Load the base question from the ImageText table
    cursor.execute("SELECT * FROM ImageText WHERE id=?", (current_question_id,))
    row = cursor.fetchone()
    if row:
        # Clear the text box and reset answers/checkboxes
        question_textbox.delete("1.0", tk.END)
        answer1.set("")
        answer2.set("")
        answer3.set("")
        answer4.set("")
        checkbox1_var.set(False)
        checkbox2_var.set(False)
        checkbox3_var.set(False)
        checkbox4_var.set(False)

        # Get the original question text and image filename from ImageText table
        original_question = row[2]
        image_filename = row[1]
        # Insert the original question into the text area
        question_textbox.insert(tk.END, original_question)
        question_image.set(image_filename)

        # Load and display the image
        try:
            img = Image.open(f"{directory}/{image_filename}")
            img = img.resize((500, 350))  # Enlarge image display
            img_tk = ImageTk.PhotoImage(img)
            image_label.configure(image=img_tk)
            image_label.image = img_tk
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")

        # Check whether CleanedData exists for this question
        cursor.execute("SELECT * FROM CleanedData WHERE question_id=?", (current_question_id,))
        cleaned_data = cursor.fetchone()
        if cleaned_data:
            # cleaned_data layout (if table was created/upgraded as expected):
            # index 0: id, 1: question_id, 2: cleaned_question,
            # 3: answer1, 4: answer2, 5: answer3, 6: answer4, 7: correct_answers
            cleaned_question = cleaned_data[2]
            if cleaned_question:
                question_textbox.delete("1.0", tk.END)
                question_textbox.insert(tk.END, cleaned_question)
            answer1.set(cleaned_data[3] if cleaned_data[3] is not None else "")
            answer2.set(cleaned_data[4] if cleaned_data[4] is not None else "")
            answer3.set(cleaned_data[5] if cleaned_data[5] is not None else "")
            answer4.set(cleaned_data[6] if cleaned_data[6] is not None else "")
            # Check if there is a "correct_answers" column (index 7)
            if len(cleaned_data) > 7 and cleaned_data[7]:
                correct_list = cleaned_data[7].split(',')
            else:
                correct_list = []
            checkbox1_var.set(answer1.get() in correct_list)
            checkbox2_var.set(answer2.get() in correct_list)
            checkbox3_var.set(answer3.get() in correct_list)
            checkbox4_var.set(answer4.get() in correct_list)
    else:
        messagebox.showinfo("Info", "No more questions to load.")

# Function to save the cleaned question text and answers to the database
def save_answers():
    # Get the current (cleaned-up) question text from the editable text widget
    cleaned_question = question_textbox.get("1.0", tk.END).strip()
    correct = []
    answers = [answer1.get(), answer2.get(), answer3.get(), answer4.get()]

    # Check which answer(s) is marked as correct
    if checkbox1_var.get():
        correct.append(answer1.get())
    if checkbox2_var.get():
        correct.append(answer2.get())
    if checkbox3_var.get():
        correct.append(answer3.get())
    if checkbox4_var.get():
        correct.append(answer4.get())

    if not correct:
        messagebox.showwarning("Warning", "Please mark at least one correct answer!")
        return

    # Save the cleaned question along with the answers and correct answers
    cursor.execute("""
        INSERT OR REPLACE INTO CleanedData 
            (question_id, cleaned_question, answer1, answer2, answer3, answer4, correct_answers)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (current_question_id, cleaned_question, answers[0], answers[1], answers[2], answers[3], ','.join(correct)))
    conn.commit()

    messagebox.showinfo("Success", "Question and answers saved successfully!")

# Function to move to the next question
def next_question():
    global current_question_id
    current_question_id += 1
    load_question()

# Function to move to the previous question
def previous_question():
    global current_question_id
    if current_question_id > 1:
        current_question_id -= 1
        load_question()
    else:
        messagebox.showinfo("Info", "This is the first question.")

# Set up the database by prompting the user for the DB file and the directory containing images
db_path = filedialog.askopenfilename(title="Select the database file")
directory = filedialog.askdirectory(title="Select the directory containing images")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the CleanedData table if it doesn't already exist.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS CleanedData (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER UNIQUE,
        cleaned_question TEXT,
        answer1 TEXT,
        answer2 TEXT,
        answer3 TEXT,
        answer4 TEXT,
        correct_answers TEXT
    )
""")
conn.commit()

# Initialize the GUI
root = tk.Tk()
root.title("Question Data Cleaner")

# Label for the question
tk.Label(root, text="Question:").grid(row=0, column=0, sticky="w")
# Update the text area to be 15 lines by 100 columns
question_textbox = tk.Text(root, height=15, width=100, wrap="word")
question_textbox.grid(row=0, column=1, columnspan=3)

# Image display
question_image = tk.StringVar()
image_label = tk.Label(root)
image_label.grid(row=1, column=0, columnspan=4)

# Answer input fields and corresponding checkboxes
answer1 = tk.StringVar()
answer2 = tk.StringVar()
answer3 = tk.StringVar()
answer4 = tk.StringVar()

tk.Label(root, text="Answer 1:").grid(row=2, column=0, sticky="w")
tk.Entry(root, textvariable=answer1, width=30).grid(row=2, column=1)
checkbox1_var = tk.BooleanVar()
tk.Checkbutton(root, variable=checkbox1_var).grid(row=2, column=2)

tk.Label(root, text="Answer 2:").grid(row=3, column=0, sticky="w")
tk.Entry(root, textvariable=answer2, width=30).grid(row=3, column=1)
checkbox2_var = tk.BooleanVar()
tk.Checkbutton(root, variable=checkbox2_var).grid(row=3, column=2)

tk.Label(root, text="Answer 3:").grid(row=4, column=0, sticky="w")
tk.Entry(root, textvariable=answer3, width=30).grid(row=4, column=1)
checkbox3_var = tk.BooleanVar()
tk.Checkbutton(root, variable=checkbox3_var).grid(row=4, column=2)

tk.Label(root, text="Answer 4:").grid(row=5, column=0, sticky="w")
tk.Entry(root, textvariable=answer4, width=30).grid(row=5, column=1)
checkbox4_var = tk.BooleanVar()
tk.Checkbutton(root, variable=checkbox4_var).grid(row=5, column=2)

# Navigation and Save buttons
tk.Button(root, text="Save Question and Answers", command=save_answers).grid(row=6, column=0)
tk.Button(root, text="Next Question", command=next_question).grid(row=6, column=1)
tk.Button(root, text="Previous Question", command=previous_question).grid(row=6, column=2)

# Start with the first question (ID = 1)
current_question_id = 1
load_question()

# Start the GUI event loop
root.mainloop()
