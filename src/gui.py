import customtkinter as ctk
from tkinter import messagebox
import threading
from src.quiz_data import QuizData
from src.timer import QuizTimer
from src.score_report import ScoreReport

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class QuizApp:
    def __init__(self, root):
        """
        Initialize the QuizApp with the root Tkinter window.
        Sets up the main application structure, including frames for different screens.
        """
        self.root = root
        self.root.title("🎓 Quiz Master - Modern Examination System")
        self.root.geometry("900x700")
        self.root.resizable(False, False)

        # Initialize data and components
        self.quiz_data = QuizData()
        self.questions = self.quiz_data.get_questions()
        self.current_question_index = 0
        self.user_answers = {}
        self.user_name = ""
        self.timer = None
        self.score_report = None

        # Create frames for different screens using CustomTkinter
        self.name_frame = ctk.CTkFrame(self.root)
        self.quiz_frame = ctk.CTkFrame(self.root)
        self.result_frame = ctk.CTkFrame(self.root)

        # Setup the initial screen (name entry)
        self.setup_name_screen()

    def setup_name_screen(self):
        """
        Setup the name entry screen where the user enters their name to start the quiz.
        """
        # Clear any existing widgets
        for widget in self.name_frame.winfo_children():
            widget.destroy()

        self.name_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(self.name_frame, text="🎓 Welcome to Quiz Master", font=ctk.CTkFont(size=32, weight="bold"))
        title_label.pack(pady=60)

        # Subtitle
        subtitle_label = ctk.CTkLabel(self.name_frame, text="Modern Examination System with Timer & Analytics", font=ctk.CTkFont(size=14))
        subtitle_label.pack(pady=(0, 40))

        # Name entry section
        name_label = ctk.CTkLabel(self.name_frame, text="Enter your name to begin:", font=ctk.CTkFont(size=18, weight="bold"))
        name_label.pack(pady=(20, 10))

        self.name_entry = ctk.CTkEntry(self.name_frame, placeholder_text="Your full name", width=350, height=45, font=ctk.CTkFont(size=16))
        self.name_entry.pack(pady=15)
        self.name_entry.focus()

        # Start button
        start_button = ctk.CTkButton(self.name_frame, text="🚀 Start Quiz", command=self.start_quiz, width=200, height=50, font=ctk.CTkFont(size=18, weight="bold"))
        start_button.pack(pady=40)

        # Instructions
        instructions_label = ctk.CTkLabel(self.name_frame, text="• 10-minute timer • Multiple choice questions • Instant results", font=ctk.CTkFont(size=12))
        instructions_label.pack(pady=(10, 0))

        # Bind Enter key to start quiz
        self.root.bind('<Return>', lambda event: self.start_quiz())

    def start_quiz(self):
        """
        Start the quiz after validating the user's name.
        Initializes the timer, loads questions, and switches to quiz screen.
        """
        self.user_name = self.name_entry.get().strip()
        if not self.user_name:
            messagebox.showerror("Error", "Please enter your name to start the quiz.")
            return

        # Hide name frame and show quiz frame
        self.name_frame.pack_forget()
        self.setup_quiz_screen()

        # Initialize timer (10 minutes)
        self.timer = QuizTimer(duration_minutes=10, callback=self.auto_submit)
        self.timer.start_timer()

        # Update timer display
        self.update_timer_label()

    def setup_quiz_screen(self):
        """
        Setup the quiz screen with question display, options, navigation buttons, and timer.
        """
        # Clear any existing widgets
        for widget in self.quiz_frame.winfo_children():
            widget.destroy()

        self.quiz_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header with timer and progress
        header_frame = ctk.CTkFrame(self.quiz_frame)
        header_frame.pack(fill="x", pady=(0, 20))

        # Timer label
        self.timer_label = ctk.CTkLabel(header_frame, text="⏰ Time Remaining: 10:00", font=ctk.CTkFont(size=18, weight="bold"))
        self.timer_label.pack(side="left", padx=20)

        # Progress label
        self.progress_label = ctk.CTkLabel(header_frame, text=f"📊 Question {self.current_question_index + 1} of {len(self.questions)}", font=ctk.CTkFont(size=16))
        self.progress_label.pack(side="right", padx=20)

        # Question text in a card-like frame
        question_frame = ctk.CTkFrame(self.quiz_frame)
        question_frame.pack(fill="x", pady=(0, 20))

        self.question_label = ctk.CTkLabel(question_frame, text="", font=ctk.CTkFont(size=18), wraplength=750, justify="left")
        self.question_label.pack(pady=20, padx=20)

        # Options using CustomTkinter radio buttons
        options_frame = ctk.CTkFrame(self.quiz_frame)
        options_frame.pack(fill="x", pady=(0, 20))

        self.option_vars = ctk.StringVar()
        self.option_buttons = []

        # Create radio buttons for each option
        for i, option in enumerate(['A', 'B', 'C', 'D']):
            rb = ctk.CTkRadioButton(options_frame, text="", variable=self.option_vars, value=option, font=ctk.CTkFont(size=16))
            rb.pack(anchor="w", padx=30, pady=8)
            self.option_buttons.append(rb)

        # Navigation buttons frame
        nav_frame = ctk.CTkFrame(self.quiz_frame, fg_color="transparent")
        nav_frame.pack(fill="x", pady=(20, 0))

        # Button container
        button_container = ctk.CTkFrame(nav_frame, fg_color="transparent")
        button_container.pack(expand=True)

        self.prev_button = ctk.CTkButton(button_container, text="⬅️ Previous", command=self.previous_question, width=120, height=45, font=ctk.CTkFont(size=14, weight="bold"))
        self.prev_button.pack(side="left", padx=10)

        self.next_button = ctk.CTkButton(button_container, text="Next ➡️", command=self.next_question, width=120, height=45, font=ctk.CTkFont(size=14, weight="bold"))
        self.next_button.pack(side="left", padx=10)

        self.submit_button = ctk.CTkButton(button_container, text="🎯 Submit Quiz", command=self.submit_quiz, width=150, height=45, font=ctk.CTkFont(size=16, weight="bold"), fg_color="#FF6B35", hover_color="#E55A2B")
        self.submit_button.pack(side="right", padx=10)

        # Load the first question
        self.load_question()

    def load_question(self):
        """
        Load the current question and its options into the GUI.
        """
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.question_label.configure(text=question['question'])

            # Update progress label
            self.progress_label.configure(text=f"Question {self.current_question_index + 1} of {len(self.questions)}")

            # Update option buttons
            for i, (key, value) in enumerate(question['options'].items()):
                self.option_buttons[i].configure(text=f"{key}. {value}")

            # Check if user has already answered this question
            if self.current_question_index in self.user_answers:
                self.option_vars.set(self.user_answers[self.current_question_index])
            else:
                self.option_vars.set("")

            # Force update to ensure changes are visible
            self.root.update_idletasks()

            # Update navigation buttons
            self.prev_button.configure(state="normal" if self.current_question_index > 0 else "disabled")
            self.next_button.configure(state="normal" if self.current_question_index < len(self.questions) - 1 else "disabled")

    def next_question(self):
        """
        Move to the next question, saving the current answer.
        """
        self.save_current_answer()
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.load_question()

    def previous_question(self):
        """
        Move to the previous question, saving the current answer.
        """
        self.save_current_answer()
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.load_question()

    def save_current_answer(self):
        """
        Save the current question's answer to the user_answers dictionary.
        """
        answer = self.option_vars.get()
        if answer:
            self.user_answers[self.current_question_index] = answer

    def update_timer_label(self):
        """
        Update the timer label every second.
        """
        if self.timer:
            self.timer_label.configure(text=f"Time Remaining: {self.timer.get_remaining_time()}")
            if self.timer.is_running:
                self.root.after(1000, self.update_timer_label)

    def auto_submit(self):
        """
        Automatically submit the quiz when time runs out.
        """
        self.save_current_answer()
        self.submit_quiz()

    def submit_quiz(self):
        """
        Submit the quiz, calculate score, generate report, and switch to result screen.
        """
        self.save_current_answer()
        if self.timer:
            self.timer.stop_timer()

        # Calculate score and collect correct/incorrect questions
        correct_answers = 0
        total_questions = len(self.questions)
        self.correct_questions = []
        self.incorrect_questions = []
        for i, question in enumerate(self.questions):
            if i in self.user_answers and self.user_answers[i] == question['correct']:
                correct_answers += 1
                self.correct_questions.append(question)
            else:
                self.incorrect_questions.append(question)

        # Get time taken
        time_taken = 10 * 60 - self.timer.remaining_seconds if self.timer else 0

        # Create score report
        self.score_report = ScoreReport(self.user_name, total_questions, correct_answers, time_taken)
        self.score_report.save_to_file()
        self.score_report.generate_chart()

        # Switch to result screen
        self.quiz_frame.pack_forget()
        self.setup_result_screen()

    def setup_result_screen(self):
        """
        Setup the result screen displaying the score report and performance chart.
        """
        # Clear any existing widgets
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        self.result_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(self.result_frame, text="🎉 Quiz Results", font=ctk.CTkFont(size=32, weight="bold"))
        title_label.pack(pady=30)

        # Results card
        results_frame = ctk.CTkFrame(self.result_frame)
        results_frame.pack(fill="x", pady=(0, 30))

        results_text = f"""👤 Name: {self.score_report.user_name}
📊 Score: {self.score_report.score}/{self.score_report.total_questions}
📈 Percentage: {self.score_report.percentage:.2f}%
🏆 Status: {self.score_report.status}
⏱️ Time Taken: {self.score_report.time_taken_str}"""

        results_label = ctk.CTkLabel(results_frame, text=results_text, font=ctk.CTkFont(size=16), justify="left")
        results_label.pack(pady=20, padx=20)

        # Buttons frame
        button_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        # Button container
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(expand=True)

        view_questions_button = ctk.CTkButton(button_container, text="📋 View Questions", command=self.view_questions, width=160, height=45, font=ctk.CTkFont(size=14, weight="bold"))
        view_questions_button.pack(side="left", padx=10)

        view_chart_button = ctk.CTkButton(button_container, text="📊 View Chart", command=self.view_chart, width=160, height=45, font=ctk.CTkFont(size=14, weight="bold"))
        view_chart_button.pack(side="left", padx=10)

        restart_button = ctk.CTkButton(button_container, text="🔄 Take Again", command=self.restart_quiz, width=160, height=45, font=ctk.CTkFont(size=14, weight="bold"))
        restart_button.pack(side="left", padx=10)

        exit_button = ctk.CTkButton(button_container, text="🚪 Exit", command=self.root.quit, width=120, height=45, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#FF6B35", hover_color="#E55A2B")
        exit_button.pack(side="right", padx=10)

    def view_questions(self):
        """
        Display the correct and incorrect questions in a new window.
        """
        questions_window = ctk.CTkToplevel(self.root)
        questions_window.title("📋 Quiz Questions Review")
        questions_window.geometry("900x700")

        # Title
        title_label = ctk.CTkLabel(questions_window, text="Questions Review", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        # Scrollable frame for questions
        scrollable_frame = ctk.CTkScrollableFrame(questions_window)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Correct questions
        if self.correct_questions:
            correct_label = ctk.CTkLabel(scrollable_frame, text="✅ Correct Answers:", font=ctk.CTkFont(size=18, weight="bold"), text_color="#00FF00")
            correct_label.pack(pady=(10, 15), anchor="w")
            for question in self.correct_questions:
                # Question card
                q_frame = ctk.CTkFrame(scrollable_frame)
                q_frame.pack(fill="x", pady=(0, 10))

                q_text = ctk.CTkLabel(q_frame, text=f"Q: {question['question']}", font=ctk.CTkFont(size=14), wraplength=750, justify="left")
                q_text.pack(pady=10, padx=15, anchor="w")

                ans_text = ctk.CTkLabel(q_frame, text=f"✅ Correct Answer: {question['options'][question['correct']]}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00FF00")
                ans_text.pack(pady=(0, 10), padx=15, anchor="w")

        # Incorrect questions
        if self.incorrect_questions:
            incorrect_label = ctk.CTkLabel(scrollable_frame, text="❌ Incorrect Answers:", font=ctk.CTkFont(size=18, weight="bold"), text_color="#FF6B35")
            incorrect_label.pack(pady=(20, 15), anchor="w")
            for i, question in enumerate(self.questions):
                if i in self.user_answers and self.user_answers[i] != question['correct']:
                    # Question card
                    q_frame = ctk.CTkFrame(scrollable_frame)
                    q_frame.pack(fill="x", pady=(0, 10))

                    q_text = ctk.CTkLabel(q_frame, text=f"Q: {question['question']}", font=ctk.CTkFont(size=14), wraplength=750, justify="left")
                    q_text.pack(pady=10, padx=15, anchor="w")

                    user_ans = self.user_answers.get(i, "Not answered")
                    user_ans_text = ctk.CTkLabel(q_frame, text=f"❌ Your Answer: {question['options'].get(user_ans, 'Not answered')}", font=ctk.CTkFont(size=12), text_color="#FF6B35")
                    user_ans_text.pack(pady=(0, 5), padx=15, anchor="w")

                    correct_ans_text = ctk.CTkLabel(q_frame, text=f"✅ Correct Answer: {question['options'][question['correct']]}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00FF00")
                    correct_ans_text.pack(pady=(0, 10), padx=15, anchor="w")

        # Close button
        close_button = ctk.CTkButton(questions_window, text="Close", command=questions_window.destroy, width=120, height=40, font=ctk.CTkFont(size=14, weight="bold"))
        close_button.pack(pady=(0, 20))

    def view_chart(self):
        """
        Display the performance chart using Matplotlib.
        """
        if self.score_report:
            self.score_report.display_chart()

    def restart_quiz(self):
        """
        Restart the quiz by resetting all data and going back to name screen.
        """
        self.current_question_index = 0
        self.user_answers = {}
        self.user_name = ""
        if self.timer:
            self.timer.reset_timer()
        self.result_frame.pack_forget()
        self.setup_name_screen()

# Main function to run the app
def main():
    """
    Main function to initialize and run the QuizApp.
    """
    root = ctk.CTk()
    app = QuizApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
