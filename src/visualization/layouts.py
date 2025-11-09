"""
Layout Components & Helpers

Provides grid layouts, card containers, and UI structure helpers.
"""

import streamlit as st
from typing import List, Dict, Optional, Callable
from .colors import COLOR_PALETTE, get_confidence_color, get_category_color


def create_skill_badge_html(
    skill_name: str,
    confidence: float,
    category: str = "",
) -> str:
    """
    Create HTML for a skill badge.

    Args:
        skill_name: Name of the skill
        confidence: Confidence score (0.0-1.0)
        category: Skill category (optional)

    Returns:
        HTML string for the badge
    """
    color = get_confidence_color(confidence)

    category_html = f" <small style='opacity: 0.7;'>• {category}</small>" if category else ""

    badge_html = f"""
    <span style="
        display: inline-block;
        padding: 0.5rem 0.75rem;
        margin: 0.25rem;
        border-radius: 20px;
        background-color: {color}20;
        border: 1px solid {color};
        color: {color};
        font-size: 0.875rem;
        font-weight: 500;
        white-space: nowrap;
    ">
        {skill_name} ({confidence:.2f}){category_html}
    </span>
    """

    return badge_html


def create_skills_grid(
    skills: List[Dict],
    columns: int = 4,
) -> None:
    """
    Create a responsive grid of skill badges.

    Args:
        skills: List of skill dicts with keys: name, confidence, category (optional)
        columns: Number of columns
    """
    cols = st.columns(columns)

    for idx, skill in enumerate(skills):
        with cols[idx % columns]:
            skill_html = create_skill_badge_html(
                skill_name=skill.get("name", "Unknown"),
                confidence=skill.get("confidence", 0.5),
                category=skill.get("category", ""),
            )
            st.markdown(skill_html, unsafe_allow_html=True)


def create_job_card(
    job_title: str,
    company: str = "",
    match_score: float = 0.0,
    matched_skills: int = 0,
    missing_skills: int = 0,
    description: str = "",
) -> None:
    """
    Create a job card with match information.

    Args:
        job_title: Job title
        company: Company name (optional)
        match_score: Match percentage (0.0-1.0)
        matched_skills: Number of matched skills
        missing_skills: Number of missing skills
        description: Job description
    """
    match_percentage = int(match_score * 100)

    if match_score >= 0.8:
        color = "#10B981"
    elif match_score >= 0.6:
        color = "#06B6D4"
    elif match_score >= 0.4:
        color = "#F59E0B"
    else:
        color = "#EF4444"

    company_html = f'<div style="font-size: 0.875rem; color: #6B7280; margin-bottom: 0.5rem;">{company}</div>' if company else ""
    desc_html = f'<div style="font-size: 0.875rem; color: #6B7280; margin-top: 1rem; line-height: 1.5;">{description}</div>' if description else ""

    card_html = f'<div style="padding: 1.5rem; border-radius: 12px; background: white; border: 1px solid #E5E7EB; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); height: 100%;"><div style="display: flex; justify-content: space-between; align-items: start;"><div><div style="font-size: 1.125rem; font-weight: 700; color: #0F172A;">{job_title}</div>{company_html}</div><div style="display: flex; align-items: center; justify-content: center; width: 60px; height: 60px; border-radius: 8px; background-color: {color}20; font-weight: 700; color: {color}; font-size: 1.5rem;">{match_percentage}%</div></div><div style="display: flex; gap: 1rem; margin-top: 1rem; font-size: 0.875rem;"><div style="color: #10B981; font-weight: 500;">Matched: {matched_skills}</div><div style="color: #EF4444; font-weight: 500;">Missing: {missing_skills}</div></div><div style="width: 100%; height: 4px; background-color: #E5E7EB; border-radius: 2px; margin-top: 1rem; overflow: hidden;"><div style="height: 100%; width: {match_percentage}%; background-color: {color}; border-radius: 2px;"></div></div>{desc_html}</div>'

    st.markdown(card_html, unsafe_allow_html=True)


def create_job_cards_grid(
    jobs: List[Dict],
    columns: int = 3,
) -> None:
    """
    Create a grid of job cards.

    Args:
        jobs: List of job dicts with keys:
              - title, company, match_score, matched_skills, missing_skills, description
        columns: Number of columns
    """
    cols = st.columns(columns)

    for idx, job in enumerate(jobs):
        with cols[idx % columns]:
            create_job_card(
                job_title=job.get("title", "Unknown"),
                company=job.get("company", ""),
                match_score=job.get("match_score", 0.0),
                matched_skills=job.get("matched_skills", 0),
                missing_skills=job.get("missing_skills", 0),
                description=job.get("description", ""),
            )


