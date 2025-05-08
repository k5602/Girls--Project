from typing import List, Tuple, Dict
import os


class HighScores:
    """
    Manages high scores for the quiz game, including saving and loading scores.
    """
    
    def __init__(self, file_path: str = "high_scores.txt"):
        """
        Initialize the high scores manager with the path to the scores file.
        
        Args:
            file_path: Path to the text file containing high scores
        """
        self.file_path = file_path
        self.scores = []
        self.load_scores()
    
    def load_scores(self) -> None:
        """Load high scores from the file."""
        self.scores = []
        
        if not os.path.exists(self.file_path):
            return
            
        try:
            with open(self.file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and ',' in line:
                        name, score_str = line.split(',', 1)
                        try:
                            score = int(score_str)
                            self.scores.append((name, score))
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Error loading high scores: {e}")
    
    def save_score(self, name: str, score: int) -> None:
        """
        Save a new score to the high scores file.
        
        Args:
            name: Player's name
            score: Player's score
        """
        if not name:
            name = "Anonymous"
            
        self.scores.append((name, score))
        self.scores.sort(key=lambda x: x[1], reverse=True)
        
        try:
            with open(self.file_path, 'w') as file:
                for name, score in self.scores:
                    file.write(f"{name},{score}\n")
        except Exception as e:
            print(f"Error saving high scores: {e}")
    
    def get_top_scores(self, limit: int = 5) -> List[Tuple[str, int]]:
        """
        Get the top scores.
        
        Args:
            limit: Number of top scores to return
            
        Returns:
            List of (name, score) tuples for the top scores
        """
        return sorted(self.scores, key=lambda x: x[1], reverse=True)[:limit]
    
    def is_high_score(self, score: int) -> bool:
        """
        Check if a score qualifies as a high score.
        
        Args:
            score: Score to check
            
        Returns:
            True if the score is a high score, False otherwise
        """
        if len(self.scores) < 5:
            return True
            
        return score > min(s[1] for s in self.get_top_scores())
