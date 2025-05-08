import customtkinter as ctk
import tkinter as tk
from typing import Callable, List, Dict, Any, Optional
import time
from quiz_logic import QuizLogic
from high_scores import HighScores


class QuizApp:
    """
    Main application class for the Quiz Game GUI using CustomTkinter.
    """

    def __init__(self, root: ctk.CTk):
        """
        Initialize the Quiz Game GUI.

        Args:
            root: The root CustomTkinter window
        """
        self.root = root
        self.root.title("Quiz Game")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Set appearance mode and default color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize quiz logic and high scores
        self.quiz_logic = QuizLogic()
        self.high_scores = HighScores()

        # Initialize variables
        self.timer_id = None
        self.time_left = 15
        self.selected_option = ""  # Changed from None to empty string
        self.option_buttons = []   # List of tuples (button, option_text)

        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Show welcome screen
        self.show_welcome_screen()

    def clear_frame(self) -> None:
        """Clear all widgets from the main frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_welcome_screen(self) -> None:
        """Display the welcome screen with options to start quiz or view high scores."""
        self.clear_frame()

        # Title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="Quiz Game",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=(50, 30))

        # Difficulty selection
        difficulty_frame = ctk.CTkFrame(self.main_frame)
        difficulty_frame.pack(pady=10, fill=tk.X, padx=100)

        difficulty_label = ctk.CTkLabel(
            difficulty_frame,
            text="Select Difficulty:",
            font=ctk.CTkFont(size=16)
        )
        difficulty_label.pack(side=tk.LEFT, padx=10)

        difficulties = ["all"] + self.quiz_logic.get_available_difficulties()
        difficulty_var = ctk.StringVar(value=difficulties[0])

        difficulty_dropdown = ctk.CTkOptionMenu(
            difficulty_frame,
            values=difficulties,
            variable=difficulty_var,
            width=150
        )
        difficulty_dropdown.pack(side=tk.RIGHT, padx=10)

        # Category selection
        category_frame = ctk.CTkFrame(self.main_frame)
        category_frame.pack(pady=10, fill=tk.X, padx=100)

        category_label = ctk.CTkLabel(
            category_frame,
            text="Select Category:",
            font=ctk.CTkFont(size=16)
        )
        category_label.pack(side=tk.LEFT, padx=10)

        categories = ["all"] + self.quiz_logic.get_available_categories()
        category_var = ctk.StringVar(value=categories[0])

        category_dropdown = ctk.CTkOptionMenu(
            category_frame,
            values=categories,
            variable=category_var,
            width=150
        )
        category_dropdown.pack(side=tk.RIGHT, padx=10)

        # Start button
        start_button = ctk.CTkButton(
            self.main_frame,
            text="Start Quiz",
            font=ctk.CTkFont(size=18),
            height=50,
            command=lambda: self.start_quiz(difficulty_var.get(), category_var.get())
        )
        start_button.pack(pady=20)

        # High scores button
        high_scores_button = ctk.CTkButton(
            self.main_frame,
            text="View High Scores",
            font=ctk.CTkFont(size=18),
            height=50,
            command=self.show_high_scores_screen
        )
        high_scores_button.pack(pady=10)

    def start_quiz(self, difficulty: str, category: str) -> None:
        """
        Start a new quiz with the selected difficulty and category.

        Args:
            difficulty: Selected difficulty level
            category: Selected category
        """
        self.quiz_logic.difficulty = difficulty
        self.quiz_logic.category = category

        if not self.quiz_logic.start_new_game():
            self.show_error("No questions available for the selected criteria.")
            return

        self.show_question_screen()

    def show_error(self, message: str) -> None:
        """
        Display an error message.

        Args:
            message: Error message to display
        """
        self.clear_frame()

        error_label = ctk.CTkLabel(
            self.main_frame,
            text=message,
            font=ctk.CTkFont(size=18),
            text_color="red"
        )
        error_label.pack(pady=(100, 20))

        back_button = ctk.CTkButton(
            self.main_frame,
            text="Back to Menu",
            command=self.show_welcome_screen
        )
        back_button.pack(pady=20)

    def show_question_screen(self) -> None:
        """Display the current question with options and timer."""
        self.clear_frame()
        self.cancel_timer()

        question = self.quiz_logic.get_current_question()
        if not question:
            self.show_results_screen()
            return

        # Progress indicator
        current, total = self.quiz_logic.get_progress()
        progress_frame = ctk.CTkFrame(self.main_frame)
        progress_frame.pack(fill=tk.X, padx=20, pady=(10, 20))

        progress_label = ctk.CTkLabel(
            progress_frame,
            text=f"Question {current} of {total}",
            font=ctk.CTkFont(size=14)
        )
        progress_label.pack(side=tk.LEFT)

        score_label = ctk.CTkLabel(
            progress_frame,
            text=f"Score: {self.quiz_logic.score}",
            font=ctk.CTkFont(size=14)
        )
        score_label.pack(side=tk.RIGHT)

        # Progress bar
        progress_bar = ctk.CTkProgressBar(self.main_frame, width=700)
        progress_bar.pack(padx=20, pady=(0, 20))
        progress_bar.set(current / total)

        # Question
        difficulty = question.get("difficulty", "").capitalize()
        category = question.get("category", "")

        info_label = ctk.CTkLabel(
            self.main_frame,
            text=f"{difficulty} | {category}",
            font=ctk.CTkFont(size=14, slant="italic")
        )
        info_label.pack(pady=(0, 10))

        question_label = ctk.CTkLabel(
            self.main_frame,
            text=question.get("question", ""),
            font=ctk.CTkFont(size=20, weight="bold"),
            wraplength=700
        )
        question_label.pack(pady=(0, 30))

        # Timer
        self.time_left = 15
        timer_frame = ctk.CTkFrame(self.main_frame)
        timer_frame.pack(pady=(0, 20))

        timer_label = ctk.CTkLabel(
            timer_frame,
            text=f"Time left: {self.time_left}s",
            font=ctk.CTkFont(size=16)
        )
        timer_label.pack()

        # Options
        options_frame = ctk.CTkFrame(self.main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=10)

        # Reset selected option
        self.selected_option = ""
        self.option_buttons = []

        options = self.quiz_logic.get_shuffled_options()
        for option in options:
            option_button = ctk.CTkButton(
                options_frame,
                text=option,
                font=ctk.CTkFont(size=16),
                height=50,
                command=lambda opt=option: self.select_option(opt)
            )
            option_button.pack(fill=tk.X, pady=5)
            self.option_buttons.append((option_button, option))

        # Submit button
        self.submit_button = ctk.CTkButton(
            self.main_frame,
            text="Submit Answer",
            font=ctk.CTkFont(size=18),
            height=50,
            state="disabled",
            command=self.submit_answer
        )
        self.submit_button.pack(pady=20)

        # Start timer
        self.start_timer(timer_label)

    def select_option(self, option: str) -> None:
        """
        Handle option selection.

        Args:
            option: The selected option
        """
        self.selected_option = option
        self.submit_button.configure(state="normal")

        # Update button appearance
        for button, opt in self.option_buttons:
            if opt == option:
                button.configure(fg_color="#1f538d")  # Highlight selected
            else:
                button.configure(fg_color="#3a7ebf")  # Reset others

    def start_timer(self, timer_label: ctk.CTkLabel) -> None:
        """
        Start the countdown timer for the current question.

        Args:
            timer_label: Label to display the timer
        """
        def update_timer():
            self.time_left -= 1

            # Check if the timer_label still exists before updating it
            try:
                if timer_label.winfo_exists():
                    timer_label.configure(text=f"Time left: {self.time_left}s")

                    if self.time_left <= 0:
                        self.time_expired()
                    else:
                        self.timer_id = self.root.after(1000, update_timer)
                else:
                    # Label no longer exists, cancel the timer
                    self.cancel_timer()
            except (tk.TclError, RuntimeError):
                # Handle any Tkinter errors by canceling the timer
                self.cancel_timer()

        self.timer_id = self.root.after(1000, update_timer)

    def cancel_timer(self) -> None:
        """Cancel the current timer if active."""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def time_expired(self) -> None:
        """Handle timer expiration."""
        self.cancel_timer()

        # Show correct answer
        self.show_correct_answer()

        # Wait 2 seconds before moving to next question
        self.root.after(2000, self.move_to_next_question)

    def submit_answer(self) -> None:
        """Handle answer submission."""
        self.cancel_timer()

        is_correct = self.quiz_logic.check_answer(self.selected_option)
        self.show_correct_answer(is_correct)

        # Wait 2 seconds before moving to next question
        self.root.after(2000, self.move_to_next_question)

    def show_correct_answer(self, is_correct: Optional[bool] = None) -> None:
        """
        Highlight the correct answer and the user's selection.

        Args:
            is_correct: Whether the user's answer is correct
        """
        question = self.quiz_logic.get_current_question()
        if not question:
            return

        correct_answer = question.get("correct_answer", "")

        for button, option in self.option_buttons:
            if option == correct_answer:
                button.configure(fg_color="green")  # Correct answer
            elif is_correct is not None and option == self.selected_option and not is_correct:
                button.configure(fg_color="red")  # Wrong answer

        self.submit_button.configure(state="disabled")

    def move_to_next_question(self) -> None:
        """Move to the next question or show results if quiz is complete."""
        if self.quiz_logic.next_question():
            self.show_question_screen()
        else:
            self.show_results_screen()

    def show_results_screen(self) -> None:
        """Display the final results screen with score and name input."""
        self.clear_frame()

        # Results title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="Quiz Complete!",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(50, 20))

        # Final score
        score_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Your Score: {self.quiz_logic.score}",
            font=ctk.CTkFont(size=24)
        )
        score_label.pack(pady=(0, 30))

        # Check if it's a high score
        if self.high_scores.is_high_score(self.quiz_logic.score):
            high_score_label = ctk.CTkLabel(
                self.main_frame,
                text="Congratulations! You got a high score!",
                font=ctk.CTkFont(size=18),
                text_color="#FFD700"  # Gold color
            )
            high_score_label.pack(pady=(0, 20))

            # Name input
            name_frame = ctk.CTkFrame(self.main_frame)
            name_frame.pack(pady=10)

            name_label = ctk.CTkLabel(
                name_frame,
                text="Enter your name:",
                font=ctk.CTkFont(size=16)
            )
            name_label.pack(side=tk.LEFT, padx=10)

            name_entry = ctk.CTkEntry(name_frame, width=200)
            name_entry.pack(side=tk.RIGHT, padx=10)
            name_entry.insert(0, "Player")

            # Save score button
            save_button = ctk.CTkButton(
                self.main_frame,
                text="Save Score",
                font=ctk.CTkFont(size=16),
                command=lambda: self.save_score(name_entry.get())
            )
            save_button.pack(pady=10)

        # Buttons
        buttons_frame = ctk.CTkFrame(self.main_frame)
        buttons_frame.pack(pady=30)

        play_again_button = ctk.CTkButton(
            buttons_frame,
            text="Play Again",
            font=ctk.CTkFont(size=16),
            width=150,
            command=self.show_welcome_screen
        )
        play_again_button.pack(side=tk.LEFT, padx=10)

        high_scores_button = ctk.CTkButton(
            buttons_frame,
            text="View High Scores",
            font=ctk.CTkFont(size=16),
            width=150,
            command=self.show_high_scores_screen
        )
        high_scores_button.pack(side=tk.RIGHT, padx=10)

    def save_score(self, name: str) -> None:
        """
        Save the player's score to high scores.

        Args:
            name: Player's name
        """
        self.high_scores.save_score(name, self.quiz_logic.score)
        self.show_high_scores_screen()

    def show_high_scores_screen(self) -> None:
        """Display the high scores screen."""
        self.clear_frame()

        # Refresh high scores
        self.high_scores.load_scores()

        # Title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="High Scores",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(50, 30))

        # Scores table
        scores_frame = ctk.CTkFrame(self.main_frame)
        scores_frame.pack(pady=20, fill=tk.BOTH, expand=True, padx=100)

        # Headers
        header_frame = ctk.CTkFrame(scores_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        rank_header = ctk.CTkLabel(
            header_frame,
            text="Rank",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=100
        )
        rank_header.pack(side=tk.LEFT)

        name_header = ctk.CTkLabel(
            header_frame,
            text="Name",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=300
        )
        name_header.pack(side=tk.LEFT)

        score_header = ctk.CTkLabel(
            header_frame,
            text="Score",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=100
        )
        score_header.pack(side=tk.LEFT)

        # Scores
        top_scores = self.high_scores.get_top_scores()

        if not top_scores:
            no_scores_label = ctk.CTkLabel(
                scores_frame,
                text="No high scores yet!",
                font=ctk.CTkFont(size=16, slant="italic")
            )
            no_scores_label.pack(pady=20)
        else:
            for i, (name, score) in enumerate(top_scores, 1):
                score_row = ctk.CTkFrame(scores_frame)
                score_row.pack(fill=tk.X, pady=5)

                rank_label = ctk.CTkLabel(
                    score_row,
                    text=f"{i}",
                    font=ctk.CTkFont(size=14),
                    width=100
                )
                rank_label.pack(side=tk.LEFT)

                name_label = ctk.CTkLabel(
                    score_row,
                    text=name,
                    font=ctk.CTkFont(size=14),
                    width=300,
                    anchor="w"
                )
                name_label.pack(side=tk.LEFT)

                score_label = ctk.CTkLabel(
                    score_row,
                    text=str(score),
                    font=ctk.CTkFont(size=14),
                    width=100
                )
                score_label.pack(side=tk.LEFT)

        # Back button
        back_button = ctk.CTkButton(
            self.main_frame,
            text="Back to Menu",
            font=ctk.CTkFont(size=16),
            command=self.show_welcome_screen
        )
        back_button.pack(pady=20)
