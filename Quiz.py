import tkinter as tk
import colorsys
import requests
import random
import html

# GUI Window Code
root = tk.Tk()
root.title("Quiz!")
root.geometry('850x850')
root.config(bg='black')

# RGB Color Cycling
def rgb_cycle(widget):
    hue = 0
    def update_color():
        nonlocal hue
        rgb = colorsys.hsv_to_rgb(hue, 1, 1)
        color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        widget.config(fg=color)
        hue = (hue + 0.01) % 1
        root.after(50, update_color)
    update_color()

# Label
label = tk.Label(root, text='Knowledge Quiz', font=('Arial', 24, 'bold'), bg='#121212', fg='white')
label.pack(pady=20)
rgb_cycle(label)

# Initialize Quiz State
score = 0
current_question = 0
questions = []
timer_seconds = 15  
timer_id = None
answer_selected = False

# Question Label
question_label = tk.Label(root, text='', font=('Arial', 18), bg='black', fg='#FFEF06', wraplength=450, justify='center')
question_label.pack(pady=10)

# Options Frame
options_frame = tk.Frame(root, bg='black')
options_frame.pack(pady=10)
option_buttons = []
for i in range(4):
    btn = tk.Button(options_frame, text='', width=40, height=2, font=('Arial', 12), bg='#333', fg='#FFEF06', relief='flat', bd=0)
    btn.grid(row=i, column=0, pady=5, padx=10, sticky='ew')
    btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#FFD700', fg='black', highlightbackground='#FFD700', highlightcolor='#FFD700', highlightthickness=2))
    btn.bind("<Leave>", lambda e, b=btn: b.config(bg='#333', fg='#FFEF06', highlightbackground='black', highlightcolor='black', highlightthickness=0))
    btn.config(command=lambda i=i: select_answer(i))
    option_buttons.append(btn)

# Feedback Label
feedback_label = tk.Label(root, text='', font=('Arial', 14), bg='black', fg='red')
feedback_label.pack(pady=10)

# Control Buttons
control_frame = tk.Frame(root, bg='black')
control_frame.pack(pady=10)

# Hover effects for buttons
def button_hover_enter(widget, bg_color, fg_color):
    widget.config(bg=bg_color, fg=fg_color, highlightbackground=bg_color, highlightcolor=bg_color, highlightthickness=2)

def button_hover_leave(widget, bg_color, fg_color):
    widget.config(bg=bg_color, fg=fg_color, highlightbackground='black', highlightcolor='black', highlightthickness=0)

# Next Question Button
next_button = tk.Button(control_frame, text='Next Question', font=('Arial', 14, 'bold'), bg='#4CAF50', fg='#FCFBF4', command=lambda: next_question())
next_button.grid(row=0, column=0, pady=5, padx=10)
next_button.bind("<Enter>", lambda e: button_hover_enter(next_button, '#00D61C', '#FCFBF4'))
next_button.bind("<Leave>", lambda e: button_hover_leave(next_button, '#4CAF50', '#FCFBF4'))

# Start New Quiz Button
new_quiz_button = tk.Button(control_frame, text='Start New Quiz', font=('Arial', 14, 'bold'), bg='#4CAF50', fg='#FCFBF4', command=lambda: start_new_quiz())
new_quiz_button.grid(row=1, column=0, pady=8, padx=10)
new_quiz_button.bind("<Enter>", lambda e: button_hover_enter(new_quiz_button, '#00D61C', '#FCFBF4'))
new_quiz_button.bind("<Leave>", lambda e: button_hover_leave(new_quiz_button, '#4CAF50', '#FCFBF4'))

# Score Label
score_label = tk.Label(root, text=f'Score: {score}', font=('Arial', 20, 'bold'), bg='#000000', fg='#BFFFFC')
score_label.place(relx=1.0, x=-55, y=28, anchor='ne')

# Timer Label
timer_label = tk.Label(root, text=f'Time: {timer_seconds}', font=('Arial', 14, 'bold'), bg='#000000', fg='#BFFFFC')
timer_label.pack(pady=10)

# Code To Fetch Questions from API
def fetch_questions():
    global questions, current_question, score
    url = "https://opentdb.com/api.php?amount=5&type=multiple"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        questions = data['results']
        current_question = 0
        score = 0
        load_question()
    else:
        question_label.config(text="Error fetching questions. Please try again.")

# Code To Load Questions
def load_question():
    global current_question, timer_seconds, answer_selected
    if current_question < len(questions):
        question = questions[current_question]
        question_label.config(text=html.unescape(question['question']))
        options = question['incorrect_answers'] + [question['correct_answer']]
        random.shuffle(options)
        for i, option in enumerate(options):
            option_buttons[i].config(text=html.unescape(option), state='normal', bg='#333')
        next_button.config(state='normal')  # Enable Next Question button
        feedback_label.config(text='')
        timer_seconds = 15  # Reset timer to 15 seconds for each question
        answer_selected = False
        update_timer()
    else:
        show_final_score()

# Code To Select Answer
def select_answer(index):
    global answer_selected
    if not answer_selected:
        answer_selected = True
        check_answer(index)

# Code To Check Answer
def check_answer(index):
    global current_question, score
    question = questions[current_question]
    correct_answer = html.unescape(question['correct_answer'])
    selected_option = html.unescape(option_buttons[index].cget('text'))
    if selected_option == correct_answer:
        score += 1
        feedback_label.config(text="Correct! Well done!", fg='green')
        option_buttons[index].config(bg='green')
    else:
        feedback_label.config(text=f"Incorrect. The correct answer was: {correct_answer}", fg='red')
        option_buttons[index].config(bg='red')
        for btn in option_buttons:
            if btn.cget('text') == correct_answer:
                btn.config(bg='green')
    score_label.config(text=f'Score: {score}')
    for btn in option_buttons:
        btn.config(state='disabled')
    if timer_id:
        root.after_cancel(timer_id)
    next_button.config(state='normal')  # Enable Next Question button

# Next Question Button Code
def next_question():
    global current_question, answer_selected
    if not answer_selected:
        # If no answer was selected, the score for this question is zero
        feedback_label.config(text="Question skipped. No points awarded.")
    
    # Proceed to the next question
    current_question += 1
    if current_question < len(questions):
        load_question()
    else:
        show_final_score()

# Final Score Code
def show_final_score():
    question_label.config(text=f'Quiz completed!\nYour final score is: {score}/{len(questions)}')
    feedback_label.config(text='')
    for btn in option_buttons:
        btn.config(state='disabled')
    next_button.config(state='disabled')
    new_quiz_button.config(state='normal')
    timer_label.config(text='')

# Start New Quiz Button Code
def start_new_quiz():
    global questions, current_question, score, timer_id
    # Cancel any ongoing timer and reset states
    if timer_id:
        root.after_cancel(timer_id)
    questions = []
    current_question = 0
    score = 0
    score_label.config(text='Score: 0')
    timer_label.config(text='Time Remaining: 15')
    feedback_label.config(text='')
    for btn in option_buttons:
        btn.config(text='', state='normal', bg='#333')
    next_button.config(state='normal')
    fetch_questions()

# Timer Code
def update_timer():
    global timer_seconds, timer_id
    if timer_seconds > 0:
        timer_label.config(text=f'Time Remaining: {timer_seconds}')
        timer_seconds -= 1
        timer_id = root.after(1000, update_timer)
    else:
        feedback_label.config(text="Time's up! Moving to the next question.")
        next_question()

# Start the application
fetch_questions()  
root.mainloop()
