# BIBLE QUEST - simple Tkinter desktop quiz game
import tkinter as tk
from tkinter import messagebox
import random
import os

# Settings
TOTAL = 10
SECONDS = 60
FILE = "high_score.txt"

PARCHMENT = "#F1E3C6"
PAPER = "#E4D2AE"
GOLD = "#B08D57"
BROWN = "#4A3022"
BURGUNDY = "#722F37"
TEXT = "#30251D"
GREEN = "#3F6B4A"

F_TITLE = ("Georgia", 30, "bold")
F_HEAD = ("Georgia", 18, "bold")
F_BODY = ("Georgia", 13)
F_BOLD = ("Georgia", 13, "bold")
F_SMALL = ("Georgia", 11)
F_BTN = ("Georgia", 12, "bold")

# 10 Bible questions
questions = [
    {"q": "Who was the first man according to Genesis?",
     "c": {"A": "Adam", "B": "Noah", "C": "Abraham", "D": "Moses"}, "a": "A"},
    {"q": "How many days did God take to create the world in Genesis 1?",
     "c": {"A": "Three", "B": "Six", "C": "Seven", "D": "Ten"}, "a": "B"},
    {"q": "Which shepherd boy defeated Goliath?",
     "c": {"A": "Solomon", "B": "Saul", "C": "David", "D": "Jonathan"}, "a": "C"},
    {"q": "Who interpreted Pharaoh's dreams in Egypt?",
     "c": {"A": "Joseph", "B": "Daniel", "C": "Moses", "D": "Nehemiah"}, "a": "A"},
    {"q": "Which prophet was thrown into a den of lions?",
     "c": {"A": "Elijah", "B": "Isaiah", "C": "Jeremiah", "D": "Daniel"}, "a": "D"},
    {"q": "Who was the mother of Jesus?",
     "c": {"A": "Elizabeth", "B": "Mary", "C": "Anna", "D": "Rachel"}, "a": "B"},
    {"q": "How many disciples did Jesus choose?",
     "c": {"A": "Ten", "B": "Eleven", "C": "Twelve", "D": "Thirteen"}, "a": "C"},
    {"q": "On which sea did Jesus calm the storm?",
     "c": {"A": "Dead Sea", "B": "Red Sea", "C": "Mediterranean Sea", "D": "Sea of Galilee"}, "a": "D"},
    {"q": "Which book of the New Testament was written by Luke as a companion to his gospel?",
     "c": {"A": "Acts", "B": "Romans", "C": "Hebrews", "D": "Revelation"}, "a": "A"},
    {"q": "In the Good Samaritan parable, who passed by the injured man first?",
     "c": {"A": "A king and a soldier", "B": "A priest and a Levite",
           "C": "A farmer and a merchant", "D": "A scribe and a Pharisee"}, "a": "B"},
]

# Main window
root = tk.Tk()
root.title("BIBLE QUEST")
root.configure(bg=PARCHMENT)
root.resizable(False, False)
root.geometry("900x700")
try:
    root.eval("tk::PlaceWindow . center")
except Exception:
    pass

frame = tk.Frame(root, bg=PARCHMENT)
frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

# Quiz variables
high_score = 0
quiz = []
index = 0
score = 0
choice = tk.StringVar()
tick = None
done = False
log = []

lbl_time = None
lbl_score = None
lbl_feedback = None
btn_submit = None
btn_next = None
radios = []


# High score
def load_high():
    global high_score
    high_score = 0
    try:
        if os.path.exists(FILE):
            with open(FILE) as f:
                value = f.read().strip()
            if value.isdigit():
                high_score = int(value)
    except (OSError, ValueError):
        high_score = 0


def save_high(final_score):
    global high_score
    if final_score > high_score:
        high_score = final_score
        try:
            with open(FILE, "w") as f:
                f.write(str(high_score))
        except OSError:
            pass
        return True
    return False


# Helpers
def clear():
    global tick, radios
    stop_timer()
    radios = []
    for widget in frame.winfo_children():
        widget.destroy()


def stop_timer():
    global tick
    if tick is not None:
        try:
            root.after_cancel(tick)
        except Exception:
            pass
        tick = None


def make_button(parent, text, command, gold=True):
    return tk.Button(
        parent, text=text, command=command, font=F_BTN,
        bg=GOLD if gold else BROWN,
        fg=TEXT if gold else PARCHMENT,
        activebackground=BROWN if gold else GOLD,
        activeforeground=PARCHMENT if gold else TEXT,
        relief=tk.RAISED, bd=2, padx=14, pady=7, cursor="hand2"
    )


