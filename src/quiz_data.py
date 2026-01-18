import pandas as pd
import numpy as np

class QuizData:
    def __init__(self, file_path='data/sample_quiz.csv'):
        """
        Initialize the QuizData class with the path to the quiz CSV file.
        Loads the quiz questions and answers into a pandas DataFrame.
        """
        self.file_path = file_path
        self.questions_df = None
        self.load_data()

    def load_data(self):
        """
        Load the quiz data from the CSV file using pandas.
        The CSV should have columns: question, option_a, option_b, option_c, option_d, correct_answer
        """
        try:
            self.questions_df = pd.read_csv(self.file_path)
            print(f"Loaded {len(self.questions_df)} questions from {self.file_path}")
        except FileNotFoundError:
            print(f"Error: File {self.file_path} not found.")
            self.questions_df = pd.DataFrame()  # Empty DataFrame as fallback
        except Exception as e:
            print(f"Error loading data: {e}")
            self.questions_df = pd.DataFrame()

    def get_questions(self):
        """
        Return a list of dictionaries, each containing a question and its options.
        Each dict: {'question': str, 'options': {'A': str, 'B': str, 'C': str, 'D': str}, 'correct': str}
        """
        if self.questions_df.empty:
            return []

        questions = []
        for _, row in self.questions_df.iterrows():
            question_dict = {
                'question': row['question'],
                'options': {
                    'A': row['option_a'],
                    'B': row['option_b'],
                    'C': row['option_c'],
                    'D': row['option_d']
                },
                'correct': row['correct_answer']
            }
            questions.append(question_dict)
        return questions

    def get_total_questions(self):
        """
        Return the total number of questions in the quiz.
        """
        return len(self.questions_df) if self.questions_df is not None else 0

    def validate_data(self):
        """
        Validate the loaded data to ensure it has the required columns and data integrity.
        Returns True if valid, False otherwise.
        """
        required_columns = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        if self.questions_df is None or self.questions_df.empty:
            print("No data loaded.")
            return False

        missing_columns = [col for col in required_columns if col not in self.questions_df.columns]
        if missing_columns:
            print(f"Missing columns: {missing_columns}")
            return False

        # Check if correct_answer is one of A, B, C, D
        valid_answers = ['A', 'B', 'C', 'D']
        invalid_answers = self.questions_df[~self.questions_df['correct_answer'].isin(valid_answers)]
        if not invalid_answers.empty:
            print(f"Invalid correct answers found: {invalid_answers['correct_answer'].tolist()}")
            return False

        print("Data validation passed.")
        return True

# Example usage (for testing)
if __name__ == "__main__":
    quiz_data = QuizData()
    if quiz_data.validate_data():
        questions = quiz_data.get_questions()
        print(f"Total questions: {len(questions)}")
        if questions:
            print("Sample question:")
            print(questions[0])
