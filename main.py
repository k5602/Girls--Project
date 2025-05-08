import customtkinter as ctk
from gui import QuizApp


def main():
    """
    Main entry point for the Quiz Game application.
    Initializes the CustomTkinter root window and starts the application.
    """
    # Initialize the root window
    root = ctk.CTk()
    
    # Create the quiz application
    app = QuizApp(root)
    
    # Start the main event loop
    root.mainloop()


if __name__ == "__main__":
    main()
