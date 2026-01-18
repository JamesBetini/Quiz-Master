import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import os
import tkinter as tk

class ScoreReport:
    """
    Class to handle score calculation, result display, saving to file, and generating performance charts.
    """
    def __init__(self, user_name, total_questions, correct_answers, time_taken_seconds):
        """
        Initialize the ScoreReport with user data.

        Args:
            user_name (str): Name of the user
            total_questions (int): Total number of questions
            correct_answers (int): Number of correct answers
            time_taken_seconds (int): Time taken in seconds
        """
        self.user_name = user_name
        self.total_questions = total_questions
        self.score = correct_answers
        self.percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        self.status = "Pass" if self.percentage >= 50 else "Fail"
        self.time_taken_seconds = time_taken_seconds
        self.time_taken_str = self.format_time(time_taken_seconds)

        # File paths
        self.results_dir = "results"
        self.results_file = os.path.join(self.results_dir, "quiz_results.csv")
        self.chart_file = os.path.join(self.results_dir, f"{user_name}_performance.png")

    def format_time(self, seconds):
        """
        Format seconds into MM:SS format.

        Args:
            seconds (int): Time in seconds

        Returns:
            str: Formatted time string
        """
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def save_to_file(self):
        """
        Save the quiz results to a CSV file.
        """
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)

        # Prepare data
        data = {
            'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'User Name': [self.user_name],
            'Score': [f"{self.score}/{self.total_questions}"],
            'Percentage': [f"{self.percentage:.2f}%"],
            'Status': [self.status],
            'Time Taken': [self.time_taken_str]
        }

        df = pd.DataFrame(data)

        # Append to existing file or create new one
        if os.path.exists(self.results_file):
            existing_df = pd.read_csv(self.results_file)
            df = pd.concat([existing_df, df], ignore_index=True)

        df.to_csv(self.results_file, index=False)

    def generate_chart(self):
        """
        Generate a performance chart using Matplotlib and save it to a file.
        """
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)

        # Data for the chart
        labels = ['Correct', 'Incorrect']
        sizes = [self.score, self.total_questions - self.score]
        colors = ['#4CAF50', '#F44336']  # Green for correct, red for incorrect
        explode = (0.1, 0)  # Explode the correct slice

        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
               shadow=True, startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Title
        ax.set_title(f'Quiz Performance - {self.user_name}\nScore: {self.score}/{self.total_questions} ({self.percentage:.2f}%)',
                     fontsize=16, fontweight='bold')

        # Save the chart
        plt.savefig(self.chart_file, dpi=300, bbox_inches='tight')
        plt.close()

    def display_chart(self):
        """
        Display the performance chart using Matplotlib.
        """
        if os.path.exists(self.chart_file):
            img = plt.imread(self.chart_file)
            plt.imshow(img)
            plt.axis('off')
            plt.show()
        else:
            tk.messagebox.showerror("Error", "Performance chart not found. Please generate the chart first.")
