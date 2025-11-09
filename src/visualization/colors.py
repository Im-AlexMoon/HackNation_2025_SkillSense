"""
SkillSense Color Palette & Theme Configuration

Defines the complete color system for consistent UI styling.
"""

# Primary Color Palette
COLOR_PALETTE = {
    "primary": "#003B73",        # Navy blue
    "secondary": "#14B8A6",      # Teal
    "accent": "#F97316",         # Orange
    "success": "#10B981",        # Green
    "warning": "#F59E0B",        # Amber/Yellow
    "error": "#EF4444",          # Red
    "info": "#3B82F6",           # Blue
    "surface": "#F6F7FB",        # Light background
    "surface_dark": "#0D1B2A",   # Dark background
    "text": "#0F172A",           # Dark text
    "text_light": "#6B7280",     # Light text (muted)
    "border": "#E5E7EB",         # Light border
    "border_dark": "#1F2937",    # Dark border
}

# Confidence Level Colors
CONFIDENCE_COLORS = {
    "very_high": COLOR_PALETTE["success"],    # Green - 0.9+
    "high": "#059669",                         # Dark green - 0.7-0.89
    "medium": COLOR_PALETTE["warning"],        # Amber - 0.5-0.69
    "low": "#DC2626",                          # Dark red - 0.3-0.49
    "very_low": COLOR_PALETTE["error"],        # Red - <0.3
}

# Skill Category Colors (15 categories)
CATEGORY_COLORS = {
    "programming_languages": "#EC4899",      # Pink
    "web_development": "#3B82F6",            # Blue
    "mobile_development": "#8B5CF6",         # Purple
    "data_science": "#F59E0B",               # Amber
    "cloud_devops": "#0EA5E9",               # Sky blue
    "databases": "#10B981",                  # Emerald
    "ai_ml": "#D946EF",                      # Fuchsia
    "communication": "#06B6D4",              # Cyan
    "leadership": "#F97316",                 # Orange
    "collaboration": "#6366F1",              # Indigo
    "problem_solving": "#14B8A6",            # Teal
    "personal_traits": "#A78BFA",            # Violet
    "business": "#EF4444",                   # Red
    "design": "#EC4899",                     # Pink
    "industries": "#84CC16",                 # Lime
}

# Detection Method Colors
DETECTION_COLORS = {
    "explicit": COLOR_PALETTE["success"],    # Green - keyword matched
    "contextual": COLOR_PALETTE["warning"],  # Amber - pattern matched
    "semantic": COLOR_PALETTE["info"],       # Blue - similarity matched
}

# Source Type Colors
SOURCE_COLORS = {
    "cv": "#3B82F6",                    # Blue
    "github": "#1F2937",                # Dark gray
    "personal_statement": "#8B5CF6",    # Purple
    "reference_letter": "#F97316",      # Orange
}

# Match Score Colors (for gauges)
MATCH_SCORE_COLORS = {
    "excellent": COLOR_PALETTE["success"],   # Green - >80%
    "good": "#06B6D4",                       # Cyan - 60-80%
    "fair": COLOR_PALETTE["warning"],        # Amber - 40-60%
    "poor": COLOR_PALETTE["error"],          # Red - <40%
}


def get_confidence_color(confidence: float) -> str:
    """Get color based on confidence score (0.0-1.0)"""
    if confidence >= 0.9:
        return CONFIDENCE_COLORS["very_high"]
    elif confidence >= 0.7:
        return CONFIDENCE_COLORS["high"]
    elif confidence >= 0.5:
        return CONFIDENCE_COLORS["medium"]
    elif confidence >= 0.3:
        return CONFIDENCE_COLORS["low"]
    else:
        return CONFIDENCE_COLORS["very_low"]


def get_category_color(category: str) -> str:
    """Get color for skill category"""
    return CATEGORY_COLORS.get(category, COLOR_PALETTE["primary"])


def get_detection_color(method: str) -> str:
    """Get color for detection method"""
    return DETECTION_COLORS.get(method, COLOR_PALETTE["primary"])


def get_source_color(source: str) -> str:
    """Get color for data source"""
    return SOURCE_COLORS.get(source, COLOR_PALETTE["primary"])


def get_match_color(score: float) -> str:
    """Get color based on match score (0.0-1.0)"""
    if score >= 0.8:
        return MATCH_SCORE_COLORS["excellent"]
    elif score >= 0.6:
        return MATCH_SCORE_COLORS["good"]
    elif score >= 0.4:
        return MATCH_SCORE_COLORS["fair"]
    else:
        return MATCH_SCORE_COLORS["poor"]


# CSS for custom styling
CUSTOM_CSS = f"""
<style>
:root {{
    --primary: {COLOR_PALETTE['primary']};
    --secondary: {COLOR_PALETTE['secondary']};
    --accent: {COLOR_PALETTE['accent']};
    --success: {COLOR_PALETTE['success']};
    --warning: {COLOR_PALETTE['warning']};
    --error: {COLOR_PALETTE['error']};
    --text: {COLOR_PALETTE['text']};
    --surface: {COLOR_PALETTE['surface']};
}}

.metric-card {{
    padding: 1.5rem;
    border-radius: 12px;
    background: white;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    border-left: 4px solid var(--primary);
}}

.metric-card-high {{
    border-left-color: {CONFIDENCE_COLORS['high']};
}}

.metric-card-medium {{
    border-left-color: {CONFIDENCE_COLORS['medium']};
}}

.metric-card-low {{
    border-left-color: {CONFIDENCE_COLORS['low']};
}}

.skill-badge {{
    display: inline-block;
    padding: 0.375rem 0.75rem;
    margin: 0.25rem;
    border-radius: 16px;
    font-size: 0.875rem;
    font-weight: 500;
}}

.skill-badge-high {{
    background-color: {CONFIDENCE_COLORS['high']}20;
    color: {CONFIDENCE_COLORS['high']};
    border: 1px solid {CONFIDENCE_COLORS['high']};
}}

.skill-badge-medium {{
    background-color: {CONFIDENCE_COLORS['medium']}20;
    color: {CONFIDENCE_COLORS['medium']};
    border: 1px solid {CONFIDENCE_COLORS['medium']};
}}

.skill-badge-low {{
    background-color: {CONFIDENCE_COLORS['low']}20;
    color: {CONFIDENCE_COLORS['low']};
    border: 1px solid {CONFIDENCE_COLORS['low']};
}}
</style>
"""
