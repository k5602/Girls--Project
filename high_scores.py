from typing import List, Tuple, Dict, Any, Optional
import os
import json
from datetime import datetime


class HighScores:
    """
    Manages high scores for the quiz game, including saving and loading scores.
    
    This class handles:
    - Saving and loading high scores from file
    - Determining if a score qualifies as a high score
    - Maintaining player statistics and game history
    - Generating leaderboards for different categories and difficulties
    """
    
    def __init__(self, file_path: str = "high_scores.txt", stats_file: str = "player_stats.json"):
        """
        Initialize the high scores manager with the path to the scores file.
        
        Args:
            file_path: Path to the text file containing high scores
            stats_file: Path to the JSON file containing player statistics
        """
        self.file_path = file_path
        self.stats_file = stats_file
        self.scores = []
        self.player_stats = {}
        self.load_scores()
        self.load_stats()
    
    def load_scores(self) -> None:
        """
        Load high scores from the file.
        
        Handles file not found errors gracefully and maintains
        a sorted list of scores in descending order.
        
        Returns:
            None
        """
        self.scores = []
        
        if not os.path.exists(self.file_path):
            return
            
        try:
            with open(self.file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and ',' in line:
                        parts = line.split(',')
                        if len(parts) >= 4:  # Extended format with metadata
                            name, score_str, date_str, category = parts[:4]
                            difficulty = parts[4] if len(parts) > 4 else "all"
                        else:  # Legacy format
                            name, score_str = parts[:2]
                            date_str = "Unknown"
                            category = "all"
                            difficulty = "all"
                            
                        try:
                            score = int(score_str)
                            entry = (name, score, date_str, category, difficulty)
                            self.scores.append(entry)
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Error loading high scores: {e}")
            
        # Sort scores by score value (descending)
        self.scores.sort(key=lambda x: x[1], reverse=True)
    
    def save_score(self, name: str, score: int, stats: Dict[str, Any] = None) -> None:
        """
        Save a new score to the high scores file with metadata.
        
        Args:
            name: Player's name
            score: Player's score
            stats: Dictionary containing additional statistics about the game
            
        Returns:
            None
        """
        if not name:
            name = "Anonymous"
            
        # Get additional metadata from stats if provided
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        category = "all"
        difficulty = "all"
        
        if stats:
            category = stats.get("category", "all")
            difficulty = stats.get("difficulty", "all")
            
        # Add to scores list
        entry = (name, score, date_str, category, difficulty)
        self.scores.append(entry)
        self.scores.sort(key=lambda x: x[1], reverse=True)
        
        try:
            with open(self.file_path, 'w') as file:
                for entry in self.scores:
                    # Save extended format with metadata
                    file.write(f"{entry[0]},{entry[1]},{entry[2]},{entry[3]},{entry[4]}\n")
        except Exception as e:
            print(f"Error saving high scores: {e}")
            
        # Update player statistics
        self.update_player_stats(name, score, stats)
    
    def get_top_scores(self, limit: int = 5, category: str = "all", 
               difficulty: str = "all") -> List[Tuple]:
        """
        Get the top scores, optionally filtered by category and difficulty.
        
        Args:
            limit: Number of top scores to return
            category: Category to filter by, or "all" for unfiltered
            difficulty: Difficulty to filter by, or "all" for unfiltered
            
        Returns:
            List of (name, score, date, category, difficulty) tuples for the top scores
        """
        filtered_scores = self.scores
        
        # Filter by category if specified
        if category != "all":
            filtered_scores = [s for s in filtered_scores if s[3] == category]
            
        # Filter by difficulty if specified
        if difficulty != "all":
            filtered_scores = [s for s in filtered_scores if s[4] == difficulty]
            
        # Return sorted, limited list
        return sorted(filtered_scores, key=lambda x: x[1], reverse=True)[:limit]
    
    def is_high_score(self, score: int, category: str = "all", 
                     difficulty: str = "all") -> bool:
        """
        Check if a score qualifies as a high score, optionally for a specific
        category and difficulty.
        
        Args:
            score: Score to check
            category: Category to check against, or "all"
            difficulty: Difficulty to check against, or "all"
            
        Returns:
            True if the score is a high score, False otherwise
        """
        top_scores = self.get_top_scores(5, category, difficulty)
        
        if len(top_scores) < 5:
            return True
            
        # Extract the score value (index 1) from each tuple
        return score > min(entry[1] for entry in top_scores)
        
    def load_stats(self) -> None:
        """
        Load player statistics from JSON file.
        
        Returns:
            None
        """
        if not os.path.exists(self.stats_file):
            self.player_stats = {}
            return
            
        try:
            with open(self.stats_file, 'r') as file:
                self.player_stats = json.load(file)
        except Exception as e:
            print(f"Error loading player stats: {e}")
            self.player_stats = {}
            
    def update_player_stats(self, name: str, score: int, game_stats: Optional[Dict[str, Any]] = None) -> None:
        """
        Update statistics for a player based on their latest game.
        
        Args:
            name: Player's name
            score: Score achieved in the game
            game_stats: Dictionary of statistics from the game
            
        Returns:
            None
        """
        if name not in self.player_stats:
            self.player_stats[name] = {
                "total_score": 0,
                "games_played": 0,
                "highest_score": 0,
                "average_score": 0,
                "questions_answered": 0,
                "correct_answers": 0,
                "last_played": "",
                "achievements": [],
                "categories_played": [],
                "difficulties_completed": []
            }
            
        player = self.player_stats[name]
        player["total_score"] += score
        player["games_played"] += 1
        player["highest_score"] = max(player["highest_score"], score)
        player["last_played"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Update with game statistics if provided
        if game_stats:
            player["questions_answered"] += game_stats.get("total_questions", 0)
            player["correct_answers"] += game_stats.get("answered_correctly", 0)
            
            # Update categories played
            category = game_stats.get("category", "")
            if category and category != "all" and category not in player["categories_played"]:
                player["categories_played"].append(category)
                
            # Update completed difficulties
            difficulty = game_stats.get("difficulty", "")
            if difficulty and difficulty != "all" and difficulty not in player["difficulties_completed"]:
                player["difficulties_completed"].append(difficulty)
                
        # Recalculate average score
        if player["games_played"] > 0:
            player["average_score"] = player["total_score"] / player["games_played"]
            
        # Save updated stats
        self.save_stats()
        
    def save_stats(self) -> None:
        """
        Save player statistics to JSON file.
        
        Returns:
            None
        """
        try:
            with open(self.stats_file, 'w') as file:
                json.dump(self.player_stats, file, indent=2)
        except Exception as e:
            print(f"Error saving player stats: {e}")
            
    def get_player_stats(self, name: str) -> Dict[str, Any]:
        """
        Get statistics for a specific player.
        
        Args:
            name: Player's name
            
        Returns:
            Dictionary of player statistics, or empty dict if player not found
        """
        return self.player_stats.get(name, {})
        
    def get_leaderboard(self, metric: str = "highest_score", limit: int = 10) -> List[Tuple[str, Any]]:
        """
        Get a leaderboard based on a specific metric.
        
        Args:
            metric: Statistic to rank by (highest_score, average_score, games_played)
            limit: Number of entries to return
            
        Returns:
            List of (name, value) tuples sorted by the metric
        """
        if not self.player_stats:
            return []
            
        leaderboard = []
        for name, stats in self.player_stats.items():
            if metric in stats:
                leaderboard.append((name, stats[metric]))
                
        # Sort by the selected metric (descending)
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        return leaderboard[:limit]
