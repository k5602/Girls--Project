import unittest
import os
import json
from quiz_logic import QuizLogic
from high_scores import HighScores
import tkinter as tk
import customtkinter as ctk
from gui import QuizApp


class TestQuizLogic(unittest.TestCase):
    """Test cases for the QuizLogic class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary test questions file
        self.test_questions_file = "test_questions.json"
        self.test_questions = {
            "questions": [
                {
                    "question": "What is 2+2?",
                    "options": ["3", "4", "5", "6"],
                    "correct_answer": "4",
                    "difficulty": "easy",
                    "category": "Math"
                },
                {
                    "question": "What is the capital of France?",
                    "options": ["London", "Berlin", "Paris", "Madrid"],
                    "correct_answer": "Paris",
                    "difficulty": "easy",
                    "category": "Geography"
                },
                {
                    "question": "Which is the largest planet?",
                    "options": ["Earth", "Jupiter", "Mars", "Venus"],
                    "correct_answer": "Jupiter",
                    "difficulty": "medium",
                    "category": "Science"
                },
                {
                    "question": "Who wrote 'Hamlet'?",
                    "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
                    "correct_answer": "William Shakespeare",
                    "difficulty": "medium",
                    "category": "Literature"
                },
                {
                    "question": "What is the square root of 144?",
                    "options": ["10", "11", "12", "14"],
                    "correct_answer": "12",
                    "difficulty": "hard",
                    "category": "Math"
                }
            ]
        }
        
        # Write test questions to file
        with open(self.test_questions_file, "w") as f:
            json.dump(self.test_questions, f)
            
        # Create quiz logic instance
        self.quiz_logic = QuizLogic(self.test_questions_file)

    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.test_questions_file):
            os.remove(self.test_questions_file)

    def test_load_questions(self):
        """Test loading questions from file."""
        self.assertEqual(len(self.quiz_logic.questions), 5)
        self.assertEqual(self.quiz_logic.questions[0]["question"], "What is 2+2?")

    def test_filter_questions_by_difficulty(self):
        """Test filtering questions by difficulty."""
        self.quiz_logic.difficulty = "easy"
        filtered = self.quiz_logic.filter_questions()
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["difficulty"], "easy")
        self.assertEqual(filtered[1]["difficulty"], "easy")

    def test_filter_questions_by_category(self):
        """Test filtering questions by category."""
        self.quiz_logic.category = "Math"
        filtered = self.quiz_logic.filter_questions()
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["category"], "Math")
        self.assertEqual(filtered[1]["category"], "Math")

    def test_start_new_game(self):
        """Test starting a new game."""
        result = self.quiz_logic.start_new_game()
        self.assertTrue(result)
        self.assertEqual(len(self.quiz_logic.current_questions), 5)  # All questions
        self.assertEqual(self.quiz_logic.current_question_index, 0)
        self.assertEqual(self.quiz_logic.score, 0)

    def test_get_current_question(self):
        """Test getting the current question."""
        self.quiz_logic.start_new_game()
        question = self.quiz_logic.get_current_question()
        self.assertIsNotNone(question)
        self.assertIn("question", question)
        self.assertIn("options", question)
        self.assertIn("correct_answer", question)

    def test_check_answer_correct(self):
        """Test checking a correct answer."""
        self.quiz_logic.start_new_game()
        question = self.quiz_logic.get_current_question()
        correct = self.quiz_logic.check_answer(question["correct_answer"])
        self.assertTrue(correct)
        
        # Score should be increased based on difficulty
        difficulty = question["difficulty"]
        expected_points = {"easy": 10, "medium": 15, "hard": 20}.get(difficulty, 10)
        self.assertGreaterEqual(self.quiz_logic.score, expected_points)

    def test_check_answer_incorrect(self):
        """Test checking an incorrect answer."""
        self.quiz_logic.start_new_game()
        question = self.quiz_logic.get_current_question()
        incorrect_answer = next(opt for opt in question["options"] 
                               if opt != question["correct_answer"])
        correct = self.quiz_logic.check_answer(incorrect_answer)
        self.assertFalse(correct)
        self.assertEqual(self.quiz_logic.score, 0)  # Score should remain 0

    def test_next_question(self):
        """Test moving to the next question."""
        self.quiz_logic.start_new_game()
        first_question = self.quiz_logic.get_current_question()
        
        has_next = self.quiz_logic.next_question()
        self.assertTrue(has_next)
        
        second_question = self.quiz_logic.get_current_question()
        self.assertNotEqual(first_question, second_question)

    def test_get_progress(self):
        """Test getting progress information."""
        self.quiz_logic.start_new_game()
        progress = self.quiz_logic.get_progress()
        self.assertEqual(progress, (1, len(self.quiz_logic.current_questions)))
        
        self.quiz_logic.next_question()
        progress = self.quiz_logic.get_progress()
        self.assertEqual(progress, (2, len(self.quiz_logic.current_questions)))

    def test_get_available_categories(self):
        """Test getting available categories."""
        categories = self.quiz_logic.get_available_categories()
        expected_categories = ["Math", "Geography", "Science", "Literature"]
        self.assertListEqual(sorted(categories), sorted(expected_categories))

    def test_get_available_difficulties(self):
        """Test getting available difficulties."""
        difficulties = self.quiz_logic.get_available_difficulties()
        expected_difficulties = ["easy", "medium", "hard"]
        self.assertListEqual(sorted(difficulties), sorted(expected_difficulties))

    def test_get_statistics(self):
        """Test getting quiz statistics."""
        self.quiz_logic.start_new_game()
        
        # Answer a few questions
        question = self.quiz_logic.get_current_question()
        self.quiz_logic.check_answer(question["correct_answer"])
        self.quiz_logic.next_question()
        
        question = self.quiz_logic.get_current_question()
        incorrect_answer = next(opt for opt in question["options"] 
                               if opt != question["correct_answer"])
        self.quiz_logic.check_answer(incorrect_answer)
        
        stats = self.quiz_logic.get_statistics()
        self.assertEqual(stats["answered_correctly"], 1)
        self.assertEqual(stats["answered_incorrectly"], 1)
        self.assertEqual(stats["accuracy"], 50.0)


class TestHighScores(unittest.TestCase):
    """Test cases for the HighScores class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_scores_file = "test_scores.txt"
        self.test_stats_file = "test_stats.json"
        
        # Create a fresh HighScores instance
        self.high_scores = HighScores(self.test_scores_file, self.test_stats_file)
        
    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.test_scores_file):
            os.remove(self.test_scores_file)
        if os.path.exists(self.test_stats_file):
            os.remove(self.test_stats_file)

    def test_save_and_get_scores(self):
        """Test saving and retrieving scores."""
        # Save some test scores
        self.high_scores.save_score("Player1", 100)
        self.high_scores.save_score("Player2", 200)
        self.high_scores.save_score("Player3", 150)
        
        # Get top scores and verify
        top_scores = self.high_scores.get_top_scores()
        self.assertEqual(len(top_scores), 3)
        
        # Scores should be sorted in descending order
        self.assertEqual(top_scores[0][0], "Player2")
        self.assertEqual(top_scores[0][1], 200)
        self.assertEqual(top_scores[1][0], "Player3")
        self.assertEqual(top_scores[1][1], 150)
        self.assertEqual(top_scores[2][0], "Player1")
        self.assertEqual(top_scores[2][1], 100)

    def test_is_high_score(self):
        """Test determining if a score qualifies as high score."""
        # With no existing scores, any score should be high score
        self.assertTrue(self.high_scores.is_high_score(50))
        
        # Add 5 scores
        for i in range(5):
            self.high_scores.save_score(f"Player{i}", (i+1)*100)
        
        # Test boundary cases
        self.assertFalse(self.high_scores.is_high_score(50))  # Below lowest (100)
        self.assertFalse(self.high_scores.is_high_score(100))  # Equal to lowest
        self.assertTrue(self.high_scores.is_high_score(101))   # Just above lowest
        self.assertTrue(self.high_scores.is_high_score(600))   # Above highest

    def test_player_stats(self):
        """Test updating and retrieving player statistics."""
        # Save a score with stats
        stats = {
            "category": "Science",
            "difficulty": "medium",
            "total_questions": 10,
            "answered_correctly": 8
        }
        
        self.high_scores.save_score("TestPlayer", 150, stats)
        
        # Check if player stats were updated
        player_stats = self.high_scores.get_player_stats("TestPlayer")
        self.assertEqual(player_stats["highest_score"], 150)
        self.assertEqual(player_stats["games_played"], 1)
        self.assertEqual(player_stats["questions_answered"], 10)
        self.assertEqual(player_stats["correct_answers"], 8)


class TestGUI(unittest.TestCase):
    """Basic test cases for GUI functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the root window for GUI tests."""
        cls.root = tk.Tk()
        cls.root.withdraw()  # Hide the window
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after GUI tests."""
        cls.root.destroy()
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock files for testing
        self.test_questions_file = "test_questions.json"
        self.test_scores_file = "test_scores.txt"
        
        # Create simple test questions
        test_questions = {
            "questions": [
                {
                    "question": "Test Question?",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "difficulty": "easy",
                    "category": "Test"
                }
            ]
        }
        
        # Write test questions to file
        with open(self.test_questions_file, "w") as f:
            json.dump(test_questions, f)
    
    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.test_questions_file):
            os.remove(self.test_questions_file)
        if os.path.exists(self.test_scores_file):
            os.remove(self.test_scores_file)
    
    def test_gui_initialization(self):
        """Test basic GUI initialization."""
        try:
            app = QuizApp(TestGUI.root)
            self.assertIsNotNone(app)
            self.assertIsNotNone(app.quiz_logic)
            self.assertIsNotNone(app.high_scores)
        except Exception as e:
            self.fail(f"GUI initialization failed: {e}")


if __name__ == "__main__":
    unittest.main()