# Start screen
def start_screen():
    clear()
    card = tk.Frame(frame, bg=PAPER, highlightbackground=GOLD,
                    highlightthickness=2, padx=40, pady=40)
    card.pack(expand=True)

    tk.Label(card, text="BIBLE QUEST", font=F_TITLE, fg=BURGUNDY,
             bg=PAPER).pack(pady=(0, 5))
    tk.Label(card, text="Test Your Bible Knowledge", font=("Georgia", 15, "italic"),
             fg=BROWN, bg=PAPER).pack()
    tk.Label(card, text="Explore the Scriptures and test your knowledge of the Bible.",
             font=F_BODY, fg=TEXT, bg=PAPER, wraplength=480,
             justify=tk.CENTER).pack(pady=25)
    tk.Label(card, text="10 questions  |  15 seconds each  |  1 point per correct answer",
             font=F_SMALL, fg=BROWN, bg=PAPER).pack()
    tk.Label(card, text="High Score: %d / %d" % (high_score, TOTAL),
             font=F_BOLD, fg=GOLD, bg=PAPER).pack(pady=15)

    buttons = tk.Frame(card, bg=PAPER)
    buttons.pack()
    make_button(buttons, "Start Quiz", start_quiz).grid(row=0, column=0, padx=8)
    make_button(buttons, "Exit", quit_app, False).grid(row=0, column=1, padx=8)


# Quiz setup
def start_quiz():
    global quiz, index, score, done, log, choice
    quiz = random.sample(questions, TOTAL)
    index = 0
    score = 0
    done = False
    log = []
    choice = tk.StringVar()
    question_screen()


def question_screen():
    global lbl_time, lbl_score, lbl_feedback, btn_submit, btn_next, radios, done

    clear()
    done = False
    choice.set("")
    radios = []
    item = quiz[index]

    top = tk.Frame(frame, bg=PARCHMENT)
    top.pack(fill=tk.X, pady=(0, 12))
    tk.Label(top, text="Question %d of %d" % (index + 1, TOTAL),
             font=F_BOLD, fg=BROWN, bg=PARCHMENT).pack(side=tk.LEFT)
    lbl_score = tk.Label(top, text="Score: %d" % score, font=F_BOLD,
                         fg=BROWN, bg=PARCHMENT)
    lbl_score.pack(side=tk.LEFT, padx=25)
    lbl_time = tk.Label(top, text="Time: %ds" % SECONDS, font=F_BOLD,
                        fg=BURGUNDY, bg=PARCHMENT)
    lbl_time.pack(side=tk.RIGHT)
    tk.Label(frame, text="Progress: %d/%d" % (index + 1, TOTAL),
             font=F_SMALL, fg=BROWN, bg=PARCHMENT).pack(anchor="w")

    card = tk.Frame(frame, bg=PAPER, highlightbackground=GOLD,
                    highlightthickness=1, padx=25, pady=20)
    card.pack(fill=tk.BOTH, expand=True, pady=8)

    tk.Label(card, text=item["q"], font=F_HEAD, fg=TEXT, bg=PAPER,
             wraplength=760, justify=tk.LEFT).pack(anchor="w", pady=(0, 18))

    for letter in ["A", "B", "C", "D"]:
        r = tk.Radiobutton(
            card, text="%s. %s" % (letter, item["c"][letter]),
            variable=choice, value=letter, font=F_BODY,
            fg=TEXT, bg=PAPER, selectcolor=GOLD,
            activebackground=PAPER, anchor="w", justify=tk.LEFT,
            wraplength=720, padx=6, pady=5
        )
        r.pack(fill=tk.X, pady=3)
        radios.append(r)

    lbl_feedback = tk.Label(card, text="Select an answer, then press Submit.",
                            font=F_BODY, fg=BROWN, bg=PAPER,
                            wraplength=760, justify=tk.LEFT)
    lbl_feedback.pack(anchor="w", pady=(18, 0))

    buttons = tk.Frame(card, bg=PAPER)
    buttons.pack(anchor="w", pady=(16, 0))
    btn_submit = make_button(buttons, "Submit Answer", submit)
    btn_submit.grid(row=0, column=0, padx=(0, 10))
    btn_next = make_button(buttons, "Next Question", next_question)
    btn_next.grid(row=0, column=1)
    btn_next.config(state=tk.DISABLED)

    start_timer()


# Timer
def start_timer():
    global tick
    lbl_time.config(text="Time: %ds" % SECONDS, fg=BURGUNDY)
    tick = root.after(1000, update_timer, lbl_time)


def update_timer(widget):
    global tick
    if tick is None or not widget.winfo_exists():
        return

    remaining = int(widget.cget("text").split()[1].rstrip("s")) - 1
    widget.config(text="Time: %ds" % remaining,
                  fg=BURGUNDY if remaining > 5 else BROWN)

    if remaining <= 0:
        tick = None
        timeout()
    else:
        tick = root.after(1000, update_timer, widget)


