import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os

# Configurable database and image folder
db_name = "Question_DB.db"
image_folder = filedialog.askdirectory(title="Select Image Folder")

# Database connection
def get_questions():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT ImageText.id, ImageText.filename, text FROM ImageText JOIN CleanedData on CleanedData.question_id = ImageText.id ORDER BY fixed ASC, ImageText.id ASC")
    data = cursor.fetchall()
    conn.close()
    return data

# Update cleaned text and answers
def update_question(question_id, cleaned_text, answers):
    conn = sqlite3.connect(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE ImageText SET text = ? WHERE id = ?", (cleaned_text, question_id))
        
        correct_answers = '|'.join([answer_text for answer_text, is_correct in answers if is_correct])
        answer1, answer2, answer3, answer4 = [answer_text for answer_text, _ in answers]
        
        cursor.execute("""
            UPDATE CleanedData
            SET cleaned_question = ?, answer1 = ?, answer2 = ?, answer3 = ?, answer4 = ?, correct = ?, fixed = 1
            WHERE question_id = ?
        """, (cleaned_text, answer1, answer2, answer3, answer4, correct_answers, question_id))
        
        conn.commit()
    except Exception as e:
        raise e
    finally:
        conn.close()

# Get the count of questions that need to be fixed
def get_unfixed_count():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(id) FROM CleanedData WHERE fixed IS NULL")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# GUI Application
class QuestionEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Question Editor")
        self.geometry("800x600")
        
        self.questions = get_questions()
        self.current_index = 0
        
        # UI Elements
        self.raw_text_label = tk.Label(self, text="Raw Question:")
        self.raw_text_label.pack()
        self.raw_text_display = tk.Label(self, text="", wraplength=600, justify="left")
        self.raw_text_display.pack()
        
        self.img_label = tk.Label(self)
        self.img_label.pack()
        
        self.cleaned_text_label = tk.Label(self, text="Cleaned Question:")
        self.cleaned_text_label.pack()
        self.cleaned_text_entry = tk.Entry(self, width=80)
        self.cleaned_text_entry.pack()
        
        self.answer_vars = []
        self.answer_entries = []
        self.check_buttons = []
        
        for i in range(4):
            frame = tk.Frame(self)
            frame.pack()
            answer_var = tk.BooleanVar()
            entry = tk.Entry(frame, width=60)
            check = tk.Checkbutton(frame, text="Correct", variable=answer_var)
            entry.pack(side=tk.LEFT)
            check.pack(side=tk.RIGHT)
            self.answer_vars.append(answer_var)
            self.answer_entries.append(entry)
            self.check_buttons.append(check)
        
        self.button_frame = tk.Frame(self)
        self.button_frame.pack()
        
        self.save_button = tk.Button(self.button_frame, text="Save", command=self.save_question)
        self.save_button.pack(side=tk.TOP)
        
        self.prev_button = tk.Button(self.button_frame, text="Previous", command=self.prev_question)
        self.prev_button.pack(side=tk.TOP)
        
        self.next_button = tk.Button(self.button_frame, text="Next", command=self.next_question)
        self.next_button.pack(side=tk.TOP)
        
        self.status_label = tk.Label(self, text="", fg="green")
        self.status_label.pack()
        
        self.unfixed_count_label = tk.Label(self, text=f"Questions to be fixed: {get_unfixed_count()}")
        self.unfixed_count_label.pack()
        
        self.load_question()
    
    def load_question(self):
        if not self.questions:
            messagebox.showerror("Error", "No questions found!")
            self.destroy()
            return
        
        q = self.questions[self.current_index]
        q_id, img_filename, raw_text = q
        img_path = os.path.join(image_folder, img_filename)
        
        try:
            img = Image.open(img_path)
            img = img.resize((600, 400), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            self.img_label.config(image=img)
            self.img_label.image = img
        except Exception as e:
            messagebox.showerror("Image Error", f"Could not load image: {img_path}\n{e}")
        
        self.raw_text_display.config(text=raw_text)
        self.cleaned_text_entry.delete(0, tk.END)
        self.cleaned_text_entry.insert(0, raw_text or "")
        
        conn = sqlite3.connect(db_name)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT cleaned_question, answer1, answer2, answer3, answer4, correct FROM CleanedData WHERE question_id = ?", (q_id,))
            answers = cursor.fetchone()
        finally:
            conn.close()
        
        if answers:
            self.cleaned_text_entry.delete(0, tk.END)
            self.cleaned_text_entry.insert(0, answers[0])
            correct_answers = answers[5].split('|') if answers[5] else []
            for i in range(4):
                self.answer_entries[i].delete(0, tk.END)
                self.answer_entries[i].insert(0, answers[i+1])
                self.answer_vars[i].set(answers[i+1] in correct_answers)
        else:
            for i in range(4):
                self.answer_entries[i].delete(0, tk.END)
                self.answer_vars[i].set(False)
    
    def save_question(self):
        if not any(var.get() for var in self.answer_vars):
            messagebox.showerror("Error", "At least one answer must be marked as correct.")
            return
        
        q_id = self.questions[self.current_index][0]
        cleaned_text = self.cleaned_text_entry.get()
        answers = [(self.answer_entries[i].get(), self.answer_vars[i].get()) for i in range(4)]
        try:
            update_question(q_id, cleaned_text, answers)
            self.status_label.config(text="Question updated successfully!", fg="green")
            self.unfixed_count_label.config(text=f"Questions to be fixed: {get_unfixed_count()}")
        except Exception as e:
            self.status_label.config(text=f"Failed to update question: {e}", fg="red")
    
    def next_question(self):
        self.status_label.config(text="")
        self.save_question()
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self.load_question()
        else:
            messagebox.showinfo("End", "No more questions!")
    
    def prev_question(self):
        self.status_label.config(text="")
        self.save_question()
        if self.current_index > 0:
            self.current_index -= 1
            self.load_question()

if __name__ == "__main__":
    app = QuestionEditor()
    app.mainloop()
