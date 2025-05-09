"""
Localization module for the Quiz Master application.

This module provides translation functionality for the application,
supporting multiple languages including Arabic.
"""

from typing import Dict, Any, Optional


class Localization:
    """
    Handles localization and translation for the Quiz Master application.
    
    Supports multiple languages and provides methods to translate text
    and switch between languages.
    """
    
    # Available languages
    LANGUAGES = {
        "en": "English",
        "ar": "العربية"  # Arabic
    }
    
    # Default language
    DEFAULT_LANGUAGE = "en"
    
    def __init__(self, language: str = DEFAULT_LANGUAGE):
        """
        Initialize the localization system.
        
        Args:
            language: The language code to use (default: English)
        """
        self.current_language = language if language in self.LANGUAGES else self.DEFAULT_LANGUAGE
        self._translations = self._load_translations()
        
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """
        Load all translations for supported languages.
        
        Returns:
            Dictionary of translations for all supported languages
        """
        translations = {
            "en": {
                # General
                "app_title": "Quiz Master",
                "loading": "Loading...",
                "version": "Version",
                
                # Welcome screen
                "welcome_subtitle": "Test your knowledge and compete for high scores!",
                "num_questions": "Number of Questions:",
                "difficulty_level": "Difficulty Level:",
                "category": "Category:",
                "timer_seconds": "Timer (seconds):",
                "theme": "Theme:",
                "start_quiz": "Start Quiz",
                "view_high_scores": "View High Scores",
                "achievements": "Achievements",
                
                # Difficulty levels
                "all": "All",
                "easy": "Easy",
                "medium": "Medium",
                "hard": "Hard",
                
                # Theme options
                "light": "Light",
                "dark": "Dark",
                "system": "System",
                
                # Question screen
                "question_of": "Question {current} of {total}",
                "streak": "Streak: {streak}",
                "score": "Score: {score}",
                "seconds_remaining": "seconds remaining",
                "submit_answer": "Submit Answer",
                "use_hint": "Use Hint (-5 pts)",
                "skip_question": "Skip Question",
                "times_up": "Time's Up!",
                
                # Results screen
                "quiz_completed": "Quiz Completed!",
                "final_score": "Final Score: {score}",
                "correct_answers": "Correct Answers: {correct}/{total}",
                "accuracy": "Accuracy: {accuracy}%",
                "avg_time": "Average Time: {time} seconds",
                "longest_streak": "Longest Streak: {streak}",
                "new_high_score": "New High Score!",
                "enter_name": "Enter your name:",
                "save_score": "Save Score",
                "play_again": "Play Again",
                "high_scores": "High Scores",
                
                # High scores screen
                "high_scores_title": "High Scores",
                "rank": "Rank",
                "name": "Name",
                "score_header": "Score",
                "no_scores": "No high scores yet!",
                "back_to_menu": "Back to Menu",
                
                # Error messages
                "error": "Error",
                "no_questions": "No questions available for the selected criteria.",
                
                # Language
                "language": "Language:",
            },
            
            "ar": {
                # General - Arabic translations
                "app_title": "سيد الاختبار",
                "loading": "جاري التحميل...",
                "version": "الإصدار",
                
                # Welcome screen
                "welcome_subtitle": "اختبر معلوماتك وتنافس على أعلى الدرجات!",
                "num_questions": "عدد الأسئلة:",
                "difficulty_level": "مستوى الصعوبة:",
                "category": "الفئة:",
                "timer_seconds": "المؤقت (ثواني):",
                "theme": "المظهر:",
                "start_quiz": "ابدأ الاختبار",
                "view_high_scores": "عرض أعلى الدرجات",
                "achievements": "الإنجازات",
                
                # Difficulty levels
                "all": "الكل",
                "easy": "سهل",
                "medium": "متوسط",
                "hard": "صعب",
                
                # Theme options
                "light": "فاتح",
                "dark": "داكن",
                "system": "النظام",
                
                # Question screen
                "question_of": "سؤال {current} من {total}",
                "streak": "التتابع: {streak}",
                "score": "النتيجة: {score}",
                "seconds_remaining": "ثواني متبقية",
                "submit_answer": "إرسال الإجابة",
                "use_hint": "استخدم تلميح (-5 نقاط)",
                "skip_question": "تخطي السؤال",
                "times_up": "انتهى الوقت!",
                
                # Results screen
                "quiz_completed": "اكتمل الاختبار!",
                "final_score": "النتيجة النهائية: {score}",
                "correct_answers": "الإجابات الصحيحة: {correct}/{total}",
                "accuracy": "الدقة: {accuracy}%",
                "avg_time": "متوسط الوقت: {time} ثانية",
                "longest_streak": "أطول تتابع: {streak}",
                "new_high_score": "نتيجة عالية جديدة!",
                "enter_name": "أدخل اسمك:",
                "save_score": "حفظ النتيجة",
                "play_again": "العب مرة أخرى",
                "high_scores": "أعلى الدرجات",
                
                # High scores screen
                "high_scores_title": "أعلى الدرجات",
                "rank": "الترتيب",
                "name": "الاسم",
                "score_header": "النتيجة",
                "no_scores": "لا توجد درجات عالية حتى الآن!",
                "back_to_menu": "العودة إلى القائمة",
                
                # Error messages
                "error": "خطأ",
                "no_questions": "لا توجد أسئلة متاحة للمعايير المحددة.",
                
                # Language
                "language": "اللغة:",
            }
        }
        
        return translations
    
    def get_text(self, key: str, **kwargs) -> str:
        """
        Get translated text for the given key.
        
        Args:
            key: The translation key
            **kwargs: Format parameters for the translated string
            
        Returns:
            Translated text, or the key itself if translation not found
        """
        # Get the translation dictionary for the current language
        translations = self._translations.get(self.current_language, {})
        
        # Get the translated text or fall back to the key itself
        text = translations.get(key, key)
        
        # Apply formatting if kwargs are provided
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        
        return text
    
    def change_language(self, language: str) -> bool:
        """
        Change the current language.
        
        Args:
            language: The language code to switch to
            
        Returns:
            True if language was changed, False otherwise
        """
        if language in self.LANGUAGES:
            self.current_language = language
            return True
        return False
    
    def get_available_languages(self) -> Dict[str, str]:
        """
        Get a dictionary of available languages.
        
        Returns:
            Dictionary mapping language codes to language names
        """
        return self.LANGUAGES.copy()
    
    def is_rtl(self) -> bool:
        """
        Check if the current language is right-to-left.
        
        Returns:
            True if the current language is RTL, False otherwise
        """
        # Arabic is RTL
        return self.current_language == "ar"
