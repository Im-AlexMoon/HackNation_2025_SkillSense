"""
SkillSense Visualization Module

Provides reusable chart creation, metric styling, and layout helpers
for the Streamlit frontend.
"""

from .colors import (
    COLOR_PALETTE,
    CONFIDENCE_COLORS,
    CATEGORY_COLORS,
    DETECTION_COLORS,
    SOURCE_COLORS,
    MATCH_SCORE_COLORS,
    get_confidence_color,
    get_category_color,
    get_detection_color,
    get_source_color,
    get_match_color,
    CUSTOM_CSS,
)

from .metrics import (
    inject_metric_styles,
    create_styled_metric_card,
    create_metric_grid,
    create_confidence_metric_card,
    create_stat_card,
)

from .charts import (
    create_confidence_distribution,
    create_category_breakdown,
    create_source_contribution,
    create_detection_method_breakdown,
    create_skill_evidence_heatmap,
    create_match_score_gauge,
    create_skills_gap_waterfall,
    create_required_vs_preferred,
    create_profile_completeness_gauge,
    create_skills_portfolio_bubble,
)

from .layouts import (
    create_skill_badge_html,
    create_skills_grid,
    create_job_card,
    create_job_cards_grid,
    create_category_section,
    create_metrics_row,
    create_info_card,
    create_skill_detail_card,
)

__all__ = [
    # Colors
    "COLOR_PALETTE",
    "CONFIDENCE_COLORS",
    "CATEGORY_COLORS",
    "DETECTION_COLORS",
    "SOURCE_COLORS",
    "MATCH_SCORE_COLORS",
    "get_confidence_color",
    "get_category_color",
    "get_detection_color",
    "get_source_color",
    "get_match_color",
    "CUSTOM_CSS",

    # Metrics
    "inject_metric_styles",
    "create_styled_metric_card",
    "create_metric_grid",
    "create_confidence_metric_card",
    "create_stat_card",

    # Charts
    "create_confidence_distribution",
    "create_category_breakdown",
    "create_source_contribution",
    "create_detection_method_breakdown",
    "create_skill_evidence_heatmap",
    "create_match_score_gauge",
    "create_skills_gap_waterfall",
    "create_required_vs_preferred",
    "create_profile_completeness_gauge",
    "create_skills_portfolio_bubble",

    # Layouts
    "create_skill_badge_html",
    "create_skills_grid",
    "create_job_card",
    "create_job_cards_grid",
    "create_category_section",
    "create_metrics_row",
    "create_info_card",
    "create_skill_detail_card",
]
