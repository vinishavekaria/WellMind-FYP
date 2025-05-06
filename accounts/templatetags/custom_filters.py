from django import template

register = template.Library()

mood_colors = {
    "Happy": "#4CAF50",      # Green
    "Inspired": "#FF9800",   # Orange
    "Grateful": "#FFC107",   # Yellow
    "Sad": "#2196F3",        # Blue
    "Angry": "#F44336",      # Red
    "Stressed": "#795548",   # Brown
    "Neutral": "#9E9E9E",    # Gray
    "Calm": "#8BC34A",       # Light Green
    "Reflective": "#673AB7", # Purple
    "No Data": "#E0E0E0"     # Light Gray (no entry)
}

@register.filter
def get_item(mood):
    return mood_colors.get(mood, "#E0E0E0")  # Default color for missing moods

