import tkinter as tk
from tkinter import messagebox
import random
import sqlite3
from PIL import Image, ImageTk
import os

import DataCleaner  # Assuming DataCleaner.py provides questions and answers

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz App")
        
        self.score = 0
        self.total_questions = 0
        self.current_question = 0
        self.questions = self.get_fixed_questions()
        random.shuffle(self.questions)
        
        self.create_widgets()
        self.display_question()

    def get_fixed_questions(self):
        conn = sqlite3.connect(DataCleaner.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT ImageText.id, ImageText.filename, ImageText.text FROM ImageText JOIN CleanedData ON CleanedData.question_id = ImageText.id WHERE CleanedData.fixed = 1")
        data = cursor.fetchall()
        conn.close()
        return data

    def create_widgets(self):
        self.question_label = tk.Label(self.root, text="", wraplength=400)
        self.question_label.pack(pady=20)
        
        self.answer_vars = []
        self.answer_checks = []
        for _ in range(4):
            var = tk.BooleanVar()
            check = tk.Checkbutton(self.root, variable=var, command=self.check_answer, anchor="w", justify="left")
            check.pack(anchor="w", padx=20)
            self.answer_vars.append(var)
            self.answer_checks.append(check)
        
        self.result_label = tk.Label(self.root, text="", fg="red")
        self.result_label.pack(pady=10)
        
        self.image_label = tk.Label(self.root)
        self.image_label.pack(pady=20)
        
        self.next_button = tk.Button(self.root, text="Next", command=self.next_question, bg="green", font=("Helvetica", 16))
        self.next_button.pack(pady=10)
        
        self.score_label = tk.Label(self.root, text="Score: 0/0")
        self.score_label.pack(pady=10)

    def display_question(self):
        question = self.questions[self.current_question]
        self.question_label.config(text=question[2])  # Assuming the question text is in the third position
        
        self.image_label.config(image="")
        self.image_label.image = None
        self.result_label.config(text="")
        
        conn = sqlite3.connect(DataCleaner.db_name)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT answer1, answer2, answer3, answer4, correct FROM CleanedData WHERE question_id = ?", (question[0],))
            answers = cursor.fetchone()
        finally:
            conn.close()
        
        if answers:
            correct_answers = answers[4].split('|') if answers[4] else []
            for i in range(4):
                self.answer_checks[i].config(text=answers[i])
                self.answer_vars[i].set(False)
        else:
            for i in range(4):
                self.answer_checks[i].config(text="")
                self.answer_vars[i].set(False)

    def check_answer(self):
        question = self.questions[self.current_question]
        conn = sqlite3.connect(DataCleaner.db_name)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT correct FROM CleanedData WHERE question_id = ?", (question[0],))
            result = cursor.fetchone()
            correct_answers = result[0].split('|') if result else []
        finally:
            conn.close()
        
        self.total_questions += 1
        if all(var.get() == (check.cget("text") in correct_answers) for var, check in zip(self.answer_vars, self.answer_checks)):
            self.score += 1
            self.result_label.config(text="Correct", fg="green")
            self.show_image(question[1])
        elif any(var.get() and check.cget("text") not in correct_answers for var, check in zip(self.answer_vars, self.answer_checks)):
            self.result_label.config(text="Wrong!", fg="red")
            self.show_image(question[1])
        
        self.score_label.config(text=f"Score: {self.score}/{self.total_questions}")

    def show_image(self, filename):
        img_path = os.path.join(DataCleaner.image_folder, filename)
        try:
            img = Image.open(img_path)
            img = img.resize((600, 400), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            self.image_label.config(image=img)
            self.image_label.image = img
        except Exception as e:
            messagebox.showerror("Image Error", f"Could not load image: {img_path}\n{e}")
            self.image_label.config(image="")
            self.image_label.image = None

    def next_question(self):
        self.current_question += 1
        if self.current_question >= len(self.questions):
            self.current_question = 0
        self.display_question()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()