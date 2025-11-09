"""
Chart Creation Functions

Provides reusable Plotly chart creation for skill analysis visualizations.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Tuple
import pandas as pd
from .colors import (
    COLOR_PALETTE,
    CONFIDENCE_COLORS,
    CATEGORY_COLORS,
    DETECTION_COLORS,
    get_confidence_color,
    get_category_color,
)


@st.cache_data
def create_confidence_distribution(confidences: List[float]) -> go.Figure:
    """
    Create histogram of confidence score distribution.

    Args:
        confidences: List of confidence scores (0.0-1.0)

    Returns:
        Plotly Figure
    """
    # Create bins for confidence levels
    bins = [0, 0.3, 0.5, 0.7, 0.9, 1.0]
    bin_labels = ["Very Low\n(<0.3)", "Low\n(0.3-0.5)", "Medium\n(0.5-0.7)", "High\n(0.7-0.9)", "Very High\n(>0.9)"]
    bin_colors = [
        CONFIDENCE_COLORS["very_low"],
        CONFIDENCE_COLORS["low"],
        CONFIDENCE_COLORS["medium"],
        CONFIDENCE_COLORS["high"],
        CONFIDENCE_COLORS["very_high"],
    ]

    # Fix: pd.cut returns tuple when retbins=True, unpack correctly
    binned_values, _ = pd.cut(confidences, bins=bins, retbins=True, labels=False, include_lowest=True)
    counts = binned_values.value_counts().sort_index()

    fig = go.Figure()

    for i, (label, color) in enumerate(zip(bin_labels, bin_colors)):
        count = counts.get(i, 0) if isinstance(counts, dict) else (counts[i] if i in counts.index else 0)
        fig.add_trace(
            go.Bar(
                x=[label],
                y=[count],
                marker_color=color,
                text=[f"{int(count)}<br>skills"],
                textposition="outside",
                hovertemplate=f"<b>{label}</b><br>Skills: {count}<extra></extra>",
                showlegend=False,
            )
        )

    fig.update_layout(
        title="Confidence Score Distribution",
        xaxis_title="Confidence Level",
        yaxis_title="Number of Skills",
        hovermode="x unified",
        barmode="group",
        height=400,
        template="plotly_white",
        margin=dict(l=50, r=50, t=80, b=50),
    )

    return fig


@st.cache_data
def create_category_breakdown(skill_categories: Dict[str, int]) -> go.Figure:
    """
    Create donut/pie chart of skills by category.

    Args:
        skill_categories: Dict mapping category names to skill counts

    Returns:
        Plotly Figure
    """
    categories = list(skill_categories.keys())
    counts = list(skill_categories.values())
    colors = [get_category_color(cat) for cat in categories]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=categories,
                values=counts,
                marker=dict(colors=colors),
                hole=0.4,
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title="Skills by Category",
        height=400,
        margin=dict(l=50, r=50, t=80, b=50),
    )

    return fig


@st.cache_data
def create_source_contribution(sources_data: Dict[str, int]) -> go.Figure:
    """
    Create horizontal bar chart of skills by data source.

    Args:
        sources_data: Dict mapping source names to skill counts

    Returns:
        Plotly Figure
    """
    sources = list(sources_data.keys())
    counts = list(sources_data.values())

    source_color_map = {
        "cv": "#3B82F6",
        "github": "#1F2937",
        "personal_statement": "#8B5CF6",
        "reference_letter": "#F97316",
    }

    colors = [source_color_map.get(src, COLOR_PALETTE["primary"]) for src in sources]

    fig = go.Figure(
        data=[
            go.Bar(
                y=sources,
                x=counts,
                orientation="h",
                marker=dict(color=colors),
                text=counts,
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Skills: %{x}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title="Skills by Data Source",
        xaxis_title="Number of Skills",
        yaxis_title="Data Source",
        height=300,
        margin=dict(l=150, r=50, t=80, b=50),
        template="plotly_white",
    )

    return fig


@st.cache_data
def create_detection_method_breakdown(methods_data: Dict[str, int]) -> go.Figure:
    """
    Create stacked bar chart of detection methods.

    Args:
        methods_data: Dict mapping method names (explicit, contextual, semantic) to counts

    Returns:
        Plotly Figure
    """
    methods = list(methods_data.keys())
    counts = list(methods_data.values())
    colors = [DETECTION_COLORS.get(method, COLOR_PALETTE["primary"]) for method in methods]

    fig = go.Figure()

    for method, count, color in zip(methods, counts, colors):
        fig.add_trace(
            go.Bar(
                x=[method],
                y=[count],
                marker_color=color,
                text=[f"{int(count)}<br>skills"],
                textposition="outside",
                name=method.capitalize(),
                hovertemplate=f"<b>{method.capitalize()}</b><br>Skills: {count}<extra></extra>",
                showlegend=False,
            )
        )

    fig.update_layout(
        title="Skill Detection Methods",
        yaxis_title="Number of Skills",
        height=350,
        barmode="stack",
        template="plotly_white",
        margin=dict(l=50, r=50, t=80, b=50),
    )

    return fig


@st.cache_data
def create_skill_evidence_heatmap(skill_sources: Dict[str, List[str]]) -> go.Figure:
    """
    Create heatmap of skills vs sources (evidence).

    Args:
        skill_sources: Dict mapping skill names to list of sources where found

    Returns:
        Plotly Figure
    """
    all_sources = set()
    for sources in skill_sources.values():
        all_sources.update(sources)

    all_sources = sorted(list(all_sources))
    skills = list(skill_sources.keys())

    # Create matrix
    z_data = []
    for skill in skills[:15]:  # Limit to top 15 for readability
        row = []
        for source in all_sources:
            row.append(1 if source in skill_sources[skill] else 0)
        z_data.append(row)

    fig = go.Figure(
        data=go.Heatmap(
            z=z_data,
            x=all_sources,
            y=skills,
            colorscale=["#ffffff", COLOR_PALETTE["primary"]],
            hovertemplate="<b>Skill: %{y}</b><br>Source: %{x}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Skill Evidence Matrix (Top 15 Skills)",
        xaxis_title="Data Source",
        yaxis_title="Skill",
        height=400,
        margin=dict(l=200, r=50, t=80, b=100),
    )

    return fig


@st.cache_data
def create_match_score_gauge(score: float, title: str = "Match Score") -> go.Figure:
    """
    Create gauge chart for match score.

    Args:
        score: Match score (0.0-1.0)
        title: Chart title

    Returns:
        Plotly Figure
    """
    percentage = score * 100

    if score >= 0.8:
        color = "#10B981"  # Green
        level = "Excellent"
    elif score >= 0.6:
        color = "#06B6D4"  # Cyan
        level = "Good"
    elif score >= 0.4:
        color = "#F59E0B"  # Amber
        level = "Fair"
    else:
        color = "#EF4444"  # Red
        level = "Poor"

    fig = go.Figure(
        data=[
            go.Indicator(
                mode="gauge+number",
                value=percentage,
                title={"text": title},
                number={"suffix": "%"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": color},
                    "steps": [
                        {"range": [0, 40], "color": "#FEE2E2"},
                        {"range": [40, 60], "color": "#FEF3C7"},
                        {"range": [60, 80], "color": "#DBEAFE"},
                        {"range": [80, 100], "color": "#DCFCE7"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 90,
                    },
                },
            )
        ]
    )

    fig.update_layout(
        height=350,
        margin=dict(l=50, r=50, t=80, b=50),
        annotations=[{
            "text": level,
            "x": 0.5,
            "y": 0.2,
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 16, "color": color},
            "xanchor": "center"
        }]
    )

    return fig


@st.cache_data
def create_skills_gap_waterfall(matched: int, required: int, preferred: int) -> go.Figure:
    """
    Create waterfall chart showing skills gap analysis.

    Args:
        matched: Number of matched skills
        required: Number of required skills
        preferred: Number of preferred skills

    Returns:
        Plotly Figure
    """
    missing_required = max(0, required - matched)
    missing_preferred = max(0, preferred - matched)

    fig = go.Figure(
        go.Waterfall(
            x=["Required", "Matched", "Gap (Required)", "Preferred", "Matched", "Gap (Preferred)"],
            y=[required, 0, -missing_required, preferred, 0, -missing_preferred],
            measure=["relative", "relative", "relative", "relative", "relative", "relative"],
            marker=dict(color=["#3B82F6", "#10B981", "#EF4444", "#8B5CF6", "#10B981", "#F59E0B"]),
            connector={"line": {"color": "#6B7280", "dash": "dash"}},
            hovertemplate="<b>%{x}</b><br>Skills: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Skills Gap Analysis",
        yaxis_title="Number of Skills",
        height=400,
        margin=dict(l=50, r=50, t=80, b=50),
        template="plotly_white",
    )

    return fig


@st.cache_data
def create_required_vs_preferred(
    matched_required: int,
    total_required: int,
    matched_preferred: int,
    total_preferred: int,
) -> go.Figure:
    """
    Create grouped bar chart for required vs preferred skills.

    Args:
        matched_required: Matched required skills
        total_required: Total required skills
        matched_preferred: Matched preferred skills
        total_preferred: Total preferred skills

    Returns:
        Plotly Figure
    """
    missing_required = total_required - matched_required
    missing_preferred = total_preferred - matched_preferred

    fig = go.Figure(
        data=[
            go.Bar(
                name="Matched",
                x=["Required", "Preferred"],
                y=[matched_required, matched_preferred],
                marker_color="#10B981",
                hovertemplate="<b>%{x}</b><br>Matched: %{y}<extra></extra>",
            ),
            go.Bar(
                name="Missing",
                x=["Required", "Preferred"],
                y=[missing_required, missing_preferred],
                marker_color="#EF4444",
                hovertemplate="<b>%{x}</b><br>Missing: %{y}<extra></extra>",
            ),
        ]
    )

    fig.update_layout(
        title="Required vs Preferred Skills Coverage",
        yaxis_title="Number of Skills",
        height=350,
        barmode="group",
        template="plotly_white",
        margin=dict(l=50, r=50, t=80, b=50),
    )

    return fig


@st.cache_data
def create_profile_completeness_gauge(completeness: float) -> go.Figure:
    """
    Create gauge for overall profile completeness.

    Args:
        completeness: Completeness score (0.0-1.0)

    Returns:
        Plotly Figure
    """
    percentage = completeness * 100

    fig = go.Figure(
        data=[
            go.Indicator(
                mode="gauge+number",
                value=percentage,
                title={"text": "Profile Completeness"},
                number={"suffix": "%"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": COLOR_PALETTE["secondary"]},
                    "steps": [
                        {"range": [0, 25], "color": "#FEE2E2"},
                        {"range": [25, 50], "color": "#FEF3C7"},
                        {"range": [50, 75], "color": "#DBEAFE"},
                        {"range": [75, 100], "color": "#DCFCE7"},
                    ],
                },
            )
        ]
    )

    fig.update_layout(
        height=350,
        margin=dict(l=50, r=50, t=80, b=50),
    )

    return fig


@st.cache_data
def create_skills_portfolio_bubble(
    category_data: Dict[str, Tuple[float, int]],
) -> go.Figure:
    """
    Create bubble chart of skills portfolio.

    Args:
        category_data: Dict mapping category to (avg_confidence, skill_count)

    Returns:
        Plotly Figure
    """
    categories = list(category_data.keys())
    confidences = [data[0] for data in category_data.values()]
    counts = [data[1] for data in category_data.values()]
    colors = [get_category_color(cat) for cat in categories]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=confidences,
                y=categories,
                mode="markers",
                marker=dict(
                    size=[count * 2 for count in counts],
                    color=colors,
                    opacity=0.7,
                    line=dict(width=1, color="white"),
                ),
                text=categories,
                hovertemplate="<b>%{text}</b><br>Avg Confidence: %{x:.2f}<br>Skills: %{marker.size}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title="Skills Portfolio Overview",
        xaxis_title="Average Confidence",
        yaxis_title="Skill Category",
        height=400,
        margin=dict(l=200, r=50, t=80, b=50),
        template="plotly_white",
    )

    return fig
