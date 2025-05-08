import json
import random
from typing import List, Dict, Any, Optional, Tuple


class QuizLogic:
    """
    Handles the logic for the quiz game including loading questions,
    tracking scores, and managing game state.
    """
    
    def __init__(self, questions_file: str = "questions.json"):
        """
        Initialize the quiz logic with the path to the questions file.
        
        Args:
            questions_file: Path to the JSON file containing questions
        """
        self.questions_file = questions_file
        self.questions = []
        self.current_questions = []
        self.current_question_index = 0
        self.score = 0
        self.difficulty = "all"
        self.category = "all"
        self.questions_per_game = 10
        self.load_questions()
        
    def load_questions(self) -> None:
        """Load questions from the JSON file."""
        try:
            with open(self.questions_file, 'r') as file:
                data = json.load(file)
                self.questions = data.get("questions", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.questions = []
            print(f"Error loading questions: {e}")
    
    def filter_questions(self) -> List[Dict[str, Any]]:
        """
        Filter questions based on difficulty and category.
        
        Returns:
            List of filtered questions
        """
        filtered = self.questions
        
        if self.difficulty != "all":
            filtered = [q for q in filtered if q.get("difficulty") == self.difficulty]
            
        if self.category != "all":
            filtered = [q for q in filtered if q.get("category") == self.category]
            
        return filtered
    
    def start_new_game(self) -> bool:
        """
        Start a new game by selecting and shuffling questions.
        
        Returns:
            True if game started successfully, False otherwise
        """
        filtered_questions = self.filter_questions()
        
        if not filtered_questions:
            return False
            
        # Shuffle and select questions for this game
        random.shuffle(filtered_questions)
        self.current_questions = filtered_questions[:min(self.questions_per_game, len(filtered_questions))]
        self.current_question_index = 0
        self.score = 0
        return True
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """
        Get the current question.
        
        Returns:
            Current question dictionary or None if no questions available
        """
        if 0 <= self.current_question_index < len(self.current_questions):
            return self.current_questions[self.current_question_index]
        return None
    
    def get_shuffled_options(self) -> List[str]:
        """
        Get shuffled options for the current question.
        
        Returns:
            List of shuffled options
        """
        question = self.get_current_question()
        if not question:
            return []
            
        options = question.get("options", []).copy()
        random.shuffle(options)
        return options
    
    def check_answer(self, selected_option: str) -> bool:
        """
        Check if the selected option is correct.
        
        Args:
            selected_option: The option selected by the user
            
        Returns:
            True if the answer is correct, False otherwise
        """
        question = self.get_current_question()
        if not question:
            return False
            
        is_correct = selected_option == question.get("correct_answer")
        
        if is_correct:
            # Award points based on difficulty
            difficulty = question.get("difficulty", "easy")
            points = {"easy": 10, "medium": 15, "hard": 20}.get(difficulty, 10)
            self.score += points
            
        return is_correct
    
    def next_question(self) -> bool:
        """
        Move to the next question.
        
        Returns:
            True if there is a next question, False otherwise
        """
        self.current_question_index += 1
        return self.current_question_index < len(self.current_questions)
    
    def get_progress(self) -> Tuple[int, int]:
        """
        Get the current progress in the quiz.
        
        Returns:
            Tuple of (current question number, total questions)
        """
        return self.current_question_index + 1, len(self.current_questions)
    
    def get_available_categories(self) -> List[str]:
        """
        Get a list of all available categories.
        
        Returns:
            List of unique categories
        """
        categories = set(q.get("category", "Uncategorized") for q in self.questions)
        return sorted(list(categories))
    
    def get_available_difficulties(self) -> List[str]:
        """
        Get a list of all available difficulties.
        
        Returns:
            List of unique difficulties
        """
        difficulties = set(q.get("difficulty", "easy") for q in self.questions)
        return sorted(list(difficulties))