def create_category_section(
    category: str,
    skills: List[Dict],
    icon: str = "📂",
) -> None:
    """
    Create a collapsible section for a skill category.

    Args:
        category: Category name
        skills: List of skills in category
        icon: Icon emoji
    """
    category_color = get_category_color(category)

    with st.expander(f"{icon} {category.replace('_', ' ').title()} ({len(skills)} skills)", expanded=True):
        skill_badges_html = "".join([
            create_skill_badge_html(
                skill.get("name", ""),
                skill.get("confidence", 0.5),
                category,
            )
            for skill in skills
        ])

        st.markdown(skill_badges_html, unsafe_allow_html=True)


def create_metrics_row(
    metrics: List[Dict],
    columns: int = 4,
) -> None:
    """
    Create a row of metrics.

    Args:
        metrics: List of metric dicts
        columns: Number of columns
    """
    cols = st.columns(columns)

    for idx, metric in enumerate(metrics):
        with cols[idx % columns]:
            st.metric(
                label=metric.get("label", ""),
                value=metric.get("value", ""),
                delta=metric.get("delta"),
                help=metric.get("help"),
            )


def create_info_card(
    title: str,
    content: str,
    color: str = "primary",
    icon: str = "ℹ️",
) -> None:
    """
    Create an information card.

    Args:
        title: Card title
        content: Card content
        color: Color theme
        icon: Icon emoji
    """
    border_color = COLOR_PALETTE.get(color, COLOR_PALETTE["primary"])

    card_html = f"""
    <div style="
        padding: 1.5rem;
        border-radius: 12px;
        background: {border_color}10;
        border-left: 4px solid {border_color};
        border: 1px solid {border_color}30;
    ">
        <div style="
            font-size: 1rem;
            font-weight: 600;
            color: {border_color};
            margin-bottom: 0.5rem;
        ">
            {icon} {title}
        </div>
        <div style="
            font-size: 0.875rem;
            color: #374151;
            line-height: 1.5;
        ">
            {content}
        </div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)


def create_skill_detail_card(
    skill_name: str,
    confidence: float,
    category: str,
    sources: List[str],
    evidence: List[str],
) -> None:
    """
    Create a detailed card for a single skill.

    Args:
        skill_name: Skill name
        confidence: Confidence score
        category: Skill category
        sources: List of sources where detected
        evidence: List of evidence snippets
    """
    color = get_confidence_color(confidence)
    category_color = get_category_color(category)

    sources_html = "".join([
        f'<span style="display: inline-block; padding: 0.25rem 0.5rem; margin-right: 0.5rem; background-color: {category_color}20; border-radius: 4px; color: {category_color}; font-size: 0.75rem;">{source}</span>'
        for source in sources
    ])

    evidence_html = "".join([
        f'<div style="padding: 0.75rem; background-color: #F9FAFB; border-radius: 6px; margin-bottom: 0.5rem; font-size: 0.875rem; color: #374151;">• {evidence}</div>'
        for evidence in evidence
    ])

    card_html = f"""
    <div style="
        padding: 1.5rem;
        border-radius: 12px;
        background: white;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    ">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
            <div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #0F172A;">
                    {skill_name}
                </div>
                <div style="font-size: 0.875rem; color: #6B7280; margin-top: 0.25rem;">
                    {category.replace('_', ' ').title()}
                </div>
            </div>
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 0.5rem;
            ">
                <div style="
                    font-size: 1.875rem;
                    font-weight: 700;
                    color: {color};
                ">
                    {confidence:.0%}
                </div>
                <div style="font-size: 0.75rem; color: #6B7280;">
                    Confidence
                </div>
            </div>
        </div>

        <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #E5E7EB;">
            <div style="font-size: 0.875rem; color: #6B7280; margin-bottom: 0.5rem; font-weight: 500;">
                Detected in:
            </div>
            {sources_html}
        </div>

        <div>
            <div style="font-size: 0.875rem; color: #6B7280; margin-bottom: 0.5rem; font-weight: 500;">
                Evidence:
            </div>
            {evidence_html if evidence_html else '<div style="color: #9CA3AF; font-size: 0.875rem;">No evidence available</div>'}
        </div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)
