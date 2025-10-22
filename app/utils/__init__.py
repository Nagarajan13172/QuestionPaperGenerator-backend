"""
Utilities package
Add utility functions here as needed
"""

def format_question_number(index: int, total: int) -> str:
    """Format question number with leading zeros"""
    width = len(str(total))
    return f"{index:0{width}d}"


def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename"""
    import re
    return re.sub(r'[^\w\s-]', '', filename).strip()


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time in minutes"""
    words = len(text.split())
    return max(1, words // words_per_minute)
