import customtkinter as ctk
import tkinter as tk
from typing import Callable, List, Dict, Any, Optional, Tuple
import time
try:
    from PIL import Image, ImageTk
except ImportError:
    print("PIL not found. Please install it using: pip install pillow")
    Image = None
    ImageTk = None
import os
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
        self.root.title("Quiz Master")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Set minimum window size for responsiveness
        self.root.minsize(400, 500)

        # Configure row and column weights for responsiveness
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Set appearance mode and default color theme
        ctk.set_appearance_mode("system")  # Use system preference
        ctk.set_default_color_theme("blue")

        # Color scheme
        self.colors = {
            "primary": "#3a7ebf",
            "secondary": "#1f538d",
            "accent": "#f5a742",
            "correct": "#4CAF50",
            "incorrect": "#F44336",
            "highlight": "#FFD700",
            "text_light": "#ffffff",
            "text_dark": "#333333",
            "background": "#2b2b2b"
        }

        # Initialize quiz logic and high scores
        self.quiz_logic = QuizLogic()
        self.high_scores = HighScores()

        # Initialize variables
        self.timer_id = None
        self.time_left = 20  # Increased time
        self.selected_option = ""
        self.option_buttons = []
        self.current_streak = 0
        self.longest_streak = 0
        self.achievements = {}
        self.theme_var = ctk.StringVar(value="system")
        self.font_scale = 1.0  # Default font scale

        # Create main container that fills the window
        self.container = ctk.CTkFrame(self.root)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Create main frame with some padding
        self.main_frame = ctk.CTkFrame(self.container)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Create a frame for content to enable animation effects
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, sticky="nsew")

        # Register for window resize event
        self.root.bind("<Configure>", self.on_window_resize)

        # Show welcome screen immediately
        self.show_welcome_screen()

    def clear_frame(self) -> None:
        """Clear all widgets from the content frame."""
        # Destroy previous content frame
        if hasattr(self, 'content_frame') and self.content_frame is not None:
            self.content_frame.destroy()

        # Create new content frame
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def on_window_resize(self, event) -> None:
        """Handle window resize events to ensure responsive layout."""
        # Only process events from the root window
        if event.widget == self.root:
            width = event.width
            # Adjust font sizes or layout based on window width
            if width < 500:
                self.font_scale = 0.8
            elif width < 700:
                self.font_scale = 0.9
            else:
                self.font_scale = 1.0

    def get_font(self, size: int, weight: str = "normal", slant: str = "roman") -> ctk.CTkFont:
        """
        Get a scaled font based on window size.

        Args:
            size: Base font size
            weight: Font weight (normal, bold)
            slant: Font slant (roman, italic)

        Returns:
            Scaled CTkFont object
        """
        # Convert string parameters to valid values for CTkFont
        weight_val = "bold" if weight == "bold" else "normal"
        slant_val = "italic" if slant == "italic" else "roman"

        # Scale the font size based on window size
        scaled_size = int(size * getattr(self, 'font_scale', 1.0))

        # Create and return a new font
        return ctk.CTkFont(size=scaled_size, weight=weight_val, slant=slant_val)

    def show_welcome_screen(self) -> None:
        """Display the welcome screen with options to start quiz or view high scores."""
        self.clear_frame()

        welcome_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        welcome_container.pack(fill=tk.BOTH, expand=True)

        # Title with animated effect
        title_frame = ctk.CTkFrame(welcome_container, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(30, 20))

        title_label = ctk.CTkLabel(
            title_frame,
            text="Quiz Master",
            font=self.get_font(38, "bold"),
            text_color=self.colors["accent"]
        )
        title_label.pack(pady=(10, 5))

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Test your knowledge and compete for high scores!",
            font=self.get_font(16, slant="italic")
        )
        subtitle_label.pack(pady=(0, 30))

        # Options frame
        options_frame = ctk.CTkFrame(welcome_container)
        options_frame.pack(fill=tk.X, padx=50, pady=10, expand=False)

        # Create a grid inside options frame
        options_frame.grid_columnconfigure(0, weight=1)
        options_frame.grid_columnconfigure(1, weight=1)

        # Number of Questions
        questions_label = ctk.CTkLabel(
            options_frame,
            text="Number of Questions:",
            font=self.get_font(16)
        )
        questions_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        questions_values = ["5", "10", "15", "20"]
        questions_var = ctk.StringVar(value="10")

        questions_dropdown = ctk.CTkOptionMenu(
            options_frame,
            values=questions_values,
            variable=questions_var,
            width=150,
            dynamic_resizing=False
        )
        questions_dropdown.grid(row=0, column=1, sticky="e", padx=20, pady=(20, 10))

        # Difficulty selection
        difficulty_label = ctk.CTkLabel(
            options_frame,
            text="Difficulty Level:",
            font=self.get_font(16)
        )
        difficulty_label.grid(row=1, column=0, sticky="w", padx=20, pady=10)

        difficulties = ["all"] + self.quiz_logic.get_available_difficulties()
        difficulty_var = ctk.StringVar(value=difficulties[0])

        difficulty_dropdown = ctk.CTkOptionMenu(
            options_frame,
            values=difficulties,
            variable=difficulty_var,
            width=150,
            dynamic_resizing=False
        )
        difficulty_dropdown.grid(row=1, column=1, sticky="e", padx=20, pady=10)

        # Category selection
        category_label = ctk.CTkLabel(
            options_frame,
            text="Category:",
            font=self.get_font(16)
        )
        category_label.grid(row=2, column=0, sticky="w", padx=20, pady=10)

        categories = ["all"] + self.quiz_logic.get_available_categories()
        category_var = ctk.StringVar(value=categories[0])

        category_dropdown = ctk.CTkOptionMenu(
            options_frame,
            values=categories,
            variable=category_var,
            width=150,
            dynamic_resizing=False
        )
        category_dropdown.grid(row=2, column=1, sticky="e", padx=20, pady=10)

        # Timer duration
        timer_label = ctk.CTkLabel(
            options_frame,
            text="Timer (seconds):",
            font=self.get_font(16)
        )
        timer_label.grid(row=3, column=0, sticky="w", padx=20, pady=10)

        timer_values = ["10", "15", "20", "30"]
        timer_var = ctk.StringVar(value="20")

        timer_dropdown = ctk.CTkOptionMenu(
            options_frame,
            values=timer_values,
            variable=timer_var,
            width=150,
            dynamic_resizing=False
        )
        timer_dropdown.grid(row=3, column=1, sticky="e", padx=20, pady=10)

        # Theme selection
        theme_label = ctk.CTkLabel(
            options_frame,
            text="Theme:",
            font=ctk.CTkFont(size=16)
        )
        theme_label.grid(row=4, column=0, sticky="w", padx=20, pady=(10, 20))

        # Create dropdown for theme selection instead of segmented button
        theme_values = ["Light", "Dark", "System"]
        theme_dropdown = ctk.CTkOptionMenu(
            options_frame,
            values=theme_values,
            command=self.change_theme,
            width=150,
            dynamic_resizing=False
        )
        theme_dropdown.grid(row=4, column=1, sticky="e", padx=20, pady=(10, 20))

        # Set default theme
        theme_dropdown.set("System")

        # Buttons frame
        buttons_frame = ctk.CTkFrame(welcome_container, fg_color="transparent")
        buttons_frame.pack(fill=tk.X, pady=30)

        # Centered button frame
        center_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        center_frame.pack(expand=True)

        # Start button with accent color
        start_button = ctk.CTkButton(
            center_frame,
            text="Start Quiz",
            font=self.get_font(20),
            height=50,
            width=200,
            fg_color=self.colors["accent"],
            hover_color=self.colors["secondary"],
            command=lambda: self.start_quiz(
                difficulty_var.get(),
                category_var.get(),
                int(questions_var.get()),
                int(timer_var.get())
            )
        )
        start_button.pack(pady=10)

        # High scores button
        high_scores_button = ctk.CTkButton(
            center_frame,
            text="View High Scores",
            font=self.get_font(16),
            height=40,
            width=200,
            command=self.show_high_scores_screen
        )
        high_scores_button.pack(pady=10)

        # Achievements button
        achievements_button = ctk.CTkButton(
            center_frame,
            text="Achievements",
            font=self.get_font(16),
            height=40,
            width=200,
            command=self.show_achievements_screen
        )
        achievements_button.pack(pady=10)

    def change_theme(self, value: str) -> None:
        """
        Change the application theme.

        Args:
            value: Theme name (Light, Dark, System)
        """
        theme_map = {"Light": "light", "Dark": "dark", "System": "system"}
        ctk.set_appearance_mode(theme_map[value])

    def start_quiz(self, difficulty: str, category: str, num_questions: int = 10, timer_duration: int = 20) -> None:
        """
        Start a new quiz with the selected options.

        Args:
            difficulty: Selected difficulty level
            category: Selected category
            num_questions: Number of questions for the quiz
            timer_duration: Timer duration in seconds
        """
        self.quiz_logic.difficulty = difficulty
        self.quiz_logic.category = category
        self.quiz_logic.questions_per_game = num_questions
        self.time_left = timer_duration
        self.current_streak = 0
        self.longest_streak = 0

        if not self.quiz_logic.start_new_game():
            self.show_error("No questions available for the selected criteria.")
            return

        self.show_question_screen()

    def show_error(self, message: str) -> None:
        """
        Display an error message with improved styling.

        Args:
            message: Error message to display
        """
        self.clear_frame()

        error_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        error_container.pack(fill=tk.BOTH, expand=True)

        error_box = ctk.CTkFrame(
            error_container,
            fg_color=self.colors["incorrect"],
            corner_radius=10
        )
        error_box.pack(pady=(100, 20), padx=50, ipadx=20, ipady=20)

        error_icon = ctk.CTkLabel(
            error_box,
            text="⚠️",
            font=self.get_font(30)
        )
        error_icon.pack(pady=(10, 5))

        error_label = ctk.CTkLabel(
            error_box,
            text=message,
            font=self.get_font(18),
            text_color=self.colors["text_light"]
        )
        error_label.pack(pady=(0, 10))

        back_button = ctk.CTkButton(
            error_container,
            text="Back to Menu",
            font=self.get_font(16),
            width=150,
            command=self.show_welcome_screen
        )
        back_button.pack(pady=20)

    def show_question_screen(self) -> None:
        """Display the current question with options and timer with enhanced UI."""
        self.clear_frame()
        self.cancel_timer()

        question = self.quiz_logic.get_current_question()
        if not question:
            self.show_results_screen()
            return

        question_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        question_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top bar with stats
        top_bar = ctk.CTkFrame(question_container)
        top_bar.pack(fill=tk.X, pady=(5, 15))

        # Progress indicator
        current, total = self.quiz_logic.get_progress()

        progress_label = ctk.CTkLabel(
            top_bar,
            text=f"Question {current} of {total}",
            font=self.get_font(14)
        )
        progress_label.pack(side=tk.LEFT, padx=10)

        # Streak indicator
        streak_frame = ctk.CTkFrame(top_bar, fg_color=self.colors["accent"] if self.current_streak > 2 else "transparent")
        streak_frame.pack(side=tk.LEFT, padx=10)

        streak_label = ctk.CTkLabel(
            streak_frame,
            text=f"🔥 Streak: {self.current_streak}",
            font=self.get_font(14),
            text_color="black" if self.current_streak > 2 else None
        )
        streak_label.pack(padx=5)

        score_label = ctk.CTkLabel(
            top_bar,
            text=f"Score: {self.quiz_logic.score}",
            font=self.get_font(14, "bold")
        )
        score_label.pack(side=tk.RIGHT, padx=10)

        # Progress bar with color
        progress_frame = ctk.CTkFrame(question_container)
        progress_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=700,
            progress_color=self.colors["accent"],
            height=10
        )
        progress_bar.pack(fill=tk.X, pady=5)
        progress_bar.set(current / total)

        # Question card
        question_card = ctk.CTkFrame(question_container)
        question_card.pack(fill=tk.X, padx=20, pady=10, ipady=10)

        # Question metadata
        meta_frame = ctk.CTkFrame(question_card, fg_color="transparent")
        meta_frame.pack(fill=tk.X, padx=15, pady=(10, 0))

        difficulty = question.get("difficulty", "").capitalize()
        category = question.get("category", "")

        # Create difficulty badge
        diff_colors = {"Easy": "#4CAF50", "Medium": "#FF9800", "Hard": "#F44336"}
        diff_badge = ctk.CTkFrame(
            meta_frame,
            fg_color=diff_colors.get(difficulty, self.colors["primary"]),
            corner_radius=5
        )
        diff_badge.pack(side=tk.LEFT, padx=(0, 10))

        diff_label = ctk.CTkLabel(
            diff_badge,
            text=difficulty,
            font=self.get_font(12),
            text_color="white"
        )
        diff_label.pack(padx=8, pady=2)

        # Category badge
        cat_badge = ctk.CTkFrame(meta_frame, fg_color=self.colors["secondary"], corner_radius=5)
        cat_badge.pack(side=tk.LEFT)

        cat_label = ctk.CTkLabel(
            cat_badge,
            text=category,
            font=self.get_font(12),
            text_color="white"
        )
        cat_label.pack(padx=8, pady=2)

        # Points indicator
        points_map = {"Easy": 10, "Medium": 15, "Hard": 20}
        points_value = points_map.get(difficulty, 10)

        points_label = ctk.CTkLabel(
            meta_frame,
            text=f"+{points_value} pts",
            font=self.get_font(12, "bold"),
            text_color=self.colors["highlight"]
        )
        points_label.pack(side=tk.RIGHT)

        # Question text with better wrapping
        question_text = question.get("question", "")
        question_label = ctk.CTkLabel(
            question_card,
            text=question_text,
            font=self.get_font(20, "bold"),
            wraplength=600,
            justify="left"
        )
        question_label.pack(pady=(15, 20), padx=20)

        # Timer with circular progress bar
        timer_frame = ctk.CTkFrame(question_container)
        timer_frame.pack(pady=(0, 15))

        timer_label = ctk.CTkLabel(
            timer_frame,
            text=f"{self.time_left}",
            font=self.get_font(22, "bold")
        )
        timer_label.pack(pady=5)

        timer_text = ctk.CTkLabel(
            timer_frame,
            text="seconds remaining",
            font=self.get_font(12)
        )
        timer_text.pack(pady=(0, 5))

        # Options in a grid layout for better responsiveness
        options_frame = ctk.CTkFrame(question_container)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=1)

        # Reset selected option
        self.selected_option = ""
        self.option_buttons = []

        options = self.quiz_logic.get_shuffled_options()

        # Arrange options in a 2x2 grid
        row, col = 0, 0
        option_letters = ["A", "B", "C", "D"]

        for i, option in enumerate(options):
            option_frame = ctk.CTkFrame(options_frame)
            option_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            option_button = ctk.CTkButton(
                option_frame,
                text=f"{option_letters[i]}. {option}",
                font=self.get_font(16),
                height=60,
                anchor="w",
                fg_color=self.colors["primary"],
                hover_color=self.colors["secondary"],
                command=lambda opt=option: self.select_option(opt)
            )
            option_button.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.option_buttons.append((option_button, option))

            # Move to next column or row
            col += 1
            if col > 1:
                col = 0
                row += 1

        # Submit button with accent color
        button_frame = ctk.CTkFrame(question_container, fg_color="transparent")
        button_frame.pack(pady=15)

        self.submit_button = ctk.CTkButton(
            button_frame,
            text="Submit Answer",
            font=self.get_font(18),
            height=50,
            width=200,
            state="disabled",
            fg_color=self.colors["accent"],
            hover_color=self.colors["secondary"],
            command=self.submit_answer
        )
        self.submit_button.pack()

        # Hint button (disabled if no hint available)
        hint_button = ctk.CTkButton(
            button_frame,
            text="Use Hint (−5 pts)",
            font=self.get_font(14),
            height=30,
            width=150,
            fg_color="gray",
            command=self.show_hint
        )
        hint_button.pack(pady=10)

        # Skip button
        skip_button = ctk.CTkButton(
            button_frame,
            text="Skip Question",
            font=self.get_font(14),
            height=30,
            width=150,
            fg_color="#555555",
            hover_color="#444444",
            command=self.skip_question
        )
        skip_button.pack()

        # Start timer
        self.start_timer(timer_label)

    def show_hint(self) -> None:
        """Show a hint by eliminating wrong options."""
        question = self.quiz_logic.get_current_question()
        if not question:
            return

        correct_answer = question.get("correct_answer", "")

        # Find buttons with wrong answers (up to 2)
        wrong_buttons = [(btn, opt) for btn, opt in self.option_buttons if opt != correct_answer]

        # Randomly select 1-2 wrong options to eliminate
        import random
        to_eliminate = min(2, len(wrong_buttons))
        eliminated = random.sample(wrong_buttons, to_eliminate)

        # Apply visual effect to eliminated options
        for button, _ in eliminated:
            button.configure(state="disabled", fg_color="gray")

        # Reduce score for using hint
        self.quiz_logic.score = max(0, self.quiz_logic.score - 5)

        # Update score display
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkFrame):
                        for label in child.winfo_children():
                            if isinstance(label, ctk.CTkLabel) and "Score:" in label.cget("text"):
                                label.configure(text=f"Score: {self.quiz_logic.score}")
                                break

    def skip_question(self) -> None:
        """Skip the current question and move to the next one."""
        self.cancel_timer()
        # Reset streak as the question was skipped
        self.current_streak = 0
        self.move_to_next_question()

    def select_option(self, option: str) -> None:
        """
        Handle option selection with enhanced visual feedback.

        Args:
            option: The selected option
        """
        self.selected_option = option
        self.submit_button.configure(state="normal")

        # Update button appearance with improved visual feedback
        for button, opt in self.option_buttons:
            if opt == option:
                button.configure(
                    fg_color=self.colors["secondary"],
                    border_color=self.colors["highlight"],
                    border_width=2
                )  # Highlight selected
            else:
                button.configure(
                    fg_color=self.colors["primary"],
                    border_width=0
                )  # Reset others

    def start_timer(self, timer_label: ctk.CTkLabel) -> None:
        """
        Start the countdown timer for the current question with visual cues.

        Args:
            timer_label: Label to display the timer
        """
        def update_timer():
            # Use a try-except block to handle any potential errors
            try:
                self.time_left -= 1

                # Check if the timer_label still exists before updating it
                if timer_label.winfo_exists():
                    # Use after method to ensure UI updates happen in the main thread
                    self.root.after_idle(lambda: timer_label.configure(text=f"{self.time_left}"))

                    # Change color to warn when time is running low
                    if self.time_left <= 5:
                        self.root.after_idle(lambda: timer_label.configure(text_color=self.colors["incorrect"]))
                    elif self.time_left <= 10:
                        self.root.after_idle(lambda: timer_label.configure(text_color=self.colors["accent"]))

                    if self.time_left <= 0:
                        # Use after_idle to ensure time_expired is called in the main thread
                        self.root.after_idle(self.time_expired)
                    else:
                        # Schedule the next timer update
                        self.timer_id = self.root.after(1000, update_timer)
                else:
                    # Label no longer exists, cancel the timer
                    self.cancel_timer()
            except (tk.TclError, RuntimeError, Exception) as e:
                # Handle any errors by canceling the timer and logging the error
                print(f"Timer error: {e}")
                self.cancel_timer()

        # Start the timer
        self.timer_id = self.root.after(1000, update_timer)

    def cancel_timer(self) -> None:
        """Cancel the current timer if active."""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def time_expired(self) -> None:
        """Handle timer expiration with visual feedback."""
        self.cancel_timer()

        # Reset streak
        self.current_streak = 0

        # Show "Time's Up!" message
        for widget in self.content_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                time_up_label = ctk.CTkLabel(
                    widget,
                    text="Time's Up!",
                    font=self.get_font(24, "bold"),
                    text_color=self.colors["incorrect"]
                )
                time_up_label.pack(pady=10)
                break

        # Show correct answer
        self.show_correct_answer()

        # Wait 2 seconds before moving to next question
        self.root.after(2000, self.move_to_next_question)

    def submit_answer(self) -> None:
        """Handle answer submission with feedback and streak tracking."""
        self.cancel_timer()

        is_correct = self.quiz_logic.check_answer(self.selected_option)
        self.show_correct_answer(is_correct)

        # Update streak
        if is_correct:
            self.current_streak += 1
            self.longest_streak = max(self.longest_streak, self.current_streak)

            # Add bonus points for streaks
            if self.current_streak >= 3:
                streak_bonus = self.current_streak
                self.quiz_logic.score += streak_bonus

                # Show streak bonus message
                streak_bonus_label = ctk.CTkLabel(
                    self.content_frame,
                    text=f"🔥 Streak Bonus: +{streak_bonus} points!",
                    font=self.get_font(16, "bold"),
                    text_color=self.colors["highlight"]
                )
                streak_bonus_label.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

            # Track achievement for 5+ streak
            if self.current_streak >= 5 and "streak_5" not in self.achievements:
                self.achievements["streak_5"] = True
                self.show_achievement("Hot Streak", "Answered 5 questions correctly in a row")
        else:
            self.current_streak = 0

        # Track perfect score achievement
        current, total = self.quiz_logic.get_progress()
        if current == total and is_correct:
            difficulty = self.quiz_logic.difficulty
            if difficulty != "all" and f"perfect_{difficulty}" not in self.achievements:
                self.achievements[f"perfect_{difficulty}"] = True
                self.show_achievement(
                    f"Perfect {difficulty.capitalize()} Quiz",
                    f"Answered all {difficulty} questions correctly"
                )

        # Wait 2 seconds before moving to next question
        self.root.after(2000, self.move_to_next_question)

    def show_achievement(self, title: str, description: str) -> None:
        """
        Display an achievement notification.

        Args:
            title: Achievement title
            description: Achievement description
        """
        # Create achievement popup
        popup = ctk.CTkToplevel(self.root)
        popup.title("Achievement Unlocked!")
        popup.geometry("400x200")
        popup.resizable(False, False)

        # Position popup in center of parent window
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 100
        popup.geometry(f"+{x}+{y}")

        # Achievement content
        frame = ctk.CTkFrame(popup)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Trophy emoji and title
        header_label = ctk.CTkLabel(
            frame,
            text="🏆 Achievement Unlocked!",
            font=self.get_font(22, "bold"),
            text_color=self.colors["highlight"]
        )
        header_label.pack(pady=(10, 5))

        # Achievement title
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=self.get_font(18, "bold")
        )
        title_label.pack(pady=(5, 10))

        # Description
        desc_label = ctk.CTkLabel(
            frame,
            text=description,
            font=self.get_font(14)
        )
        desc_label.pack(pady=(0, 15))

        # Close button
        close_button = ctk.CTkButton(
            frame,
            text="Continue",
            command=popup.destroy,
            width=100
        )
        close_button.pack()

    def show_correct_answer(self, is_correct: Optional[bool] = None) -> None:
        """
        Highlight the correct answer and the user's selection with enhanced visual feedback.

        Args:
            is_correct: Whether the user's answer is correct
        """
        question = self.quiz_logic.get_current_question()
        if not question:
            return

        correct_answer = question.get("correct_answer", "")

        # Create feedback message
        feedback_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.colors["correct"] if is_correct else self.colors["incorrect"],
            corner_radius=10
        )
        feedback_frame.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        feedback_text = "✓ Correct!" if is_correct else "✗ Incorrect!"
        feedback_label = ctk.CTkLabel(
            feedback_frame,
            text=feedback_text,
            font=self.get_font(18, "bold"),
            text_color="white"
        )
        feedback_label.pack(padx=15, pady=8)

        # Update buttons with improved visual feedback
        for button, option in self.option_buttons:
            if option == correct_answer:
                button.configure(
                    fg_color=self.colors["correct"],
                    hover_color=self.colors["correct"],
                    text_color="white"
                )  # Correct answer
            elif is_correct is not None and option == self.selected_option and not is_correct:
                button.configure(
                    fg_color=self.colors["incorrect"],
                    hover_color=self.colors["incorrect"],
                    text_color="white"
                )  # Wrong answer
            else:
                button.configure(state="disabled", fg_color="#555555")  # Disable other options

        self.submit_button.configure(state="disabled")

    def move_to_next_question(self) -> None:
        """Move to the next question or show results if quiz is complete."""
        if self.quiz_logic.next_question():
            self.show_question_screen()
        else:
            self.show_results_screen()

    def show_results_screen(self) -> None:
        """Display the final results screen with enhanced visual feedback and statistics."""
        self.clear_frame()

        results_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        results_container.pack(fill=tk.BOTH, expand=True)

        # Results title with celebration emojis
        title_frame = ctk.CTkFrame(results_container, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(20, 0))

        title_label = ctk.CTkLabel(
            title_frame,
            text="🎉 Quiz Complete! 🎉",
            font=self.get_font(32, "bold"),
            text_color=self.colors["accent"]
        )
        title_label.pack(pady=(20, 10))

        # Statistics card
        stats_frame = ctk.CTkFrame(results_container)
        stats_frame.pack(pady=20, padx=40, fill=tk.X)

        # Final score with large display
        score_label = ctk.CTkLabel(
            stats_frame,
            text=f"{self.quiz_logic.score}",
            font=self.get_font(48, "bold"),
            text_color=self.colors["highlight"]
        )
        score_label.pack(pady=(20, 5))

        score_text = ctk.CTkLabel(
            stats_frame,
            text="POINTS",
            font=self.get_font(16),
        )
        score_text.pack(pady=(0, 20))

        # Divider
        divider = ctk.CTkFrame(stats_frame, height=2, fg_color=self.colors["primary"])
        divider.pack(fill=tk.X, padx=30, pady=10)

        # Additional statistics
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(pady=10, fill=tk.X)

        # Configure columns for responsiveness
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)

        # Longest streak
        streak_title = ctk.CTkLabel(
            stats_grid,
            text="Longest Streak:",
            font=self.get_font(14),
            anchor="e"
        )
        streak_title.grid(row=0, column=0, sticky="e", padx=(20, 10), pady=5)

        streak_value = ctk.CTkLabel(
            stats_grid,
            text=f"{self.longest_streak}",
            font=self.get_font(14, "bold"),
            anchor="w"
        )
        streak_value.grid(row=0, column=1, sticky="w", padx=(10, 20), pady=5)

        # Difficulty
        difficulty_title = ctk.CTkLabel(
            stats_grid,
            text="Difficulty:",
            font=self.get_font(14),
            anchor="e"
        )
        difficulty_title.grid(row=1, column=0, sticky="e", padx=(20, 10), pady=5)

        difficulty_value = ctk.CTkLabel(
            stats_grid,
            text=f"{self.quiz_logic.difficulty.capitalize()}",
            font=self.get_font(14, "bold"),
            anchor="w"
        )
        difficulty_value.grid(row=1, column=1, sticky="w", padx=(10, 20), pady=5)

        # Questions
        questions_title = ctk.CTkLabel(
            stats_grid,
            text="Questions:",
            font=self.get_font(14),
            anchor="e"
        )
        questions_title.grid(row=2, column=0, sticky="e", padx=(20, 10), pady=5)

        _, total_questions = self.quiz_logic.get_progress()
        questions_value = ctk.CTkLabel(
            stats_grid,
            text=f"{total_questions}",
            font=self.get_font(14, "bold"),
            anchor="w"
        )
        questions_value.grid(row=2, column=1, sticky="w", padx=(10, 20), pady=5)

        # Achievement unlocked (if applicable)
        if self.longest_streak >= 3 or self.quiz_logic.score >= 100:
            achievement_frame = ctk.CTkFrame(stats_frame, fg_color=self.colors["highlight"])
            achievement_frame.pack(pady=15, padx=50, fill=tk.X)

            achievement_label = ctk.CTkLabel(
                achievement_frame,
                text="🏆 New Achievement Unlocked!",
                font=self.get_font(14, "bold"),
                text_color="black"
            )
            achievement_label.pack(pady=5)

        # Check if it's a high score
        is_high_score = self.high_scores.is_high_score(self.quiz_logic.score)

        if is_high_score:
            # High score badge
            high_score_frame = ctk.CTkFrame(
                results_container,
                fg_color=self.colors["highlight"],
                corner_radius=10
            )
            high_score_frame.pack(pady=15)

            high_score_label = ctk.CTkLabel(
                high_score_frame,
                text="🌟 New High Score! 🌟",
                font=self.get_font(20, "bold"),
                text_color="black"
            )
            high_score_label.pack(pady=10, padx=20)

            # Name input with improved styling
            name_frame = ctk.CTkFrame(results_container)
            name_frame.pack(pady=10, fill=tk.X, padx=100)

            name_label = ctk.CTkLabel(
                name_frame,
                text="Enter your name:",
                font=self.get_font(16)
            )
            name_label.pack(pady=(10, 5))

            name_entry = ctk.CTkEntry(
                name_frame,
                width=200,
                placeholder_text="Your name here"
            )
            name_entry.pack(pady=5)
            name_entry.insert(0, "Player")

            # Save score button
            save_button = ctk.CTkButton(
                name_frame,
                text="Save Score",
                font=self.get_font(16),
                fg_color=self.colors["accent"],
                hover_color=self.colors["secondary"],
                command=lambda: self.save_score(name_entry.get())
            )
            save_button.pack(pady=10)

        # Buttons with improved layout
        buttons_frame = ctk.CTkFrame(results_container, fg_color="transparent")
        buttons_frame.pack(pady=20, fill=tk.X)

        # Configure columns for button layout
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)

        play_again_button = ctk.CTkButton(
            buttons_frame,
            text="Play Again",
            font=self.get_font(16),
            width=150,
            fg_color=self.colors["primary"],
            hover_color=self.colors["secondary"],
            command=self.show_welcome_screen
        )
        play_again_button.grid(row=0, column=0, padx=10, pady=10)

        high_scores_button = ctk.CTkButton(
            buttons_frame,
            text="High Scores",
            font=self.get_font(16),
            width=150,
            command=self.show_high_scores_screen
        )
        high_scores_button.grid(row=0, column=1, padx=10, pady=10)

        achievements_button = ctk.CTkButton(
            buttons_frame,
            text="Achievements",
            font=self.get_font(16),
            width=150,
            command=self.show_achievements_screen
        )
        achievements_button.grid(row=0, column=2, padx=10, pady=10)

    def save_score(self, name: str) -> None:
        """
        Save the player's score to high scores.

        Args:
            name: Player's name
        """
        self.high_scores.save_score(name, self.quiz_logic.score)
        self.show_high_scores_screen()

    def show_high_scores_screen(self) -> None:
        """Display the high scores screen with enhanced visual style and responsiveness."""
        self.clear_frame()

        # Refresh high scores
        self.high_scores.load_scores()

        scores_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        scores_container.pack(fill=tk.BOTH, expand=True)

        # Title with trophy icon
        title_frame = ctk.CTkFrame(scores_container, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(20, 10))

        title_label = ctk.CTkLabel(
            title_frame,
            text="🏆 High Scores 🏆",
            font=self.get_font(32, "bold"),
            text_color=self.colors["highlight"]
        )
        title_label.pack(pady=(10, 0))

        # Scores table with card-like design
        scores_card = ctk.CTkFrame(scores_container)
        scores_card.pack(pady=20, fill=tk.BOTH, expand=True, padx=40)

        # Headers with colored background
        header_frame = ctk.CTkFrame(scores_card, fg_color=self.colors["secondary"])
        header_frame.pack(fill=tk.X, pady=(0, 2))

        # Configure columns for responsiveness
        header_frame.columnconfigure(0, weight=1)
        header_frame.columnconfigure(1, weight=3)
        header_frame.columnconfigure(2, weight=1)

        rank_header = ctk.CTkLabel(
            header_frame,
            text="RANK",
            font=self.get_font(16, "bold"),
            text_color="white"
        )
        rank_header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        name_header = ctk.CTkLabel(
            header_frame,
            text="NAME",
            font=self.get_font(16, "bold"),
            text_color="white"
        )
        name_header.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        score_header = ctk.CTkLabel(
            header_frame,
            text="SCORE",
            font=self.get_font(16, "bold"),
            text_color="white"
        )
        score_header.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        # Scores with alternating row colors
        top_scores = self.high_scores.get_top_scores(10)  # Show more scores

        scores_list_frame = ctk.CTkScrollableFrame(scores_card, fg_color="transparent")
        scores_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure columns for responsiveness
        scores_list_frame.columnconfigure(0, weight=1)
        scores_list_frame.columnconfigure(1, weight=3)
        scores_list_frame.columnconfigure(2, weight=1)

        if not top_scores:
            no_scores_label = ctk.CTkLabel(
                scores_list_frame,
                text="No high scores yet!",
                font=self.get_font(16, slant="italic")
            )
            no_scores_label.grid(row=0, column=0, columnspan=3, pady=30)
        else:
            for i, (name, score) in enumerate(top_scores, 1):
                # Use different background for alternating rows and highlight top 3
                if i <= 3:
                    # Gold, Silver, Bronze for top 3
                    bg_colors = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32"}
                    row_color = bg_colors.get(i)
                    text_color = "black"
                else:
                    # Alternating colors for other rows
                    row_color = self.colors["secondary"] if i % 2 == 0 else None
                    text_color = None

                # Create row frame
                score_row = ctk.CTkFrame(scores_list_frame, fg_color=row_color, corner_radius=5)
                score_row.grid(row=i-1, column=0, columnspan=3, sticky="ew", pady=3, padx=5)

                # Configure row columns
                score_row.columnconfigure(0, weight=1)
                score_row.columnconfigure(1, weight=3)
                score_row.columnconfigure(2, weight=1)

                # Medal emoji for top 3
                medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}")

                rank_label = ctk.CTkLabel(
                    score_row,
                    text=medal,
                    font=self.get_font(14, "bold"),
                    text_color=text_color
                )
                rank_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")

                name_label = ctk.CTkLabel(
                    score_row,
                    text=name,
                    font=self.get_font(14),
                    text_color=text_color
                )
                name_label.grid(row=0, column=1, padx=10, pady=8, sticky="w")

                score_label = ctk.CTkLabel(
                    score_row,
                    text=str(score),
                    font=self.get_font(14, "bold"),
                    text_color=text_color
                )
                score_label.grid(row=0, column=2, padx=10, pady=8, sticky="e")

        # Back button
        button_frame = ctk.CTkFrame(scores_container, fg_color="transparent")
        button_frame.pack(pady=20, fill=tk.X)

        back_button = ctk.CTkButton(
            button_frame,
            text="Back to Menu",
            font=self.get_font(16),
            width=150,
            command=self.show_welcome_screen
        )
        back_button.pack()

    def show_achievements_screen(self) -> None:
        """Display the achievements screen with unlocked and locked achievements."""
        self.clear_frame()

        achievements_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        achievements_container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ctk.CTkLabel(
            achievements_container,
            text="🏆 Achievements 🏆",
            font=self.get_font(32, "bold"),
            text_color=self.colors["highlight"]
        )
        title_label.pack(pady=(30, 20))

        # Define all possible achievements
        all_achievements = [
            {
                "id": "perfect_easy",
                "title": "Perfect Easy Quiz",
                "description": "Complete an easy quiz with 100% accuracy",
                "icon": "🎯"
            },
            {
                "id": "perfect_medium",
                "title": "Perfect Medium Quiz",
                "description": "Complete a medium difficulty quiz with 100% accuracy",
                "icon": "🎯"
            },
            {
                "id": "perfect_hard",
                "title": "Perfect Hard Quiz",
                "description": "Complete a hard quiz with 100% accuracy",
                "icon": "🎯"
            },
            {
                "id": "streak_5",
                "title": "Hot Streak",
                "description": "Answer 5 questions correctly in a row",
                "icon": "🔥"
            },
            {
                "id": "streak_10",
                "title": "On Fire!",
                "description": "Answer 10 questions correctly in a row",
                "icon": "🔥"
            },
            {
                "id": "score_100",
                "title": "Century",
                "description": "Earn 100 points in a single quiz",
                "icon": "💯"
            },
            {
                "id": "score_200",
                "title": "Double Century",
                "description": "Earn 200 points in a single quiz",
                "icon": "🌟"
            },
            {
                "id": "all_categories",
                "title": "Jack of All Trades",
                "description": "Complete quizzes in all categories",
                "icon": "🧠"
            }
        ]

        # Create scrollable frame for achievements
        achievements_frame = ctk.CTkScrollableFrame(
            achievements_container,
            fg_color="transparent"
        )
        achievements_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(10, 20))

        # Track row for grid layout
        row = 0

        for achievement in all_achievements:
            # Check if achievement is unlocked
            is_unlocked = self.achievements.get(achievement["id"], False)

            # Create achievement card
            achievement_card = ctk.CTkFrame(
                achievements_frame,
                fg_color=self.colors["secondary"] if is_unlocked else "#555555",
                corner_radius=10
            )
            achievement_card.grid(row=row, column=0, sticky="ew", pady=5, padx=10)
            achievement_card.columnconfigure(1, weight=1)

            # Icon
            icon_label = ctk.CTkLabel(
                achievement_card,
                text=achievement["icon"] if is_unlocked else "🔒",
                font=self.get_font(24)
            )
            icon_label.grid(row=0, column=0, rowspan=2, padx=(15, 10), pady=10)

            # Title
            title_label = ctk.CTkLabel(
                achievement_card,
                text=achievement["title"],
                font=self.get_font(16, "bold"),
                anchor="w"
            )
            title_label.grid(row=0, column=1, sticky="w", padx=5, pady=(10, 0))

            # Description
            description_label = ctk.CTkLabel(
                achievement_card,
                text=achievement["description"],
                font=self.get_font(12),
                anchor="w"
            )
            description_label.grid(row=1, column=1, sticky="w", padx=5, pady=(0, 10))

            # Status indicator
            status_label = ctk.CTkLabel(
                achievement_card,
                text="UNLOCKED" if is_unlocked else "LOCKED",
                font=self.get_font(12, "bold"),
                text_color=self.colors["highlight"] if is_unlocked else None
            )
            status_label.grid(row=0, column=2, rowspan=2, padx=15, pady=10)

            row += 1

        # Back button
        back_button = ctk.CTkButton(
            achievements_container,
            text="Back to Menu",
            font=self.get_font(16),
            width=150,
            command=self.show_welcome_screen
        )
        back_button.pack(pady=20)
