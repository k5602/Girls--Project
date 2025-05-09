import customtkinter as ctk
import tkinter as tk
from gui import QuizApp
import time


def main():
    """
    Main entry point for the Quiz Game application.
    Initializes the application directly without a splash screen.
    """
    # Initialize the root window with a modern theme
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")

    # Create the root window
    root = ctk.CTk()
    root.title("Quiz Master")
    root.geometry("900x700")

    # Create the quiz application
    app = QuizApp(root)

    # Start the main event loop
    root.mainloop()


if __name__ == "__main__":
    main()
