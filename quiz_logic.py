import json
import random
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set


class QuizLogic:
    """
    Handles the logic for the quiz game including loading questions,
    tracking scores, and managing game state.

    This class is responsible for:
    - Loading and filtering questions from the JSON database
    - Managing game state including current question, score, and progress
    - Checking answers and calculating scores
    - Tracking statistics including streak, accuracy, and timing
    """

    def __init__(self, questions_file: str = "questions.json"):
        """
        Initialize the quiz logic with the path to the questions file.

        Args:
            questions_file: Path to the JSON file containing questions
        """
        self.questions_file = questions_file
        self.questions: List[Dict[str, Any]] = []
        self.current_questions: List[Dict[str, Any]] = []
        self._remaining_questions: List[Dict[str, Any]] = []  # For pagination
        self.current_question_index = 0
        self.score = 0
        self.difficulty = "all"
        self.category = "all"
        self.questions_per_game = 10
        self.answered_correctly = 0
        self.answered_incorrectly = 0
        self.skipped_questions = 0
        self.used_hints = 0
        self.question_times: List[float] = []
        self.played_categories: Set[str] = set()
        self.completed_difficulties: Set[str] = set()
        self.load_questions()

    def load_questions(self) -> None:
        """
        Load questions from the JSON file.

        Handles file not found and JSON decode errors gracefully.

        Returns:
            None
        """
        try:
            with open(self.questions_file, 'r') as file:
                data = json.load(file)
                self.questions = data.get("questions", [])

            # Add unique IDs to questions if they don't have them
            for i, q in enumerate(self.questions):
                if "id" not in q:
                    q["id"] = f"q{i}"

                # Add hints if they don't exist
                if "hint" not in q:
                    # Generate a basic hint based on the correct answer
                    answer = q.get("correct_answer", "")
                    if len(answer) > 3:
                        q["hint"] = f"The answer starts with '{answer[0]}' and contains {len(answer)} letters."
                    else:
                        q["hint"] = "No hint available for this question."

        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.questions = []
            print(f"Error loading questions: {e}")

    def filter_questions(self) -> List[Dict[str, Any]]:
        """
        Filter questions based on difficulty and category.

        Uses the currently set difficulty and category properties
        to filter the question bank. Also removes duplicates based
        on question text to ensure variety.

        Returns:
            List of filtered questions matching the criteria
        """
        # Create a filtered iterator for better performance with large datasets
        filtered_iter = iter(self.questions)

        # Apply filters efficiently
        if self.difficulty != "all":
            filtered_iter = (q for q in filtered_iter if q.get("difficulty", "easy") == self.difficulty)

        if self.category != "all":
            filtered_iter = (q for q in filtered_iter if q.get("category", "") == self.category)

        # Ensure no duplicate questions by checking question text
        seen_questions: Set[str] = set()
        unique_filtered: List[Dict[str, Any]] = []

        # Process the iterator
        for q in filtered_iter:
            q_text = q.get("question", "")
            if q_text not in seen_questions:
                seen_questions.add(q_text)
                unique_filtered.append(q)

        return unique_filtered

    def start_new_game(self) -> bool:
        """
        Start a new game by selecting and shuffling questions.

        Resets game state and prepares a new set of questions based
        on the current difficulty and category settings. Also resets
        statistics for the new game.

        Returns:
            True if game started successfully, False otherwise
        """
        filtered_questions = self.filter_questions()

        if not filtered_questions:
            return False

        # Shuffle and select questions for this game
        random.shuffle(filtered_questions)

        # Implement pagination - only load a subset of questions initially
        # to improve performance with large question sets
        max_questions = min(self.questions_per_game, len(filtered_questions))
        self.current_questions = filtered_questions[:max_questions]
        self.current_question_index = 0
        self.score = 0

        # Store remaining questions for potential pagination
        self._remaining_questions = filtered_questions[max_questions:]

        # Reset game statistics
        self.answered_correctly = 0
        self.answered_incorrectly = 0
        self.skipped_questions = 0
        self.used_hints = 0
        self.question_times = []

        # Record game start time
        self.game_start_time = time.time()

        # Add current category to played categories if it's not "all"
        if self.category != "all":
            self.played_categories.add(self.category)

        return True

    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """
        Get the current question.

        Retrieves the question at the current index position. Also
        records the timestamp when the question is first accessed
        to allow for timing analytics.

        Returns:
            Current question dictionary or None if no questions available
        """
        if 0 <= self.current_question_index < len(self.current_questions):
            question = self.current_questions[self.current_question_index]

            # Record timestamp when the question is first accessed
            if "start_time" not in question:
                question["start_time"] = time.time()

            return question
        return None

    def get_shuffled_options(self) -> List[str]:
        """
        Get shuffled options for the current question.

        Creates a copy of the options array and shuffles it to ensure
        the correct answer appears in different positions each time.
        If the question has fewer than 4 options, it will add dummy
        options to ensure a consistent interface.

        Returns:
            List of shuffled options
        """
        question = self.get_current_question()
        if not question:
            return []

        options = question.get("options", []).copy()

        # Ensure we always have at least 4 options for UI consistency
        correct_answer = question.get("correct_answer", "")
        if len(options) < 4:
            # Add the correct answer if it's not in options
            if correct_answer and correct_answer not in options:
                options.append(correct_answer)

            # Add dummy options if still needed
            dummy_options = ["Option A", "Option B", "Option C", "Option D"]
            for opt in dummy_options:
                if len(options) >= 4:
                    break
                if opt not in options:
                    options.append(opt)

        random.shuffle(options)
        return options

    def check_answer(self, selected_option: str) -> bool:
        """
        Check if the selected option is correct and award points.

        Awards points based on difficulty level and calculates time bonus
        if the answer is correct. Updates statistics for correct/incorrect
        answers.

        Args:
            selected_option: The option selected by the user

        Returns:
            True if the answer is correct, False otherwise
        """
        question = self.get_current_question()
        if not question:
            return False

        # Record the answer time
        question["answer_time"] = time.time()
        time_taken = question["answer_time"] - question.get("start_time", question["answer_time"])
        self.question_times.append(time_taken)

        is_correct = selected_option == question.get("correct_answer")

        if is_correct:
            self.answered_correctly += 1

            # Award points based on difficulty
            difficulty = question.get("difficulty", "easy")
            points = {"easy": 10, "medium": 15, "hard": 20}.get(difficulty, 10)

            # Add time bonus for quick answers (max 5 points)
            time_bonus = 0
            if time_taken < 5:
                time_bonus = 5
            elif time_taken < 10:
                time_bonus = 3
            elif time_taken < 15:
                time_bonus = 1

            self.score += points + time_bonus

            # Store the points awarded for this question
            question["points_awarded"] = points + time_bonus
        else:
            self.answered_incorrectly += 1
            question["points_awarded"] = 0

        return is_correct

    def next_question(self) -> bool:
        """
        Move to the next question.

        Increments the current question index and checks if there
        are more questions available. Implements pagination by loading
        more questions if needed and available.

        Returns:
            True if there is a next question, False otherwise
        """
        self.current_question_index += 1
        
        # Calculate total questions answered so far
        total_answered = self.answered_correctly + self.answered_incorrectly + self.skipped_questions
        
        # Check if we've reached the user-defined questions limit
        if total_answered >= self.questions_per_game:
            # If we've reached the user-defined limit, don't add more questions
            return False

        # Check if we've reached the end of the current batch
        if self.current_question_index >= len(self.current_questions):
            # If we have more questions available, load the next batch
            if self._remaining_questions:
                # Calculate how many more questions we can add without exceeding the limit
                questions_remaining = self.questions_per_game - total_answered
                if questions_remaining <= 0:
                    return False
                    
                # Load up to 5 more questions (pagination), but not exceeding user limit
                batch_size = min(5, len(self._remaining_questions), questions_remaining)
                next_batch = self._remaining_questions[:batch_size]
                self._remaining_questions = self._remaining_questions[batch_size:]

                # Add to current questions
                self.current_questions.extend(next_batch)
            # If we've reached the end and the difficulty isn't "all", mark it as completed
            elif self.difficulty != "all":
                self.completed_difficulties.add(self.difficulty)

        return self.current_question_index < len(self.current_questions)

    def get_progress(self) -> Tuple[int, int]:
        """
        Get the current progress in the quiz.

        Returns:
            Tuple of (current question number, total questions)
        """
        return self.current_question_index + 1, len(self.current_questions)

    def skip_question(self) -> None:
        """
        Skip the current question without answering.

        Increments skipped question counter and moves to the next question.
        No points are awarded for skipped questions.

        Returns:
            None
        """
        self.skipped_questions += 1

    def use_hint(self) -> str:
        """
        Use a hint for the current question.

        Increments the used hints counter and returns the hint text.

        Returns:
            Hint text for the current question
        """
        self.used_hints += 1

        question = self.get_current_question()
        if question:
            return question.get("hint", "No hint available for this question.")
        return "No question available."

    def get_available_categories(self) -> List[str]:
        """
        Get a list of all available categories.

        Extracts unique categories from the question bank and sorts them.

        Returns:
            List of unique categories
        """
        categories = set(q.get("category", "Uncategorized") for q in self.questions)
        return sorted(list(categories))

    def get_available_difficulties(self) -> List[str]:
        """
        Get a list of all available difficulties.

        Extracts unique difficulty levels from the question bank and sorts them.

        Returns:
            List of unique difficulties
        """
        difficulties = set(q.get("difficulty", "easy") for q in self.questions)
        return sorted(list(difficulties))

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the current quiz session.

        Calculates accuracy, average time per question, and other metrics.

        Returns:
            Dictionary containing quiz statistics
        """
        total_answered = self.answered_correctly + self.answered_incorrectly
        accuracy = (self.answered_correctly / total_answered * 100) if total_answered > 0 else 0
        avg_time = sum(self.question_times) / len(self.question_times) if self.question_times else 0

        return {
            "score": self.score,
            "answered_correctly": self.answered_correctly,
            "answered_incorrectly": self.answered_incorrectly,
            "skipped_questions": self.skipped_questions,
            "accuracy": accuracy,
            "average_time": avg_time,
            "used_hints": self.used_hints,
            "difficulty": self.difficulty,
            "category": self.category,
            "total_questions": len(self.current_questions),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "categories_played": list(self.played_categories),
            "difficulties_completed": list(self.completed_difficulties)
        }

    def save_questions(self, new_question: Dict[str, Any]) -> bool:
        """
        Add a new question to the question bank and save it to file.

        Args:
            new_question: Dictionary containing the new question data

        Returns:
            True if question was saved successfully, False otherwise
        """
        # Validate the question format
        required_fields = ["question", "options", "correct_answer", "difficulty", "category"]
        if not all(field in new_question for field in required_fields):
            return False

        # Add the question to the bank
        self.questions.append(new_question)

        try:
            # Save the updated question bank
            with open(self.questions_file, 'w') as file:
                json.dump({"questions": self.questions}, file, indent=2)
            return True
        except Exception as e:
            print(f"Error saving question: {e}")
            return False