def timeout():
    global done
    if done:
        return
    done = True
    item = quiz[index]
    correct = item["a"]
    selected = choice.get()

    log.append({
        "number": index + 1,
        "question": item["q"],
        "selected": selected if selected else "No answer",
        "correct": correct,
        "correct_text": item["c"][correct],
        "status": "timeout",
    })

    stop_timer()
    btn_submit.config(state=tk.DISABLED)
    for r in radios:
        r.config(state=tk.DISABLED)

    next_question()


# Answer checking
def submit():
    global score, done
    if done:
        return

    selected = choice.get()
    if selected == "":
        messagebox.showwarning("No Answer", "Please choose an answer first.")
        return

    done = True
    stop_timer()
    item = quiz[index]
    correct = item["a"]
    right = selected == correct

    if right:
        score += 1
        lbl_feedback.config(text="Correct! The answer is %s - %s" %
                            (correct, item["c"][correct]), fg=GREEN)
    else:
        lbl_feedback.config(text="Incorrect. Correct answer: %s - %s" %
                            (correct, item["c"][correct]), fg=BURGUNDY)

    log.append({
        "number": index + 1,
        "question": item["q"],
        "selected": selected,
        "correct": correct,
        "correct_text": item["c"][correct],
        "status": "correct" if right else "incorrect",
    })

    lbl_score.config(text="Score: %d" % score)
    btn_submit.config(state=tk.DISABLED)
    btn_next.config(state=tk.NORMAL)
    for r in radios:
        r.config(state=tk.DISABLED)


def next_question():
    global index
    if index < TOTAL - 1:
        index += 1
        question_screen()
    else:
        show_results()


# Results
def message_for(n):
    if n >= 9:
        return "Excellent! You have strong Bible knowledge."
    if n >= 7:
        return "Very Good! Keep learning the Scriptures."
    if n >= 5:
        return "Good effort! Continue studying."
    return "Keep exploring and learning God's Word."


def show_results():
    clear()
    record = save_high(score)
    percent = int(score / TOTAL * 100)
    timeouts = sum(1 for x in log if x["status"] == "timeout")

    tk.Label(frame, text="Quiz Complete!", font=F_TITLE, fg=BURGUNDY,
             bg=PARCHMENT).pack(pady=(5, 8))
    tk.Label(frame, text="Final Score: %d / %d  (%d%%)" % (score, TOTAL, percent),
             font=F_HEAD, fg=BROWN, bg=PARCHMENT).pack()
    tk.Label(frame, text=message_for(score), font=F_BOLD, fg=BURGUNDY,
             bg=PARCHMENT).pack(pady=6)
    tk.Label(frame, text="Correct: %d    Incorrect / timed out: %d    Timed out: %d" %
             (score, TOTAL - score, timeouts), font=F_SMALL, fg=BROWN,
             bg=PARCHMENT).pack()
    tk.Label(frame, text="High Score: %d / %d%s" %
             (high_score, TOTAL, "  - NEW RECORD!" if record else ""),
             font=F_BOLD, fg=GREEN if record else GOLD, bg=PARCHMENT).pack(pady=(4, 10))

    box_frame = tk.Frame(frame, bg=PAPER, highlightbackground=GOLD,
                         highlightthickness=1, padx=10, pady=10)
    box_frame.pack(fill=tk.BOTH, expand=True)
    tk.Label(box_frame, text="Answer Review", font=F_BOLD, fg=BROWN,
             bg=PAPER).pack(anchor="w")

    text = tk.Text(box_frame, wrap=tk.WORD, font=F_SMALL, bg=PAPER,
                   fg=TEXT, bd=0, highlightthickness=0)
    bar = tk.Scrollbar(box_frame, command=text.yview)
    text.config(yscrollcommand=bar.set)
    bar.pack(side=tk.RIGHT, fill=tk.Y)
    text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    for item in log:
        label = {"correct": "CORRECT", "incorrect": "INCORRECT",
                 "timeout": "TIME OUT - 0 POINTS"}[item["status"]]
        text.insert(tk.END, "%d. %s\n" % (item["number"], item["question"]))
        text.insert(tk.END, "   Your answer: %s\n" % item["selected"])
        text.insert(tk.END, "   Correct answer: %s - %s\n" %
                    (item["correct"], item["correct_text"]))
        text.insert(tk.END, "   Result: %s\n\n" % label)
    text.config(state=tk.DISABLED)

    buttons = tk.Frame(frame, bg=PARCHMENT)
    buttons.pack(pady=10)
    make_button(buttons, "Restart Quiz", start_quiz).grid(row=0, column=0, padx=8)
    make_button(buttons, "Exit", quit_app, False).grid(row=0, column=1, padx=8)


# Restart and exit
def quit_app():
    stop_timer()
    root.destroy()


load_high()
start_screen()
root.mainloop()