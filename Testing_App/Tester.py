import tkinter as tk
from tkinter import messagebox
import random

import DataCleaner  # Assuming DataCleaner.py provides questions and answers

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz App")
        
        self.name_var = tk.StringVar()
        self.score = 0
        self.current_question = 0
        self.questions = DataCleaner.get_questions()  # Assuming this function returns a list of questions
        random.shuffle(self.questions)
        
        self.create_widgets()
        self.display_question()

    def create_widgets(self):
        tk.Label(self.root, text="Enter your name:").pack()
        tk.Entry(self.root, textvariable=self.name_var).pack()
        tk.Button(self.root, text="Start Test", command=self.start_test).pack()
        
        self.question_label = tk.Label(self.root, text="", wraplength=400)
        self.question_label.pack()
        
        self.answer_var = tk.StringVar()
        self.answer_check = tk.Checkbutton(self.root, text="", variable=self.answer_var, onvalue="True", offvalue="False", command=self.check_answer)
        self.answer_check.pack()
        
        self.image_label = tk.Label(self.root)
        self.image_label.pack()
        
        self.next_button = tk.Button(self.root, text="Next", command=self.next_question)
        self.next_button.pack()
        
        self.score_label = tk.Label(self.root, text="Score: 0")
        self.score_label.pack()

    def start_test(self):
        self.name = self.name_var.get()
        if not self.name:
            messagebox.showwarning("Input Error", "Please enter your name")
            return
        self.score = 0
        self.current_question = 0
        random.shuffle(self.questions)
        self.display_question()

    def display_question(self):
        question = self.questions[self.current_question]
        self.question_label.config(text=question[2])  # Assuming the question text is in the third position
        self.answer_check.config(text=question[2])  # Assuming the answer text is in the third position
        self.answer_var.set("False")
        self.image_label.config(image="")

    def check_answer(self):
        question = self.questions[self.current_question]
        if self.answer_var.get() == "True":
            if question[2]:  # Assuming the correct answer flag is in the third position
                self.score += 1
                self.image_label.config(image=tk.PhotoImage(file="correct.png"))
            else:
                self.image_label.config(image=tk.PhotoImage(file="wrong.png"))
        self.score_label.config(text=f"Score: {self.score}")

    def next_question(self):
        self.current_question += 1
        if self.current_question >= len(self.questions):
            self.current_question = 0
        self.display_question()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()