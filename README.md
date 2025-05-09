# Quiz Master

A feature-rich Python-based Quiz Game with a modern, responsive GUI built using CustomTkinter. This application allows users to test their knowledge with multiple-choice questions across various categories and difficulty levels, with gamification elements to enhance engagement.

## Features

- **Modern, Responsive UI**: Sleek interface that adapts to different screen sizes and devices
- **Multiple Choice Questions**: Answer questions with four options each, clearly displayed in a grid layout
- **Customizable Timer**: Select timer duration (10, 15, 20, or 30 seconds) to match your preferred pace
- **Advanced Scoring System**: Points awarded based on difficulty (Easy: 10, Medium: 15, Hard: 20) plus time bonuses for quick answers
- **Streak Bonuses**: Earn extra points for consecutive correct answers
- **High Scores & Leaderboards**: Track top performers with detailed statistics
- **Difficulty Levels**: Choose between Easy, Medium, and Hard questions
- **Categories**: Filter questions by subject categories
- **Progress Tracking**: Visual progress bar shows quiz completion status
- **Enhanced Visual Feedback**: Animated, color-coded feedback for correct/incorrect answers
- **Randomized Questions**: Questions and options are shuffled for each game
- **Achievements System**: Unlock achievements based on performance milestones
- **Hint System**: Use hints to eliminate wrong answers (at a point cost)
- **Theme Selection**: Choose between Light, Dark, or System themes
- **Customizable Quiz Length**: Select the number of questions per quiz (5, 10, 15, or 20)
- **Skip Question Option**: Ability to skip difficult questions
- **Detailed Statistics**: View performance metrics including accuracy and average time

## Project Structure

```
QuizMaster/
├── main.py           # Entry point with splash screen
├── quiz_logic.py     # Handles question loading, scoring, and game logic
├── gui.py            # Contains all CustomTkinter GUI code with responsive design
├── high_scores.py    # Manages saving/loading high scores and player statistics
├── questions.json    # Stores the question bank
├── high_scores.txt   # Stores high scores with metadata
├── player_stats.json # Stores detailed player statistics (created on first run)
└── README.md         # Documentation
```

## Requirements

- Python 3.6 or higher
- Libraries:
  - CustomTkinter
  - Pillow (PIL)
  - tkinter

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install customtkinter pillow
```

3. Run the application:

```bash
python main.py
```

## How to Play

1. **Start Screen**: 
   - Choose a difficulty level, category, and number of questions
   - Select timer duration and theme preference
   - Click "Start Quiz" to begin

2. **Question Screen**: 
   - Read the question and select one of the four options
   - Submit your answer before the timer expires
   - Use hints to eliminate wrong answers if needed (costs 5 points)
   - Skip difficult questions if necessary
   - Build up a streak of correct answers for bonus points
   - Correct answers are highlighted in green, incorrect in red

3. **Results Screen**: 
   - View your final score and performance statistics
   - See your longest streak and other achievements
   - If you achieved a high score, enter your name to save it
   - Choose to play again, view high scores, or check achievements

4. **High Scores Screen**: 
   - View the top 10 high scores with metadata
   - Gold, silver, and bronze highlights for top 3 scores
   - Filter scores by category or difficulty

5. **Achievements Screen**:
   - Track your progress toward completing various achievements
   - Unlock new achievements through gameplay milestones

## Enhanced Features

1. **Responsive Design**: 
   - Interface adapts to different window sizes and screen resolutions
   - Gracefully handles window resizing
   - Appropriate scaling of UI elements for usability

2. **Gamification Elements**:
   - Achievement system with unlockable badges
   - Streak tracking with visual indicators and bonus points
   - Performance statistics to track improvement

3. **Advanced Scoring System**:
   - Base points based on difficulty (Easy: 10, Medium: 15, Hard: 20)
   - Time bonuses for quick answers (up to 5 extra points)
   - Streak bonuses for consecutive correct answers
   - Penalties for using hints

4. **User Experience Improvements**:
   - Customizable quiz options (length, timer, category, difficulty)
   - Theme selection (Light, Dark, System)
   - Visual cues when timer is running low
   - Animated feedback
   - Question metadata display (category, difficulty, point value)

## Customization

- **Adding Questions**: Add more questions to the `questions.json` file following the existing format, including optional hints
- **Creating Themes**: Define custom color schemes in the `colors` dictionary in `gui.py`
- **Timer Duration**: Easily adjustable from the user interface
- **Adding Achievements**: Extend the achievements system by adding new entries to the `all_achievements` list

## Developer Documentation

Each function and class in the codebase is documented with clear, informative docstrings that explain:
- Purpose and functionality
- Parameters and return values
- Side effects and exceptions
- Usage examples where appropriate

The code follows best practices for:
- Proper error handling
- Responsive UI design
- Object-oriented programming principles
- Clean, readable code structure

## Future Enhancements

Possible future enhancements include:
- Online multiplayer mode
- More question types (true/false, fill-in-the-blank, etc.)
- Integration with external question databases
- User profile system with avatars
- Social media sharing of results
- Daily challenges and quests

## License

This project is open-source and available for educational purposes.

## Acknowledgements

- CustomTkinter for providing a modern UI toolkit
- All contributors to the project
- The open-source community for inspiration and resources

## Dedication

This project is dedicated to the rose of my life, my beautiful light Sara.
