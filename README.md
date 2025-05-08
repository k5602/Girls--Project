# Quiz Game

A Python-based Quiz Game with a modern GUI built using CustomTkinter. This application allows users to test their knowledge with multiple-choice questions across various categories and difficulty levels.

## Features

- **Modern UI**: Built with CustomTkinter for a sleek, modern interface
- **Multiple Choice Questions**: Answer questions with four options each
- **Timer**: 15-second countdown timer for each question
- **Scoring System**: Points awarded based on difficulty (Easy: 10, Medium: 15, Hard: 20)
- **High Scores**: Save and view top scores
- **Difficulty Levels**: Choose between Easy, Medium, and Hard questions
- **Categories**: Filter questions by category (Science, Geography, etc.)
- **Progress Tracking**: Visual progress bar shows quiz completion status
- **Visual Feedback**: Color-coded feedback for correct/incorrect answers
- **Randomized Questions**: Questions and options are shuffled for each game

## Project Structure

```
QuizGame/
├── main.py           # Entry point for the application
├── quiz_logic.py     # Handles question loading, scoring, and game logic
├── gui.py            # Contains all CustomTkinter GUI code
├── high_scores.py    # Manages saving/loading high scores
├── questions.json    # Stores the question bank
├── high_scores.txt   # Stores high scores (created on first run)
└── README.md         # Documentation
```

## Requirements

- Python 3.6 or higher
- CustomTkinter library

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install customtkinter
```

3. Run the application:

```bash
python main.py
```

## How to Play

1. **Start Screen**: Choose a difficulty level and category, then click "Start Quiz"
2. **Question Screen**: 
   - Read the question and select one of the four options
   - Submit your answer before the 15-second timer expires
   - Correct answers are highlighted in green, incorrect in red
3. **Results Screen**: 
   - View your final score
   - If you achieved a high score, enter your name to save it
4. **High Scores Screen**: 
   - View the top 5 high scores
   - Return to the main menu to play again

## Bonus Features Implemented

1. **Difficulty Levels**: 
   - Questions are categorized as Easy, Medium, or Hard
   - Higher difficulties award more points (Easy: 10, Medium: 15, Hard: 20)

2. **Visual Feedback**: 
   - Correct answers are highlighted in green
   - Incorrect answers are highlighted in red
   - Selected options are visually distinguished

3. **Progress Bar**: 
   - Shows quiz progress (e.g., 3/10 questions completed)
   - Updates after each question

4. **Randomized Options**: 
   - Answer options are shuffled for each question
   - Prevents memorization of option positions

## Customization

- **Adding Questions**: Add more questions to the `questions.json` file following the existing format
- **Appearance**: Modify the appearance mode in `gui.py` (dark/light) to change the overall theme
- **Timer Duration**: Adjust the timer duration in `gui.py` by changing the `self.time_left` value

## License

This project is open-source and available for educational purposes.

## Acknowledgements

- CustomTkinter for providing a modern UI toolkit
- All contributors to the project
## Dedication

This project is dedicated to the rose of my life, my beautiful light.
