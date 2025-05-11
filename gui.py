import customtkinter as ctk
import tkinter as tk
from typing import Callable, List, Dict, Any, Optional, Tuple
import time
import math
from PIL import Image, ImageTk
import os
from quiz_logic import QuizLogic
from high_scores import HighScores
from localization import Localization


class QuizApp:
    """
    Main application class for the Quiz Game GUI using CustomTkinter.
    
    Features enhanced visual feedback with animations for transitions,
    user interactions, and game events.
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

        # Initialize localization system
        self.localization = Localization("en")  # Default to English

        # Initialize variables
        self.timer_id = None
        self.time_left = 20  # Increased time
        self.selected_option = ""
        self.option_buttons = []
        self.current_streak = 0
        self.longest_streak = 0
        self.achievements = {}
        self.theme_var = ctk.StringVar(value="system")
        self.language_var = ctk.StringVar(value="en")
        
        # Animation variables
        self.animation_speed = 10  # ms between animation frames
        self.animation_ids = []  # Store animation IDs for cancellation
        
        # Ensure animations are cleaned up when the window closes
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Scaling factors for responsive design
        self.font_scale = 1.0  # Default font scale
        self.ui_scale = 1.0  # Scale for UI elements (padding, margins)
        self.button_width_scale = 1.0  # Scale for button widths
        self.button_height_scale = 1.0  # Scale for button heights
        self.window_width = 900  # Default window width
        self.window_height = 700  # Default window height
        self._last_size = (900, 700)  # Track window size changes

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
        """Clear all widgets from the content frame with fade-out animation."""
        # Cancel any running animations
        self.cancel_animations()
        
        # Create new content frame that will replace the old one
        new_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        new_frame.grid(row=0, column=0, sticky="nsew")
        new_frame.grid_rowconfigure(0, weight=1)
        new_frame.grid_columnconfigure(0, weight=1)
        
        # If there's an existing frame, animate the transition
        if hasattr(self, 'content_frame') and self.content_frame is not None:
            # Start with the new frame invisible
            new_frame.grid_remove()
            
            # Fade out old frame
            self.fade_out_widget(self.content_frame, 
                                 callback=lambda: self._complete_frame_transition(new_frame))
        else:
            # If no previous frame, just make the new one visible
            new_frame.grid()
            
        # Update content frame reference
        self.content_frame = new_frame
        
    def _complete_frame_transition(self, new_frame: ctk.CTkFrame) -> None:
        """Complete the transition to a new frame after fade-out."""
        # Show the new frame
        new_frame.grid()
        
        # Fade in the new frame
        self.fade_in_widget(new_frame)

    # Animation utility methods
    def cancel_animations(self) -> None:
        """Cancel all running animations."""
        for anim_id in self.animation_ids:
            if anim_id:
                self.root.after_cancel(anim_id)
        self.animation_ids = []
        
    def fade_in_widget(self, widget, duration: int = 500, callback: Optional[Callable] = None) -> None:
        """
        Animate a widget fading in.
        
        Args:
            widget: The widget to animate
            duration: Animation duration in milliseconds
            callback: Function to call when animation completes
        """
        # Ensure the widget exists and is visible
        if not widget.winfo_exists():
            if callback:
                callback()
            return
            
        # Calculate number of steps based on duration and speed
        steps = max(1, duration // self.animation_speed)
        alpha_step = 1.0 / steps
        
        # Set widget initially transparent
        widget.configure(fg_color=self._adjust_color_alpha(
            widget.cget("fg_color") if widget.cget("fg_color") != "transparent" 
            else self.main_frame.cget("fg_color"), 0))
        
        def _fade_step(step, orig_color):
            if not widget.winfo_exists():
                return
            
            alpha = min(1.0, step * alpha_step)
            widget.configure(fg_color=self._adjust_color_alpha(orig_color, alpha))
            
            if step < steps:
                anim_id = self.root.after(
                    self.animation_speed, 
                    lambda: _fade_step(step + 1, orig_color))
                self.animation_ids.append(anim_id)
            elif callback:
                callback()
        
        # Start fade-in animation with the widget's original color
        orig_color = widget.cget("fg_color") if widget.cget("fg_color") != "transparent" else self.main_frame.cget("fg_color")
        _fade_step(0, orig_color)
    
    def fade_out_widget(self, widget, callback: Optional[Callable] = None, duration: int = 300) -> None:
        """
        Animate a widget fading out.
        
        Args:
            widget: The widget to animate
            callback: Function to call when animation completes
            duration: Animation duration in milliseconds
        """
        if not widget.winfo_exists():
            if callback:
                callback()
            return
            
        steps = max(1, duration // self.animation_speed)
        alpha_step = 1.0 / steps
        
        orig_color = widget.cget("fg_color") if widget.cget("fg_color") != "transparent" else self.main_frame.cget("fg_color")
        
        def _fade_step(step):
            if not widget.winfo_exists():
                return
                
            alpha = max(0.0, 1.0 - step * alpha_step)
            widget.configure(fg_color=self._adjust_color_alpha(orig_color, alpha))
            
            if step < steps:
                anim_id = self.root.after(
                    self.animation_speed, 
                    lambda: _fade_step(step + 1))
                self.animation_ids.append(anim_id)
            else:
                # Remove or hide the widget after fade out
                widget.destroy()
                if callback:
                    callback()
        
        _fade_step(0)
    
    def slide_in_widget(self, widget, direction: str = 'left', duration: int = 500, callback: Optional[Callable] = None) -> None:
        """
        Slide in a widget from a direction.
        
        Args:
            widget: The widget to animate
            direction: Direction to slide from ('left', 'right', 'top', 'bottom')
            duration: Animation duration in milliseconds
            callback: Function to call when animation completes
        """
        # Make sure the widget exists and container is configured for packing
        if not widget.winfo_exists():
            if callback:
                callback()
            return
        
        # Get the parent's dimensions
        parent = widget.master
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # If parent dimensions aren't available yet, try again after update
        if parent_width <= 1 or parent_height <= 1:
            parent.update_idletasks()
            anim_id = self.root.after(100, lambda: self.slide_in_widget(widget, direction, duration, callback))
            self.animation_ids.append(anim_id)
            return
            
        # Position the widget initially off-screen
        if direction == 'left':
            widget.place(x=-widget.winfo_reqwidth(), y=0)
            target_x, target_y = 0, 0
        elif direction == 'right':
            widget.place(x=parent_width, y=0)
            target_x, target_y = parent_width - widget.winfo_reqwidth(), 0
        elif direction == 'top':
            widget.place(x=0, y=-widget.winfo_reqheight())
            target_x, target_y = 0, 0
        elif direction == 'bottom':
            widget.place(x=0, y=parent_height)
            target_x, target_y = 0, parent_height - widget.winfo_reqheight()
            
        # Now animate to target position using the slide function
        widget.pack(fill=tk.X, pady=(30, 20))
        
        # Add subtle fade-in effect with the slide
        self.fade_in_widget(widget, duration=duration)
        
        if callback:
            anim_id = self.root.after(duration, callback)
            self.animation_ids.append(anim_id)
    
    def slide_to_position(self, widget, target_x: float = 0.5, target_y: float = 0.5, 
                          start_x: Optional[float] = None, start_y: Optional[float] = None,
                          duration: int = 500, callback: Optional[Callable] = None) -> None:
        """
        Animate a widget sliding to a target position using relative coordinates.
        
        Args:
            widget: The widget to animate
            target_x: Target x position (relative 0-1)
            target_y: Target y position (relative 0-1)
            start_x: Starting x position (relative 0-1, None to use current)
            start_y: Starting y position (relative 0-1, None to use current)
            duration: Animation duration in milliseconds
            callback: Function to call when animation completes
        """
        if not widget.winfo_exists():
            if callback:
                callback()
            return
            
        # Use current position if start positions not specified
        if start_x is None or start_y is None:
            info = widget.place_info()
            current_x = float(info.get('relx', 0.5)) if 'relx' in info else 0.5
            current_y = float(info.get('rely', 0.5)) if 'rely' in info else 0.5
            start_x = start_x if start_x is not None else current_x
            start_y = start_y if start_y is not None else current_y
        
        # Calculate the steps
        steps = max(1, duration // self.animation_speed)
        x_step = (target_x - start_x) / steps
        y_step = (target_y - start_y) / steps
        
        def _slide_step(step):
            if not widget.winfo_exists():
                return
                
            progress = min(1.0, step / steps)
            
            # Use easing function for smoother motion
            eased_progress = self._ease_out_quad(progress)
            
            current_x = start_x + (target_x - start_x) * eased_progress
            current_y = start_y + (target_y - start_y) * eased_progress
            
            widget.place(relx=current_x, rely=current_y, anchor=tk.CENTER)
            
            if step < steps:
                anim_id = self.root.after(
                    self.animation_speed, 
                    lambda: _slide_step(step + 1))
                self.animation_ids.append(anim_id)
            elif callback:
                callback()
                
        _slide_step(0)
    
    def pulse_widget(self, widget, color: str, duration: int = 1000, intensity: float = 0.7) -> None:
        """
        Create a pulsing highlight effect for a widget.
        
        Args:
            widget: The widget to animate
            color: The highlight color to pulse with
            duration: Animation duration in milliseconds
            intensity: Maximum intensity of the pulse (0-1)
        """
        if not widget.winfo_exists():
            return
            
        # Save original colors
        orig_fg = widget.cget("fg_color")
        if orig_fg == "transparent":
            orig_fg = self.main_frame.cget("fg_color")
            
        orig_border = widget.cget("border_color") if hasattr(widget, "border_color") else None
        
        # Number of pulse cycles
        cycles = 2
        steps = max(1, duration // self.animation_speed)
        
        def _pulse_step(step):
            if not widget.winfo_exists():
                return
                
            # Calculate pulse intensity using sine wave
            progress = step / steps
            angle = progress * cycles * 2 * math.pi
            pulse_value = (math.sin(angle) + 1) / 2 * intensity
            
            # Apply the pulse to the widget
            current_color = self._blend_colors(orig_fg, color, pulse_value)
            widget.configure(fg_color=current_color)
            
            # Also pulse the border if it exists
            if orig_border is not None:
                border_color = self._blend_colors(orig_border, color, pulse_value)
                widget.configure(border_color=border_color)
            
            if step < steps:
                anim_id = self.root.after(
                    self.animation_speed, 
                    lambda: _pulse_step(step + 1))
                self.animation_ids.append(anim_id)
            else:
                # Reset to original colors
                widget.configure(fg_color=orig_fg)
                if orig_border is not None:
                    widget.configure(border_color=orig_border)
        
        _pulse_step(0)
    
    def _adjust_color_alpha(self, color, alpha: float) -> str:
        """
        Adjust the alpha (opacity) of a color.
        
        Args:
            color: Color string in format "#RRGGBB" or tuple
            alpha: Alpha value between 0 and 1
            
        Returns:
            Color string with adjusted alpha
        """
        # Handle transparent color
        if color == "transparent":
            return color
            
        # Handle tuple mode colors from CustomTkinter
        if isinstance(color, tuple):
            if len(color) == 2:
                # CTk tuple format (light mode color, dark mode color)
                # Use the appropriate one based on the current appearance mode
                mode = ctk.get_appearance_mode().lower()
                color = color[0] if mode == "light" else color[1]
                
        # Try to parse hex color
        if isinstance(color, str) and color.startswith("#"):
            # Convert hex to RGB
            r = int(color[1:3], 16) / 255.0
            g = int(color[3:5], 16) / 255.0
            b = int(color[5:7], 16) / 255.0
            
            # Blend with white based on alpha
            r = r * alpha + (1 - alpha)
            g = g * alpha + (1 - alpha)
            b = b * alpha + (1 - alpha)
            
            # Convert back to hex
            return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
        
        # Fall back to original color if we can't parse it
        return color
    
    def _blend_colors(self, color1, color2, ratio: float) -> str:
        """
        Blend two colors together.
        
        Args:
            color1: First color string "#RRGGBB" or tuple
            color2: Second color string "#RRGGBB" or tuple
            ratio: Blend ratio (0 = all color1, 1 = all color2)
            
        Returns:
            Blended color string
        """
        # Handle transparent colors
        if color1 == "transparent":
            color1 = self.main_frame.cget("fg_color")
        if color2 == "transparent":
            color2 = self.main_frame.cget("fg_color")
            
        # Handle tuple mode colors
        if isinstance(color1, tuple):
            mode = ctk.get_appearance_mode().lower()
            color1 = color1[0] if mode == "light" else color1[1]
        if isinstance(color2, tuple):
            mode = ctk.get_appearance_mode().lower()
            color2 = color2[0] if mode == "light" else color2[1]
            
        # Parse hex colors
        if isinstance(color1, str) and color1.startswith("#"):
            r1 = int(color1[1:3], 16) / 255.0
            g1 = int(color1[3:5], 16) / 255.0
            b1 = int(color1[5:7], 16) / 255.0
        else:
            r1, g1, b1 = 0.5, 0.5, 0.5  # Default gray
            
        if isinstance(color2, str) and color2.startswith("#"):
            r2 = int(color2[1:3], 16) / 255.0
            g2 = int(color2[3:5], 16) / 255.0
            b2 = int(color2[5:7], 16) / 255.0
        else:
            r2, g2, b2 = 0.5, 0.5, 0.5  # Default gray
            
        # Blend the colors
        r = r1 * (1 - ratio) + r2 * ratio
        g = g1 * (1 - ratio) + g2 * ratio
        b = b1 * (1 - ratio) + b2 * ratio
        
        # Return the blended color
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
    
    def _ease_out_quad(self, x: float) -> float:
        """
        Quadratic ease-out function for smooth animations.
        
        Args:
            x: Input value between 0-1
            
        Returns:
            Eased value between 0-1
        """
        return 1 - (1 - x) * (1 - x)
    
    def on_window_resize(self, event) -> None:
        """
        Handle window resize events to ensure responsive layout.
        Adjusts font sizes, padding, and layout based on window dimensions.
        """
        # Only process events from the root window
        if event.widget == self.root:
            width = event.width
            height = event.height

            # Store current dimensions for responsive calculations
            self.window_width = width
            self.window_height = height

            # Adjust font sizes based on window width
            if width < 500:
                self.font_scale = 0.75
            elif width < 700:
                self.font_scale = 0.85
            elif width < 900:
                self.font_scale = 0.95
            else:
                self.font_scale = 1.0

            # Adjust padding and spacing based on window size
            if width < 600 or height < 500:
                self.ui_scale = 0.7
            elif width < 800 or height < 600:
                self.ui_scale = 0.85
            else:
                self.ui_scale = 1.0

            # Adjust button sizes for smaller screens
            if width < 500:
                self.button_width_scale = 0.7
                self.button_height_scale = 0.8
            elif width < 700:
                self.button_width_scale = 0.85
                self.button_height_scale = 0.9
            else:
                self.button_width_scale = 1.0
                self.button_height_scale = 1.0

            # Refresh current screen if needed for major size changes
            # This helps ensure proper layout after significant resizing
            if hasattr(self, '_last_size') and (
                abs(self._last_size[0] - width) > 200 or
                abs(self._last_size[1] - height) > 200
            ):
                # Store current screen before refreshing
                current_screen = getattr(self, '_current_screen', 'welcome')

                # Refresh the current screen
                if current_screen == 'welcome':
                    self.root.after(100, self.show_welcome_screen)
                elif current_screen == 'question':
                    self.root.after(100, self.show_question_screen)
                elif current_screen == 'results':
                    self.root.after(100, self.show_results_screen)
                elif current_screen == 'high_scores':
                    self.root.after(100, self.show_high_scores_screen)

            # Store current size for comparison on next resize
            self._last_size = (width, height)

    def get_font(self, size: int, weight: str = "normal", slant: str = "roman") -> ctk.CTkFont:
        """
        Get a scaled font based on window size with robust error handling.

        Args:
            size: Base font size
            weight: Font weight (normal, bold)
            slant: Font slant (roman, italic)

        Returns:
            Scaled CTkFont object
        """
        try:
            # Convert string parameters to valid values for CTkFont
            weight_val = "bold" if weight == "bold" else "normal"
            slant_val = "italic" if slant == "italic" else "roman"

            # Scale the font size based on window size
            scaled_size = int(size * getattr(self, 'font_scale', 1.0))

            # Create and return a new font
            return ctk.CTkFont(size=scaled_size, weight=weight_val, slant=slant_val)
        except Exception as e:
            # Log the error
            print(f"Error creating font: {e}")

            # Fallback to a default font
            try:
                return ctk.CTkFont(size=size)
            except Exception:
                # If all else fails, return None and let the widget use its default font
                print("Critical font creation error, using system default")
                return None

    def show_welcome_screen(self) -> None:
        """Display the welcome screen with options to start quiz or view high scores."""
        self.clear_frame()

        # Track current screen for language switching
        self._current_screen = 'welcome'

        # Check if we need RTL layout
        is_rtl = self.localization.is_rtl()

        welcome_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        welcome_container.pack(fill=tk.BOTH, expand=True)

        # Title with animated effect
        title_frame = ctk.CTkFrame(welcome_container, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(30, 20))
        
        # Start with the title frame hidden for animation
        title_frame.pack_forget()
        
        # Schedule the title frame to appear with a slide-in animation
        self.root.after(100, lambda: self.slide_in_widget(title_frame, 'top'))

        title_label = ctk.CTkLabel(
            title_frame,
            text=self.get_text("app_title"),
            font=self.get_font(38, "bold"),
            text_color=self.colors["accent"]
        )
        title_label.pack(pady=(10, 5))

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text=self.get_text("welcome_subtitle"),
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
            text=self.get_text("num_questions"),
            font=self.get_font(16)
        )
        questions_label.grid(row=0, column=0, sticky="w" if not is_rtl else "e", padx=20, pady=(20, 10))

        questions_values = ["5", "10", "15", "20"]
        questions_var = ctk.StringVar(value="10")

        questions_dropdown = ctk.CTkOptionMenu(
            options_frame,
            values=questions_values,
            variable=questions_var,
            width=150,
            dynamic_resizing=False
        )
        questions_dropdown.grid(row=0, column=1, sticky="e" if not is_rtl else "w", padx=20, pady=(20, 10))

        # Difficulty selection
        difficulty_label = ctk.CTkLabel(
            options_frame,
            text=self.get_text("difficulty_level"),
            font=self.get_font(16)
        )
        difficulty_label.grid(row=1, column=0, sticky="w" if not is_rtl else "e", padx=20, pady=10)

        # Translate difficulty levels
        raw_difficulties = ["all"] + self.quiz_logic.get_available_difficulties()
        difficulties = [self.get_text(d) for d in raw_difficulties]
        difficulty_map = dict(zip(difficulties, raw_difficulties))
        difficulty_var = ctk.StringVar(value=difficulties[0])

        difficulty_dropdown = ctk.CTkOptionMenu(
            options_frame,
            values=difficulties,
            variable=difficulty_var,
            width=150,
            dynamic_resizing=False
        )
        difficulty_dropdown.grid(row=1, column=1, sticky="e" if not is_rtl else "w", padx=20, pady=10)

        # Category selection
        category_label = ctk.CTkLabel(
            options_frame,
            text=self.get_text("category"),
            font=self.get_font(16)
        )
        category_label.grid(row=2, column=0, sticky="w" if not is_rtl else "e", padx=20, pady=10)

        categories = ["all"] + self.quiz_logic.get_available_categories()
        category_var = ctk.StringVar(value=categories[0])

        category_dropdown = ctk.CTkOptionMenu(
            options_frame,
            values=categories,
            variable=category_var,
            width=150,
            dynamic_resizing=False
        )
        category_dropdown.grid(row=2, column=1, sticky="e" if not is_rtl else "w", padx=20, pady=10)

        # Timer duration
        timer_label = ctk.CTkLabel(
            options_frame,
            text=self.get_text("timer_seconds"),
            font=self.get_font(16)
        )
        timer_label.grid(row=3, column=0, sticky="w" if not is_rtl else "e", padx=20, pady=10)

        timer_values = ["10", "15", "20", "30"]
        timer_var = ctk.StringVar(value="20")

        timer_dropdown = ctk.CTkOptionMenu(
            options_frame,
            values=timer_values,
            variable=timer_var,
            width=150,
            dynamic_resizing=False
        )
        timer_dropdown.grid(row=3, column=1, sticky="e" if not is_rtl else "w", padx=20, pady=10)

        # Theme selection
        theme_label = ctk.CTkLabel(
            options_frame,
            text=self.get_text("theme"),
            font=self.get_font(16)
        )
        theme_label.grid(row=4, column=0, sticky="w" if not is_rtl else "e", padx=20, pady=10)

        # Create dropdown for theme selection
        theme_values = [self.get_text("light"), self.get_text("dark"), self.get_text("system")]
        theme_map = {
            self.get_text("light"): "Light",
            self.get_text("dark"): "Dark",
            self.get_text("system"): "System"
        }

        def on_theme_change(value):
            self.change_theme(theme_map[value])

        theme_dropdown = ctk.CTkOptionMenu(
            options_frame,
            values=theme_values,
            command=on_theme_change,
            width=150,
            dynamic_resizing=False
        )
        theme_dropdown.grid(row=4, column=1, sticky="e" if not is_rtl else "w", padx=20, pady=10)

        # Set default theme
        theme_dropdown.set(self.get_text("system"))

        # Language selection
        language_label = ctk.CTkLabel(
            options_frame,
            text=self.get_text("language"),
            font=self.get_font(16)
        )
        language_label.grid(row=5, column=0, sticky="w" if not is_rtl else "e", padx=20, pady=(10, 20))

        # Get available languages
        languages = self.localization.get_available_languages()
        language_values = list(languages.keys())

        # Create a mapping from display name to language code
        language_display = [f"{code} - {name}" for code, name in languages.items()]
        language_map = dict(zip(language_display, language_values))

        def on_language_change(value):
            lang_code = language_map[value]
            self.change_language(lang_code)

        language_dropdown = ctk.CTkOptionMenu(
            options_frame,
            values=language_display,
            command=on_language_change,
            width=150,
            dynamic_resizing=False
        )
        language_dropdown.grid(row=5, column=1, sticky="e" if not is_rtl else "w", padx=20, pady=(10, 20))

        # Set current language
        current_lang_display = next((disp for disp, code in language_map.items()
                                    if code == self.language_var.get()), language_display[0])
        language_dropdown.set(current_lang_display)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(welcome_container, fg_color="transparent")
        buttons_frame.pack(fill=tk.X, pady=30)

        # Centered button frame
        center_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        center_frame.pack(expand=True)

        # Start button with accent color
        start_button = ctk.CTkButton(
            center_frame,
            text=self.get_text("start_quiz"),
            font=self.get_font(20),
            height=50,
            width=200,
            fg_color=self.colors["accent"],
            hover_color=self.colors["secondary"],
            command=lambda: self.start_quiz(
                # Map localized difficulty back to internal value
                difficulty_map.get(difficulty_var.get(), "all"),
                category_var.get(),
                int(questions_var.get()),
                int(timer_var.get())
            )
        )
        start_button.pack(pady=10)

        # High scores button
        high_scores_button = ctk.CTkButton(
            center_frame,
            text=self.get_text("view_high_scores"),
            font=self.get_font(16),
            height=40,
            width=200,
            command=self.show_high_scores_screen
        )
        high_scores_button.pack(pady=10)

        # Achievements button
        achievements_button = ctk.CTkButton(
            center_frame,
            text=self.get_text("achievements"),
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

    def change_language(self, value: str) -> None:
        """
        Change the application language.

        Args:
            value: Language code (en, ar)
        """
        if self.localization.change_language(value):
            # Update UI with new language
            self.language_var.set(value)

            # Refresh the current screen to apply new language
            current_screen = getattr(self, '_current_screen', 'welcome')
            if current_screen == 'welcome':
                self.show_welcome_screen()
            elif current_screen == 'question':
                self.show_question_screen()
            elif current_screen == 'results':
                self.show_results_screen()
            elif current_screen == 'high_scores':
                self.show_high_scores_screen()

    def get_text(self, key: str, **kwargs) -> str:
        """
        Get localized text for the given key.

        Args:
            key: The translation key
            **kwargs: Format parameters for the translated string

        Returns:
            Localized text
        """
        return self.localization.get_text(key, **kwargs)

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
        """Display the current question with options and timer with enhanced UI and animations."""
        self.clear_frame()
        self.cancel_timer()

        question = self.quiz_logic.get_current_question()
        if not question:
            self.show_results_screen()
            return

        question_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        question_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Start with container invisible for animation
        question_container.pack_forget()
        self.root.after(100, lambda: self.fade_in_widget(question_container, duration=300))
        self.root.after(100, lambda: question_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10))

        # Top bar with stats
        top_bar = ctk.CTkFrame(question_container)
        top_bar.pack(fill=tk.X, pady=(5, 15))
        
        # Animate the top bar sliding in from left
        top_bar.pack_forget()
        self.root.after(200, lambda: self.slide_in_widget(top_bar, direction='left', duration=400))
        self.root.after(200, lambda: top_bar.pack(fill=tk.X, pady=(5, 15)))

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

        # Question card with animation
        question_card = ctk.CTkFrame(question_container)
        question_card.pack(fill=tk.X, padx=20, pady=10, ipady=10)
        
        # Animate question card sliding in from right
        question_card.pack_forget()
        self.root.after(300, lambda: self.slide_in_widget(question_card, direction='right', duration=500))
        self.root.after(300, lambda: question_card.pack(fill=tk.X, padx=20, pady=10, ipady=10))

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
        
        # Start with options frame hidden for animated reveal
        options_frame.pack_forget()
        self.root.after(400, lambda: self.fade_in_widget(options_frame, duration=400))
        self.root.after(400, lambda: options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10))

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
            
            # Initially hide the frame for staggered animation
            option_frame.grid_remove()
            
            # Schedule appearance with staggered timing based on index
            delay = 500 + (i * 150)
            self.root.after(delay, lambda frame=option_frame: frame.grid())
            self.root.after(delay, lambda frame=option_frame: self.pulse_widget(frame, self.colors["primary"], duration=300, intensity=0.3))

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
        
        # Start with button frame hidden for animation
        button_frame.pack_forget()
        self.root.after(800, lambda: self.slide_in_widget(button_frame, direction='bottom', duration=400))
        self.root.after(800, lambda: button_frame.pack(pady=15))

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
        
        # Add subtle pulsing effect to the submit button when enabled
        def pulse_submit_if_enabled():
            if self.submit_button.cget("state") == "normal":
                self.pulse_widget(self.submit_button, self.colors["highlight"], duration=1500, intensity=0.4)
            self.root.after(2000, pulse_submit_if_enabled)
            
        # Start pulsing animation loop
        self.root.after(1000, pulse_submit_if_enabled)

        # Add a small gap between buttons for better spacing
        ctk.CTkLabel(button_frame, text="", height=10).pack()
        
        # Hint button (disabled if no hint available) with animation
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
        """Cancel the active timer if one exists."""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
            
    def _on_close(self) -> None:
        """Clean up resources and close the application."""
        # Cancel any running animations and timers
        self.cancel_animations()
        self.cancel_timer()
        
        # Destroy the root window
        self.root.destroy()

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

                # Show streak bonus message with animation
                streak_bonus_label = ctk.CTkLabel(
                    self.content_frame,
                    text=f"🔥 Streak Bonus: +{streak_bonus} points!",
                    font=self.get_font(16, "bold"),
                    text_color=self.colors["highlight"]
                )
                
                # Position initially off-screen
                streak_bonus_label.place(relx=1.5, rely=0.2, anchor=tk.CENTER)
                
                # Animate sliding in from right
                self.slide_to_position(streak_bonus_label, target_x=0.5, start_x=1.5)

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
        
        # Position the frame but initially invisible
        feedback_frame.place(relx=0.5, rely=-0.2, anchor=tk.CENTER)

        feedback_text = "✓ Correct!" if is_correct else "✗ Incorrect!"
        feedback_label = ctk.CTkLabel(
            feedback_frame,
            text=feedback_text,
            font=self.get_font(18, "bold"),
            text_color="white"
        )
        feedback_label.pack(padx=15, pady=8)
        
        # Animate the feedback frame sliding in from top
        self.slide_to_position(feedback_frame, target_y=0.1, start_y=-0.2)
        
        # Highlight the correct option button with a pulsing effect
        for btn, option_text in self.option_buttons:
            if option_text == correct_answer:
                self.pulse_widget(btn, 
                                  color=self.colors["correct"],
                                  duration=1000)
            elif option_text == self.selected_option and not is_correct:
                self.pulse_widget(btn, 
                                  color=self.colors["incorrect"],
                                  duration=1000)

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
        self.cancel_animations()

        results_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        results_container.pack(fill=tk.BOTH, expand=True)
        
        # Start with container invisible for animation
        results_container.pack_forget()
        self.root.after(100, lambda: self.fade_in_widget(results_container, duration=400))
        self.root.after(100, lambda: results_container.pack(fill=tk.BOTH, expand=True))

        # Results title with celebration emojis
        title_frame = ctk.CTkFrame(results_container, fg_color="transparent")
        title_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Animate title with a slide-in effect
        title_frame.pack_forget()
        self.root.after(200, lambda: self.slide_in_widget(title_frame, direction='top', duration=500))
        self.root.after(200, lambda: title_frame.pack(fill=tk.X, pady=(20, 0)))

        title_label = ctk.CTkLabel(
            title_frame,
            text="🎉 Quiz Complete! 🎉",
            font=self.get_font(32, "bold"),
            text_color=self.colors["accent"]
        )
        title_label.pack(pady=(20, 10))

        # Statistics card with animation
        stats_frame = ctk.CTkFrame(results_container)
        stats_frame.pack(pady=20, padx=40, fill=tk.X)
        
        # Animate stats frame with a fade-in effect
        stats_frame.pack_forget()
        self.root.after(400, lambda: self.fade_in_widget(stats_frame, duration=600))
        self.root.after(400, lambda: stats_frame.pack(pady=20, padx=40, fill=tk.X))

        # Final score with large display and animation
        score_label = ctk.CTkLabel(
            stats_frame,
            text=f"{self.quiz_logic.score}",
            font=self.get_font(48, "bold"),
            text_color=self.colors["highlight"]
        )
        score_label.pack(pady=(20, 5))
        
        # Animate the score with a pulse effect
        self.root.after(800, lambda: self.pulse_widget(score_label, self.colors["accent"], duration=1200, intensity=0.5))

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
