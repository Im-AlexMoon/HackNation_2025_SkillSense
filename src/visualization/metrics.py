"""
Metric Card Creation & Styling

Provides styled metric cards using streamlit-extras for enhanced UX.
"""

import streamlit as st
from typing import Optional
from .colors import COLOR_PALETTE, get_confidence_color, CUSTOM_CSS


def inject_metric_styles():
    """Inject custom CSS for metric cards"""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def create_styled_metric_card(
    label: str,
    value: str | int | float,
    delta: Optional[str] = None,
    icon: str = "📊",
    color: str = "primary",
    help_text: Optional[str] = None,
) -> None:
    """
    Create a styled metric card using custom HTML & CSS.

    Args:
        label: Metric label/title
        value: The metric value to display
        delta: Optional change indicator (e.g., "+5" or "-2")
        icon: Emoji icon to display
        color: Color theme ("primary", "secondary", "success", "warning", "error")
        help_text: Optional tooltip text
    """
    border_color = COLOR_PALETTE.get(color, COLOR_PALETTE["primary"])

    delta_html = ""
    if delta:
        delta_html = f'<span style="font-size: 0.9rem; color: #6B7280; margin-left: 0.5rem;">({delta})</span>'

    help_html = ""
    if help_text:
        help_html = f'<div style="font-size: 0.8rem; color: #9CA3AF; margin-top: 0.5rem;">{help_text}</div>'

    card_html = f"""
    <div style="
        padding: 1.5rem;
        border-radius: 12px;
        background: white;
        border-left: 4px solid {border_color};
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
    ">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <div style="font-size: 0.875rem; color: #6B7280; font-weight: 500; margin-bottom: 0.5rem;">
                    {icon} {label}
                </div>
                <div style="font-size: 1.875rem; font-weight: 700; color: #0F172A;">
                    {value}{delta_html}
                </div>
            </div>
        </div>
        {help_html}
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)


def create_metric_grid(metrics: list[dict], columns: int = 3) -> None:
    """
    Create a grid of metric cards.

    Args:
        metrics: List of metric dicts with keys:
                 - label: str
                 - value: str | int | float
                 - icon: str (emoji)
                 - color: str (optional, default "primary")
                 - delta: str (optional)
                 - help_text: str (optional)
        columns: Number of columns in grid
    """
    cols = st.columns(columns)

    for idx, metric in enumerate(metrics):
        with cols[idx % columns]:
            create_styled_metric_card(
                label=metric.get("label", ""),
                value=metric.get("value", "N/A"),
                delta=metric.get("delta"),
                icon=metric.get("icon", "📊"),
                color=metric.get("color", "primary"),
                help_text=metric.get("help_text"),
            )


def create_confidence_metric_card(
    label: str,
    value: float,
    help_text: Optional[str] = None,
) -> None:
    """
    Create a metric card with color based on confidence score.

    Args:
        label: Metric label
        value: Confidence value (0.0-1.0)
        help_text: Optional help text
    """
    color = get_confidence_color(value)
    percentage = f"{value * 100:.1f}%"

    card_html = f"""
    <div style="
        padding: 1.5rem;
        border-radius: 12px;
        background: white;
        border-left: 4px solid {color};
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
    ">
        <div style="font-size: 0.875rem; color: #6B7280; font-weight: 500; margin-bottom: 0.75rem;">
            {label}
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="
                flex: 1;
                height: 8px;
                background-color: #E5E7EB;
                border-radius: 4px;
                overflow: hidden;
            ">
                <div style="
                    height: 100%;
                    width: {value * 100}%;
                    background-color: {color};
                    border-radius: 4px;
                    transition: width 0.3s ease;
                "></div>
            </div>
            <div style="
                font-size: 1.5rem;
                font-weight: 700;
                color: {color};
                min-width: 60px;
                text-align: right;
            ">
                {percentage}
            </div>
        </div>
        {f'<div style="font-size: 0.8rem; color: #9CA3AF; margin-top: 0.5rem;">{help_text}</div>' if help_text else ''}
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)


def create_stat_card(
    title: str,
    stat: str | int,
    description: str = "",
    color: str = "primary",
) -> None:
    """
    Create a simple stat card.

    Args:
        title: Card title
        stat: The statistic to display
        description: Optional description text
        color: Color theme
    """
    border_color = COLOR_PALETTE.get(color, COLOR_PALETTE["primary"])

    desc_html = ""
    if description:
        desc_html = f'<div style="font-size: 0.875rem; color: #6B7280; margin-top: 0.5rem;">{description}</div>'

    card_html = f"""
    <div style="
        padding: 1.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
        border: 2px solid {border_color};
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    ">
        <div style="font-size: 0.875rem; color: {border_color}; font-weight: 600; margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;">
            {title}
        </div>
        <div style="font-size: 2rem; font-weight: 700; color: #0F172A;">
            {stat}
        </div>
        {desc_html}
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)
