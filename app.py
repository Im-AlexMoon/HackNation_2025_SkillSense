"""
SkillSense - Streamlit Dashboard
AI-powered skill extraction and career matching platform
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
import json
import os
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # If dotenv fails, try manual loading
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from profile_generation.profile_builder import ProfileBuilder
from analysis.job_matcher import JobMatcher
from rag.rag_system import RAGSystem
from rag.prompts import QUICK_QUESTIONS


# Page configuration
st.set_page_config(
    page_title="SkillSense - Unlock Your Hidden Potential",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .skill-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 1rem;
        font-size: 0.9rem;
    }
    .skill-high {
        background-color: #28a745;
        color: white;
    }
    .skill-medium {
        background-color: #ffc107;
        color: black;
    }
    .skill-low {
        background-color: #dc3545;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'profile' not in st.session_state:
        st.session_state.profile = None
    if 'profile_builder' not in st.session_state:
        st.session_state.profile_builder = ProfileBuilder()
    if 'job_matcher' not in st.session_state:
        st.session_state.job_matcher = JobMatcher()


def render_header():
    """Render application header"""
    st.markdown('<div class="main-header">🎯 SkillSense</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Unlock Your Hidden Potential with AI-Powered Skill Analysis</div>', unsafe_allow_html=True)


def render_data_input_page():
    """Render data input page - supports simultaneous multi-source input with preview cards"""
    st.header("📊 Data Input & Source Collection")
    st.markdown("Provide information from **multiple sources** for comprehensive skill analysis. The more sources you provide, the more accurate your skill profile!")

    # Initialize session state for collected inputs
    if 'collected_inputs' not in st.session_state:
        st.session_state.collected_inputs = {}

    # Dictionary to accumulate all inputs from this render
    inputs = {}

    # Info card about multi-source benefits
    from src.visualization import create_info_card
    create_info_card(
        title="Why Multiple Sources Matter",
        content="Combining CV, GitHub, personal statement, and references provides a holistic view of your skills. Each source reveals different aspects of your expertise.",
        color="secondary",
        icon="💡"
    )

    st.markdown("---")
    st.subheader("🎯 Select Your Data Sources")

    # Progress indicator
    col_progress1, col_progress2, col_progress3, col_progress4 = st.columns(4)

    # Section 1: CV Upload (supports multiple files)
    st.subheader("📄 CV Upload")
    cv_info = st.container()

    cv_files = st.file_uploader(
        "Upload one or more CVs in PDF format",
        type=['pdf'],
        accept_multiple_files=True,
        key="cv_uploader"
    )

    cv_preview = ""
    if cv_files:
        import uuid
        cv_paths = []
        for idx, cv_file in enumerate(cv_files):
            # Generate unique temp file name
            temp_path = Path(f"temp_cv_{uuid.uuid4().hex[:8]}.pdf")
            with open(temp_path, 'wb') as f:
                f.write(cv_file.getbuffer())
            cv_paths.append(str(temp_path))

        inputs['cv_paths'] = cv_paths
        cv_preview = f"✅ {len(cv_paths)} CV file(s) uploaded"

        with col_progress1:
            st.metric("CVs", len(cv_paths), delta=None)

    st.markdown("---")

    # Section 2: GitHub Connection
    st.subheader("💻 GitHub Profile")
    github_username = st.text_input(
        "GitHub Username (optional)",
        placeholder="e.g., octocat",
        key="github_input"
    )

    github_preview = ""
    if github_username:
        inputs['github_username'] = github_username
        github_preview = f"✅ Connected to github.com/{github_username}"

        with col_progress2:
            st.metric("GitHub", "Connected", delta=None)

    st.markdown("---")

    # Section 3: Text Input
    st.subheader("✍️ Written Background")

    col_statement, col_reference = st.columns(2)

    personal_statement = ""
    reference_letter = ""

    with col_statement:
        st.markdown("**Personal Statement**")
        personal_statement = st.text_area(
            "Describe your background, skills, and career goals",
            placeholder="Share your professional journey, key achievements, and goals...",
            height=150,
            key="statement_input",
            label_visibility="collapsed"
        )

    with col_reference:
        st.markdown("**Reference Letter (Optional)**")
        reference_letter = st.text_area(
            "Reference from a colleague or mentor",
            placeholder="Paste a reference letter or recommendation from someone who knows your work...",
            height=150,
            key="reference_input",
            label_visibility="collapsed"
        )

    if personal_statement:
        inputs['personal_statement'] = personal_statement
        with col_progress3:
            st.metric("Statement", "Added", delta=None)

    if reference_letter:
        inputs['reference_letter'] = reference_letter
        with col_progress4:
            st.metric("Reference", "Added", delta=None)

    st.markdown("---")

    # Display data collection summary with preview cards
    if inputs:
        st.subheader("📋 Data Collection Summary")

        # Create preview cards in a responsive grid
        preview_cols = st.columns(min(len(inputs), 4))

        source_idx = 0
        if 'cv_paths' in inputs and source_idx < len(preview_cols):
            with preview_cols[source_idx]:
                cv_card = f"""
                <div style="
                    padding: 1.5rem;
                    border-radius: 12px;
                    background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
                    border: 2px solid #3B82F6;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
                    text-align: center;
                ">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📄</div>
                    <div style="font-weight: 700; color: #1E40AF; margin-bottom: 0.5rem;">CV Document(s)</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #3B82F6; margin-bottom: 0.5rem;">{len(inputs['cv_paths'])}</div>
                    <div style="font-size: 0.875rem; color: #1E40AF;">files uploaded</div>
                </div>
                """
                st.markdown(cv_card, unsafe_allow_html=True)
            source_idx += 1

        if 'github_username' in inputs and source_idx < len(preview_cols):
            with preview_cols[source_idx]:
                gh_card = f"""
                <div style="
                    padding: 1.5rem;
                    border-radius: 12px;
                    background: linear-gradient(135deg, #F3F4F6 0%, #E5E7EB 100%);
                    border: 2px solid #374151;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
                    text-align: center;
                ">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">💻</div>
                    <div style="font-weight: 700; color: #111827; margin-bottom: 0.5rem;">GitHub Profile</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #374151; margin-bottom: 0.5rem; word-break: break-all;">{inputs['github_username']}</div>
                    <div style="font-size: 0.875rem; color: #374151;">connected</div>
                </div>
                """
                st.markdown(gh_card, unsafe_allow_html=True)
            source_idx += 1

        if 'personal_statement' in inputs and source_idx < len(preview_cols):
            with preview_cols[source_idx]:
                stmt_length = len(inputs['personal_statement'].split())
                stmt_card = f"""
                <div style="
                    padding: 1.5rem;
                    border-radius: 12px;
                    background: linear-gradient(135deg, #E0E7FF 0%, #DDD6FE 100%);
                    border: 2px solid #6366F1;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
                    text-align: center;
                ">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">✍️</div>
                    <div style="font-weight: 700; color: #3730A3; margin-bottom: 0.5rem;">Personal Statement</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #6366F1; margin-bottom: 0.5rem;">{stmt_length}</div>
                    <div style="font-size: 0.875rem; color: #3730A3;">words added</div>
                </div>
                """
                st.markdown(stmt_card, unsafe_allow_html=True)
            source_idx += 1

        if 'reference_letter' in inputs and source_idx < len(preview_cols):
            with preview_cols[source_idx]:
                ref_length = len(inputs['reference_letter'].split())
                ref_card = f"""
                <div style="
                    padding: 1.5rem;
                    border-radius: 12px;
                    background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
                    border: 2px solid #EF4444;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
                    text-align: center;
                ">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📋</div>
                    <div style="font-weight: 700; color: #7F1D1D; margin-bottom: 0.5rem;">Reference Letter</div>
                    <div style="font-size: 2rem; font-weight: 700; color: #EF4444; margin-bottom: 0.5rem;">{ref_length}</div>
                    <div style="font-size: 0.875rem; color: #7F1D1D;">words added</div>
                </div>
                """
                st.markdown(ref_card, unsafe_allow_html=True)

        st.markdown("---")

        # Data quality indicator
        data_quality_score = 0
        quality_indicators = []

        if 'cv_paths' in inputs:
            data_quality_score += 0.3
            quality_indicators.append("CV detected")
        if 'github_username' in inputs:
            data_quality_score += 0.25
            quality_indicators.append("GitHub connected")
        if 'personal_statement' in inputs:
            data_quality_score += 0.25
            quality_indicators.append("Personal context added")
        if 'reference_letter' in inputs:
            data_quality_score += 0.2
            quality_indicators.append("Reference included")

        st.subheader("📊 Data Quality Score")

        col_qual1, col_qual2, col_qual3 = st.columns([2, 1, 1])

        with col_qual1:
            # Quality progress bar
            qual_percent = int(data_quality_score * 100)
            quality_html = f"""
            <div style="
                width: 100%;
                height: 30px;
                background-color: #E5E7EB;
                border-radius: 15px;
                overflow: hidden;
                border: 2px solid #D1D5DB;
            ">
                <div style="
                    height: 100%;
                    width: {qual_percent}%;
                    background: linear-gradient(90deg, #3B82F6 0%, #06B6D4 100%);
                    border-radius: 13px;
                    display: flex;
                    align-items: center;
                    justify-content: flex-end;
                    padding-right: 1rem;
                    color: white;
                    font-weight: 700;
                    font-size: 0.875rem;
                ">
                    {qual_percent}%
                </div>
            </div>
            """
            st.markdown(quality_html, unsafe_allow_html=True)

        with col_qual2:
            st.metric("Sources", len(inputs))

        with col_qual3:
            st.metric("Completeness", f"{qual_percent}%")

        # Quality indicators
        st.markdown("**Data Indicators:**")
        for indicator in quality_indicators:
            st.markdown(f"✅ {indicator}")

        if data_quality_score >= 0.8:
            st.info("🎯 Excellent data collection! Ready for comprehensive skill analysis.", icon="ℹ️")

        return inputs

    else:
        # Prompt to add data
        st.info("👆 Start by adding at least one data source above to get your skill analysis!", icon="ℹ️")

    return None


def build_profile_from_inputs(inputs: dict):
    """Build profile from user inputs - supports multi-source simultaneous processing"""
    # Display processing progress
    sources_to_process = []
    if inputs.get('cv_paths'):
        sources_to_process.append(f"{len(inputs['cv_paths'])} CV file(s)")
    if inputs.get('github_username'):
        sources_to_process.append("GitHub")
    if inputs.get('personal_statement'):
        sources_to_process.append("Personal Statement")
    if inputs.get('reference_letter'):
        sources_to_process.append("Reference Letter")

    progress_text = f"Processing: {', '.join(sources_to_process)}"

    with st.spinner(f"🔍 {progress_text}..."):
        try:
            # Build profile with all sources
            profile = st.session_state.profile_builder.build_profile(
                name=inputs.get('name', 'User'),
                cv_paths=inputs.get('cv_paths'),  # Now supports multiple CVs
                github_username=inputs.get('github_username'),
                personal_statement=inputs.get('personal_statement'),
                reference_letter=inputs.get('reference_letter')
            )
            st.session_state.profile = profile

            # Show success with source breakdown
            st.success("Profile analysis complete!")

            # Display which sources contributed
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Skills", len(profile.skills))
            with col2:
                st.metric("Data Sources", len(profile.data_sources))
            with col3:
                sources_list = ', '.join(profile.data_sources)
                st.metric("Sources Used", sources_list)

            return True
        except Exception as e:
            st.error(f"Error building profile: {str(e)}")
            import traceback
            st.error(f"Details: {traceback.format_exc()}")
            return False


def render_skill_profile_page():
    """Render skill profile visualization page with advanced charts and filters"""
    if st.session_state.profile is None:
        st.warning("⚠️ Please provide your data first in the Data Input page")
        return

    profile = st.session_state.profile

    st.header("🎓 Your Skill Profile")

    # Profile Summary Card
    from src.visualization import create_info_card
    create_info_card(
        title="Profile Overview",
        content=profile.summary,
        color="secondary",
        icon="📊"
    )

    st.markdown("---")

    # Metrics Row - Using styled metric cards
    from src.visualization import create_metric_grid
    high_confidence = len([s for s in profile.skills if s.final_confidence >= 0.75])
    medium_confidence = len([s for s in profile.skills if 0.5 <= s.final_confidence < 0.75])
    low_confidence = len([s for s in profile.skills if s.final_confidence < 0.5])

    metrics = [
        {"label": "Total Skills", "value": len(profile.skills), "icon": "📊", "color": "primary"},
        {"label": "High Confidence", "value": high_confidence, "icon": "🟢", "color": "success"},
        {"label": "Medium Confidence", "value": medium_confidence, "icon": "🟡", "color": "warning"},
        {"label": "Low Confidence", "value": low_confidence, "icon": "🔴", "color": "error"},
        {"label": "Data Sources", "value": len(profile.data_sources), "icon": "📁", "color": "secondary"},
        {"label": "Evidence Trails", "value": sum(len(s.evidence) for s in profile.skills), "icon": "🔍", "color": "info"},
    ]

    create_metric_grid(metrics, columns=3)

    st.markdown("---")

    # Interactive Filters
    st.subheader("🎯 Filter & Explore Skills")

    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        confidence_min = st.slider(
            "Minimum Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1,
            key="skill_confidence_filter"
        )

    with col_filter2:
        categories = ["All"] + sorted([cat.replace('_', ' ').title() for cat in profile.skill_categories.keys()])
        selected_category = st.selectbox(
            "Filter by Category",
            categories,
            key="skill_category_filter"
        )

    with col_filter3:
        # Extract unique sources from all skills
        all_sources = set()
        for skill in profile.skills:
            if hasattr(skill, 'sources'):
                all_sources.update(skill.sources)
        sources_list = ["All"] + sorted(list(all_sources)) if all_sources else ["All"]

        selected_source = st.selectbox(
            "Filter by Source",
            sources_list,
            key="skill_source_filter"
        )

    st.markdown("---")

    # Top Skills with Radar Chart
    st.subheader("🏆 Top Skills Overview")

    col_charts1, col_charts2 = st.columns([1.5, 1])

    with col_charts1:
        if profile.top_skills:
            from src.visualization import create_confidence_distribution
            filtered_skills = [s for s in profile.skills if s.final_confidence >= confidence_min]
            confidences = [s.final_confidence for s in filtered_skills]

            if confidences:
                fig_dist = create_confidence_distribution(confidences)
                st.plotly_chart(fig_dist, use_container_width=True)

    with col_charts2:
        if profile.top_skills:
            from src.visualization import create_category_breakdown
            category_counts = {}
            for category, skills in profile.skill_categories.items():
                filtered = [s for s in skills if s.final_confidence >= confidence_min]
                if filtered:
                    category_counts[category.replace('_', ' ').title()] = len(filtered)

            if category_counts:
                fig_category = create_category_breakdown(category_counts)
                st.plotly_chart(fig_category, use_container_width=True)

    st.markdown("---")

    # Source Contribution & Detection Methods
    col_charts3, col_charts4 = st.columns(2)

    with col_charts3:
        from src.visualization import create_source_contribution
        source_counts = {}
        for skill in profile.skills:
            if skill.final_confidence >= confidence_min:
                for source in skill.sources:
                    source_counts[source] = source_counts.get(source, 0) + 1

        if source_counts:
            fig_sources = create_source_contribution(source_counts)
            st.plotly_chart(fig_sources, use_container_width=True)

    with col_charts4:
        from src.visualization import create_detection_method_breakdown
        method_counts = {"explicit": 0, "contextual": 0, "semantic": 0}
        for skill in profile.skills:
            if skill.final_confidence >= confidence_min:
                for method_key in method_counts:
                    if method_key in skill.confidence_breakdown:
                        method_counts[method_key] += 1

        if any(method_counts.values()):
            fig_methods = create_detection_method_breakdown(method_counts)
            st.plotly_chart(fig_methods, use_container_width=True)

    st.markdown("---")

    # Detailed Skills by Category with Badges
    st.subheader("📚 Skills by Category")

    for category, skills in profile.skill_categories.items():
        # Apply filters
        filtered_skills = [
            s for s in skills
            if s.final_confidence >= confidence_min
            and (selected_category == "All" or category.replace('_', ' ').title() == selected_category)
        ]

        if filtered_skills:
            from src.visualization import create_category_section, create_skill_badge_html

            sorted_skills = sorted(filtered_skills, key=lambda x: x.final_confidence, reverse=True)

            with st.expander(
                f"{category.replace('_', ' ').title()} ({len(sorted_skills)} skills)",
                expanded=False
            ):
                # Display skills as badges
                skill_badges = "".join([
                    create_skill_badge_html(
                        skill.skill_name,
                        skill.final_confidence,
                        category.replace('_', ' ').title()
                    )
                    for skill in sorted_skills[:20]
                ])
                st.markdown(skill_badges, unsafe_allow_html=True)

    st.markdown("---")

    # Detailed Evidence View
    st.subheader("🔍 Detailed Evidence & Sources")

    from src.visualization import create_skill_detail_card

    for skill in profile.top_skills[:15]:
        if skill.final_confidence >= confidence_min:
            create_skill_detail_card(
                skill_name=skill.skill_name,
                confidence=skill.final_confidence,
                category="Unknown",
                sources=skill.sources,
                evidence=skill.evidence[:3]
            )
            st.markdown("")  # Spacing


def render_job_matching_page():
    """Render job matching page with advanced visualizations and analysis"""
    if st.session_state.profile is None:
        st.warning("⚠️ Please build your profile first")
        return

    profile = st.session_state.profile
    matcher = st.session_state.job_matcher

    st.header("💼 Job Matching & Career Recommendations")

    # Get job matches
    with st.spinner("🔎 Finding best job matches..."):
        matches = matcher.match_profile_to_jobs(profile.skills, top_n=10)

    # Metrics summary
    from src.visualization import create_metric_grid
    avg_match_score = sum(m.match_score for m in matches) / len(matches) if matches else 0
    perfect_matches = len([m for m in matches if m.match_score >= 0.8])

    metrics = [
        {"label": "Best Match Score", "value": f"{max(m.match_score for m in matches) * 100:.0f}%" if matches else "N/A", "icon": "🏆", "color": "success"},
        {"label": "Average Match", "value": f"{avg_match_score * 100:.0f}%", "icon": "📊", "color": "primary"},
        {"label": "Excellent Matches (80%+)", "value": perfect_matches, "icon": "🎯", "color": "secondary"},
    ]

    create_metric_grid(metrics, columns=3)

    st.markdown("---")

    # Match Score Threshold Filter
    st.subheader("🎯 Explore Opportunities")

    col_filter1, col_filter2 = st.columns(2)

    with col_filter1:
        match_threshold = st.slider(
            "Minimum Match Score",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            key="job_match_threshold"
        )

    with col_filter2:
        sort_by = st.selectbox(
            "Sort By",
            ["Match Score (Highest)", "Match Score (Lowest)", "Alphabetical"],
            key="job_sort"
        )

    # Filter and sort matches
    filtered_matches = [m for m in matches if m.match_score >= match_threshold]

    if sort_by == "Alphabetical":
        filtered_matches = sorted(filtered_matches, key=lambda x: x.job_title)
    elif sort_by == "Match Score (Lowest)":
        filtered_matches = sorted(filtered_matches, key=lambda x: x.match_score)

    st.markdown("---")

    # Job Cards Grid
    st.subheader(f"💼 Top Opportunities ({len(filtered_matches)} matches)")

    if filtered_matches:
        from src.visualization import create_job_cards_grid

        job_data = []
        for match in filtered_matches[:9]:  # Show top 9 in grid
            job_data.append({
                "title": match.job_title,
                "company": "",
                "match_score": match.match_score,
                "matched_skills": len(match.matched_skills),
                "missing_skills": len(match.missing_required) + len(match.missing_preferred),
                "description": match.recommendation[:100] + "..." if match.recommendation else ""
            })

        create_job_cards_grid(job_data, columns=3)
    else:
        st.info("No matches found with your selected criteria. Try lowering the match threshold.")

    st.markdown("---")

    # Detailed Job Analysis
    st.subheader("📊 Detailed Analysis & Visualizations")

    if matches:
        # Create tabs for different analyses
        tab1, tab2, tab3 = st.tabs(["Match Scores", "Skill Gaps", "Opportunity Analysis"])

        with tab1:
            st.markdown("#### Match Score Gauges")
            # Show gauges for top 3-5 jobs
            cols = st.columns(min(3, len(matches[:3])))
            for idx, (col, match) in enumerate(zip(cols, matches[:3])):
                with col:
                    from src.visualization import create_match_score_gauge
                    fig_gauge = create_match_score_gauge(match.match_score, match.job_title)
                    st.plotly_chart(fig_gauge, use_container_width=True)

        with tab2:
            # Gap Analysis Charts
            st.markdown("#### Skills Gap Analysis")

            target_job = st.selectbox(
                "Select a role for detailed gap analysis:",
                [match.job_title for match in matches[:10]],
                key="gap_analysis_job"
            )

            if target_job:
                target_match = next((m for m in matches if m.job_title == target_job), None)

                if target_match:
                    gap_analysis = matcher.identify_skill_gaps(profile.skills, target_job)

                    if 'error' not in gap_analysis:
                        # Show readiness gauge
                        col_gauge, col_info = st.columns([1, 1.5])

                        with col_gauge:
                            from src.visualization import create_profile_completeness_gauge
                            fig_readiness = create_profile_completeness_gauge(gap_analysis.get('readiness_score', 0))
                            st.plotly_chart(fig_readiness, use_container_width=True)

                        with col_info:
                            st.markdown("#### Readiness Summary")
                            readiness = gap_analysis.get('readiness_score', 0)
                            if readiness >= 0.8:
                                st.success(f"Excellent readiness: {readiness*100:.0f}%")
                            elif readiness >= 0.6:
                                st.info(f"Good readiness: {readiness*100:.0f}%")
                            elif readiness >= 0.4:
                                st.warning(f"Fair readiness: {readiness*100:.0f}%")
                            else:
                                st.error(f"Development needed: {readiness*100:.0f}%")

                        # Gap visualization
                        col_waterfall, col_comparison = st.columns(2)

                        with col_waterfall:
                            from src.visualization import create_skills_gap_waterfall
                            fig_waterfall = create_skills_gap_waterfall(
                                matched=len(target_match.matched_skills),
                                required=len(target_match.matched_skills) + len(target_match.missing_required),
                                preferred=len(target_match.missing_preferred)
                            )
                            st.plotly_chart(fig_waterfall, use_container_width=True)

                        with col_comparison:
                            from src.visualization import create_required_vs_preferred
                            fig_req_pref = create_required_vs_preferred(
                                matched_required=len([s for s in target_match.matched_skills if s not in target_match.missing_preferred]),
                                total_required=len(target_match.matched_skills) + len(target_match.missing_required),
                                matched_preferred=len([s for s in target_match.matched_skills if s in target_match.missing_preferred]),
                                total_preferred=len(target_match.missing_preferred)
                            )
                            st.plotly_chart(fig_req_pref, use_container_width=True)

                        # Skill gaps breakdown
                        st.markdown("#### Skills to Develop")

                        gap_cols = st.columns(2)

                        with gap_cols[0]:
                            if gap_analysis.get('gaps', {}).get('critical'):
                                st.warning("**🔴 Critical Skills (Must Have):**")
                                for skill in gap_analysis['gaps']['critical'][:5]:
                                    st.write(f"- {skill}")

                        with gap_cols[1]:
                            if gap_analysis.get('gaps', {}).get('preferred'):
                                st.info("**🟡 Preferred Skills (Nice to Have):**")
                                for skill in gap_analysis['gaps']['preferred'][:5]:
                                    st.write(f"- {skill}")

                        # Learning recommendations
                        if gap_analysis.get('recommendations'):
                            st.markdown("#### Learning Path")
                            st.success("**📚 Recommended Learning Sequence:**")
                            for i, rec in enumerate(gap_analysis['recommendations'][:5], 1):
                                priority = rec.get('priority', 'Medium')
                                action = rec.get('action', '')
                                color = "🔴" if priority == "Critical" else "🟡" if priority == "High" else "🟢"
                                st.write(f"{i}. {color} [{priority}] {action}")

        with tab3:
            st.markdown("#### Opportunity Analysis")

            # Show comparison across multiple jobs
            if len(matches) > 1:
                from src.visualization import create_skills_portfolio_bubble

                # Prepare data for bubble chart
                category_data = {}
                for match in matches[:6]:
                    category_data[match.job_title[:20]] = (
                        match.match_score,
                        len(match.matched_skills)
                    )

                if category_data:
                    fig_bubble = create_skills_portfolio_bubble(category_data)
                    st.plotly_chart(fig_bubble, use_container_width=True)

            # Summary statistics
            st.markdown("#### Career Path Statistics")

            stat_cols = st.columns(3)

            with stat_cols[0]:
                st.metric("Total Opportunities", len(matches))

            with stat_cols[1]:
                avg_gap = sum(len(m.missing_required) + len(m.missing_preferred) for m in matches) / len(matches) if matches else 0
                st.metric("Avg Skills to Develop", f"{avg_gap:.1f}")

            with stat_cols[2]:
                total_unique_gaps = len(set(
                    skill
                    for match in matches
                    for skill in match.missing_required + match.missing_preferred
                ))
                st.metric("Unique Skills Needed", total_unique_gaps)


def create_radar_chart(skills):
    """Create radar chart for top skills"""
    skill_names = [s.skill_name[:20] for s in skills]  # Truncate long names
    confidences = [s.final_confidence for s in skills]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=confidences,
        theta=skill_names,
        fill='toself',
        name='Confidence Level'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False,
        title="Top Skills Confidence Radar"
    )

    return fig


def render_employer_qa_page():
    """Render Employer Q&A page with RAG system, annotated text, and source relevance charts"""
    if st.session_state.profile is None:
        st.warning("⚠️ Please build a candidate profile first in the Data Input page")
        return

    st.header("💬 Employer Q&A - Ask About This Candidate")
    st.markdown("Ask natural language questions about the candidate's skills, experience, and qualifications")

    # Display candidate overview cards at top
    from src.visualization import create_info_card, create_metric_grid

    profile = st.session_state.profile

    # Quick overview metrics
    high_confidence_skills = len([s for s in profile.skills if s.final_confidence >= 0.75])

    metrics = [
        {"label": "Candidate Name", "value": profile.name or "Unknown", "icon": "👤", "color": "primary"},
        {"label": "Total Skills", "value": len(profile.skills), "icon": "📊", "color": "secondary"},
        {"label": "High Confidence", "value": high_confidence_skills, "icon": "⭐", "color": "success"},
        {"label": "Data Sources", "value": len(profile.data_sources), "icon": "📁", "color": "secondary"},
    ]

    create_metric_grid(metrics, columns=4)

    st.markdown("---")

    # Sidebar settings
    with st.sidebar:
        st.subheader("🔧 RAG Settings")

        # LLM Provider selection
        llm_provider = st.selectbox(
            "LLM Provider",
            ["gemini", "openai", "anthropic"],
            help="Gemini is free tier, OpenAI and Anthropic require API keys"
        )

        # API Key input (optional)
        with st.expander("⚙️ API Configuration"):
            api_key_input = st.text_input(
                f"{llm_provider.upper()} API Key",
                type="password",
                help=f"Optional: Enter your {llm_provider.upper()} API key"
            )

        # Display options
        show_evidence = st.checkbox("Show Evidence Citations", value=True)
        show_similarity = st.checkbox("Show Similarity Scores", value=True)
        show_source_analysis = st.checkbox("Show Source Relevance Chart", value=True)

        st.divider()

        # Profile info
        st.subheader("📊 Candidate Info")
        st.write(f"**Name:** {st.session_state.profile.name or 'Unknown'}")
        st.metric("Total Skills", len(st.session_state.profile.skills))
        st.metric("Data Sources", len(st.session_state.profile.data_sources))

        # Reset conversation button
        if st.button("🔄 Reset Conversation"):
            if 'rag_system' in st.session_state:
                st.session_state.rag_system.reset_conversation()
            if 'chat_messages' in st.session_state:
                st.session_state.chat_messages = []
            st.rerun()

    # Initialize RAG system
    if 'rag_system' not in st.session_state or st.session_state.get('rag_provider') != llm_provider:
        with st.spinner(f"🔍 Initializing RAG system with {llm_provider}..."):
            try:
                api_key = api_key_input if api_key_input else None
                st.session_state.rag_system = RAGSystem(
                    st.session_state.profile,
                    llm_provider=llm_provider,
                    api_key=api_key
                )
                st.session_state.rag_provider = llm_provider
                # Clear chat history when switching providers
                st.session_state.chat_messages = []
                st.success(f"✅ RAG system ready with {llm_provider}")
            except Exception as e:
                st.error(f"❌ Error initializing RAG system: {str(e)}")
                st.info("💡 Tip: For Gemini, you may not need an API key. For OpenAI/Anthropic, enter your API key in the sidebar.")
                return

    # Initialize chat history
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []

    # Display chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # Show enhanced evidence if available and enabled
            if show_evidence and msg.get("sources") and msg["role"] == "assistant":
                with st.expander("📚 View Evidence & Sources"):
                    sources = msg["sources"]

                    # Source relevance analysis chart
                    if show_source_analysis and len(sources) > 0:
                        st.subheader("📊 Source Relevance Analysis")

                        import plotly.graph_objects as go
                        source_types = [src['type'].replace('_', ' ').title() for src in sources]
                        similarities = [src.get('similarity', 0) for src in sources]

                        fig_sources = go.Figure(
                            data=[
                                go.Bar(
                                    y=source_types,
                                    x=similarities,
                                    orientation='h',
                                    marker=dict(
                                        color=similarities,
                                        colorscale='RdYlGn',
                                        cmin=0,
                                        cmax=1,
                                        showscale=True,
                                        colorbar=dict(title="Relevance")
                                    ),
                                    text=[f"{sim:.2f}" for sim in similarities],
                                    textposition='outside',
                                    hovertemplate="<b>%{y}</b><br>Relevance: %{x:.2f}<extra></extra>"
                                )
                            ]
                        )

                        fig_sources.update_layout(
                            title="Evidence Source Relevance Scores",
                            xaxis_title="Relevance Score",
                            yaxis_title="Source Type",
                            height=250,
                            margin=dict(l=150, r=50, t=80, b=50),
                            template="plotly_white"
                        )

                        st.plotly_chart(fig_sources, use_container_width=True)
                        st.markdown("---")

                    # Detailed evidence cards
                    st.subheader("💡 Evidence Details")
                    for i, src in enumerate(sources, 1):
                        source_type = src['type'].replace('_', ' ').title()
                        similarity_score = src.get('similarity', 0)

                        if similarity_score >= 0.8:
                            color_hex = "#10B981"
                            relevance_label = "High"
                        elif similarity_score >= 0.5:
                            color_hex = "#F59E0B"
                            relevance_label = "Medium"
                        else:
                            color_hex = "#EF4444"
                            relevance_label = "Low"

                        source_card = f"""
                        <div style="
                            padding: 1.5rem;
                            border-radius: 12px;
                            background: white;
                            border-left: 4px solid {color_hex};
                            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                            border: 1px solid #E5E7EB;
                            margin-bottom: 1rem;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                                <div style="font-weight: 700; color: #0F172A; font-size: 1.125rem;">
                                    [{i}] {source_type}
                                </div>
                                <div style="
                                    display: inline-block;
                                    padding: 0.25rem 0.75rem;
                                    background-color: {color_hex}20;
                                    border-radius: 20px;
                                    color: {color_hex};
                                    font-weight: 600;
                                    font-size: 0.875rem;
                                ">
                                    {relevance_label} Relevance
                                </div>
                            </div>

                            <div style="
                                padding: 1rem;
                                background-color: #F9FAFB;
                                border-radius: 8px;
                                color: #374151;
                                font-size: 0.95rem;
                                line-height: 1.6;
                                margin-bottom: 0.75rem;
                            ">
                                {src['text']}
                            </div>

                            <div style="display: flex; gap: 1rem; font-size: 0.875rem; color: #6B7280;">
                                <div>📊 Relevance: <strong style="color: {color_hex};">{similarity_score:.2%}</strong></div>
                        </div>
                        </div>
                        """

                        st.markdown(source_card, unsafe_allow_html=True)

                        if src.get('skill_name'):
                            st.caption(f"🎯 Skill: {src['skill_name']} | Confidence: {src.get('confidence', 0):.2%}")

                        st.markdown("")

    # Chat input
    if prompt := st.chat_input("Ask about this candidate... (e.g., 'Does this candidate have Python experience?')"):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing profile..."):
                try:
                    answer, sources = st.session_state.rag_system.query(prompt)

                    # Display answer
                    st.markdown(answer)

                    # Add to chat history
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                    # Show evidence with visualizations
                    if show_evidence and sources:
                        with st.expander("📚 View Evidence & Sources", expanded=True):
                            # Source relevance analysis chart
                            if show_source_analysis and len(sources) > 0:
                                st.subheader("📊 Source Relevance Analysis")

                                # Create source relevance visualization
                                import plotly.graph_objects as go
                                source_types = [src['type'].replace('_', ' ').title() for src in sources]
                                similarities = [src.get('similarity', 0) for src in sources]

                                fig_sources = go.Figure(
                                    data=[
                                        go.Bar(
                                            y=source_types,
                                            x=similarities,
                                            orientation='h',
                                            marker=dict(
                                                color=similarities,
                                                colorscale='RdYlGn',
                                                cmin=0,
                                                cmax=1,
                                                showscale=True,
                                                colorbar=dict(title="Relevance")
                                            ),
                                            text=[f"{sim:.2f}" for sim in similarities],
                                            textposition='outside',
                                            hovertemplate="<b>%{y}</b><br>Relevance: %{x:.2f}<extra></extra>"
                                        )
                                    ]
                                )

                                fig_sources.update_layout(
                                    title="Evidence Source Relevance Scores",
                                    xaxis_title="Relevance Score",
                                    yaxis_title="Source Type",
                                    height=250,
                                    margin=dict(l=150, r=50, t=80, b=50),
                                    template="plotly_white"
                                )

                                st.plotly_chart(fig_sources, use_container_width=True)

                            st.markdown("---")

                            # Detailed evidence cards
                            st.subheader("💡 Evidence Details")
                            for i, src in enumerate(sources, 1):
                                # Create color-coded source card
                                source_type = src['type'].replace('_', ' ').title()
                                similarity_score = src.get('similarity', 0)

                                # Determine color based on similarity
                                if similarity_score >= 0.8:
                                    color_hex = "#10B981"  # Green
                                    relevance_label = "High"
                                elif similarity_score >= 0.5:
                                    color_hex = "#F59E0B"  # Amber
                                    relevance_label = "Medium"
                                else:
                                    color_hex = "#EF4444"  # Red
                                    relevance_label = "Low"

                                source_card = f"""
                                <div style="
                                    padding: 1.5rem;
                                    border-radius: 12px;
                                    background: white;
                                    border-left: 4px solid {color_hex};
                                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                                    border: 1px solid #E5E7EB;
                                    margin-bottom: 1rem;
                                ">
                                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                                        <div style="font-weight: 700; color: #0F172A; font-size: 1.125rem;">
                                            [{i}] {source_type}
                                        </div>
                                        <div style="
                                            display: inline-block;
                                            padding: 0.25rem 0.75rem;
                                            background-color: {color_hex}20;
                                            border-radius: 20px;
                                            color: {color_hex};
                                            font-weight: 600;
                                            font-size: 0.875rem;
                                        ">
                                            {relevance_label} Relevance
                                        </div>
                                    </div>

                                    <div style="
                                        padding: 1rem;
                                        background-color: #F9FAFB;
                                        border-radius: 8px;
                                        color: #374151;
                                        font-size: 0.95rem;
                                        line-height: 1.6;
                                        margin-bottom: 0.75rem;
                                    ">
                                        {src['text']}
                                    </div>

                                    <div style="display: flex; gap: 1rem; font-size: 0.875rem; color: #6B7280;">
                                        <div>📊 Relevance: <strong style="color: {color_hex};">{similarity_score:.2%}</strong></div>
                                </div>
                                </div>
                                """

                                st.markdown(source_card, unsafe_allow_html=True)

                                # Additional metadata
                                if src.get('skill_name'):
                                    st.caption(f"🎯 Skill: {src['skill_name']} | Confidence: {src.get('confidence', 0):.2%}")

                                st.markdown("")  # Spacing

                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "sources": []
                    })

        st.rerun()

    # Quick question templates
    if len(st.session_state.chat_messages) == 0:
        st.divider()
        st.subheader("💡 Quick Question Templates")
        st.markdown("Click a question to ask it:")

        # Create tabs for question categories
        tabs = st.tabs(list(QUICK_QUESTIONS.keys()))

        for tab, (category, questions) in zip(tabs, QUICK_QUESTIONS.items()):
            with tab:
                for question in questions:
                    if st.button(question, key=f"quick_{category}_{question[:20]}"):
                        # Trigger query
                        st.session_state.pending_query = question
                        st.rerun()

        # Handle pending query
        if 'pending_query' in st.session_state:
            query = st.session_state.pending_query
            del st.session_state.pending_query

            # Add to chat and process
            st.session_state.chat_messages.append({"role": "user", "content": query})

            with st.spinner("Analyzing profile..."):
                try:
                    answer, sources = st.session_state.rag_system.query(query)
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                except Exception as e:
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": f"Error: {str(e)}",
                        "sources": []
                    })

            st.rerun()


def render_export_page():
    """Render export and download page"""
    if st.session_state.profile is None:
        st.warning("⚠️ Please build your profile first")
        return

    st.header("💾 Export Your Profile")

    profile = st.session_state.profile

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("JSON Export")
        profile_json = {
            'name': profile.name,
            'summary': profile.summary,
            'total_skills': len(profile.skills),
            'top_skills': [
                {
                    'skill': s.skill_name,
                    'confidence': s.final_confidence,
                    'category': s.category
                }
                for s in profile.top_skills
            ],
            'metadata': profile.metadata
        }

        st.download_button(
            label="📥 Download Profile (JSON)",
            data=json.dumps(profile_json, indent=2),
            file_name="skillsense_profile.json",
            mime="application/json"
        )

    with col2:
        st.subheader("Text Summary")
        summary_text = f"""
SkillSense Profile Summary
{'=' * 50}

Name: {profile.name or 'Unknown'}
Generated: {profile.metadata['created_at']}

{profile.summary}

Top 10 Skills:
{chr(10).join([f"{i}. {s.skill_name} (Confidence: {s.final_confidence:.2f})" for i, s in enumerate(profile.top_skills[:10], 1)])}

Data Sources: {', '.join(profile.data_sources)}
        """

        st.download_button(
            label="📥 Download Summary (TXT)",
            data=summary_text,
            file_name="skillsense_summary.txt",
            mime="text/plain"
        )


def render_dashboard_page():
    """Render executive dashboard with overview visualizations and Sankey diagram"""
    if st.session_state.profile is None:
        st.warning("⚠️ Please build a profile first in the Data Input page")
        return

    profile = st.session_state.profile
    st.header("📈 Executive Dashboard")
    st.markdown("Comprehensive overview of your skill profile and career readiness")

    # Header metrics
    from src.visualization import create_metric_grid, create_info_card

    total_skills = len(profile.skills)
    high_conf = len([s for s in profile.skills if s.final_confidence >= 0.75])
    med_conf = len([s for s in profile.skills if 0.5 <= s.final_confidence < 0.75])
    low_conf = len([s for s in profile.skills if s.final_confidence < 0.5])

    # Overall profile completeness
    profile_completeness = min((total_skills / 50), 1.0)  # Assume 50 skills is 100%

    metrics = [
        {"label": "Profile Completeness", "value": f"{int(profile_completeness * 100)}%", "icon": "📊", "color": "secondary"},
        {"label": "Total Skills Identified", "value": total_skills, "icon": "🎯", "color": "primary"},
        {"label": "High Confidence", "value": high_conf, "icon": "⭐", "color": "success"},
        {"label": "Avg Confidence", "value": f"{sum(s.final_confidence for s in profile.skills) / total_skills if total_skills > 0 else 0:.0%}", "icon": "📈", "color": "secondary"},
    ]

    create_metric_grid(metrics, columns=4)

    st.markdown("---")

    # Create tabs for different dashboard views
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔀 Skill Flow", "📋 Summary"])

    with tab1:
        st.subheader("Skill Distribution & Confidence Overview")

        col_dist, col_gauge = st.columns(2)

        with col_dist:
            st.markdown("**Confidence Level Distribution**")
            from src.visualization import create_confidence_distribution
            confidences = [s.final_confidence for s in profile.skills]
            if confidences:
                fig_dist = create_confidence_distribution(confidences)
                st.plotly_chart(fig_dist, use_container_width=True)

        with col_gauge:
            st.markdown("**Overall Profile Completeness**")
            from src.visualization import create_profile_completeness_gauge
            fig_gauge = create_profile_completeness_gauge(profile_completeness)
            st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown("---")

        col_cat, col_src = st.columns(2)

        with col_cat:
            st.markdown("**Skills by Category**")
            from src.visualization import create_category_breakdown
            category_counts = {}
            for skill in profile.skills:
                cat = skill.category if hasattr(skill, 'category') else 'Other'
                category_counts[cat] = category_counts.get(cat, 0) + 1
            if category_counts:
                fig_cat = create_category_breakdown(category_counts)
                st.plotly_chart(fig_cat, use_container_width=True)

        with col_src:
            st.markdown("**Skills by Data Source**")
            from src.visualization import create_source_contribution
            source_counts = {}
            for skill in profile.skills:
                for source in skill.sources if hasattr(skill, 'sources') else []:
                    source_counts[source] = source_counts.get(source, 0) + 1
            if source_counts:
                fig_src = create_source_contribution(source_counts)
                st.plotly_chart(fig_src, use_container_width=True)

    with tab2:
        st.subheader("📊 Skill Flow Diagram")

        # Create Sankey diagram showing skill flow from sources to categories to confidence levels
        import plotly.graph_objects as go

        # Prepare data for Sankey
        sources_list = list(set([s for skill in profile.skills for s in (skill.sources if hasattr(skill, 'sources') else [])]))
        categories_list = list(set([skill.category if hasattr(skill, 'category') else 'Other' for skill in profile.skills]))
        confidence_levels = ["High Confidence (75%+)", "Medium Confidence (50-75%)", "Low Confidence (<50%)"]

        # Build nodes
        all_nodes = sources_list + categories_list + confidence_levels
        node_colors = (
            ['#3B82F6'] * len(sources_list) +  # Blue for sources
            ['#8B5CF6'] * len(categories_list) +  # Purple for categories
            ['#10B981', '#F59E0B', '#EF4444']  # Green, Amber, Red for confidence
        )

        # Create mappings
        node_dict = {node: idx for idx, node in enumerate(all_nodes)}

        # Build links
        source_indices = []
        target_indices = []
        values = []
        link_colors = []

        # Source to Category links
        for skill in profile.skills:
            sources = skill.sources if hasattr(skill, 'sources') else []
            category = skill.category if hasattr(skill, 'category') else 'Other'

            for source in sources:
                if source in node_dict and category in node_dict:
                    source_indices.append(node_dict[source])
                    target_indices.append(node_dict[category])
                    values.append(1)
                    link_colors.append('rgba(59, 130, 246, 0.4)')

        # Category to Confidence links
        for skill in profile.skills:
            category = skill.category if hasattr(skill, 'category') else 'Other'
            confidence = skill.final_confidence

            if confidence >= 0.75:
                conf_level = "High Confidence (75%+)"
                color = 'rgba(16, 185, 129, 0.4)'
            elif confidence >= 0.5:
                conf_level = "Medium Confidence (50-75%)"
                color = 'rgba(245, 158, 11, 0.4)'
            else:
                conf_level = "Low Confidence (<50%)"
                color = 'rgba(239, 68, 68, 0.4)'

            if category in node_dict and conf_level in node_dict:
                source_indices.append(node_dict[category])
                target_indices.append(node_dict[conf_level])
                values.append(1)
                link_colors.append(color)

        # Create Sankey
        fig_sankey = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color='black', width=0.5),
                        label=all_nodes,
                        color=node_colors,
                    ),
                    link=dict(
                        source=source_indices,
                        target=target_indices,
                        value=values,
                        color=link_colors,
                    ),
                )
            ]
        )

        fig_sankey.update_layout(
            title="Skill Flow: From Sources to Confidence Levels",
            font=dict(size=10),
            height=600,
            margin=dict(l=50, r=50, t=100, b=50),
        )

        st.plotly_chart(fig_sankey, use_container_width=True)

        st.info(
            "📌 This Sankey diagram shows how your skills flow from their sources (CV, GitHub, etc.) "
            "through skill categories and into confidence levels. "
            "Thicker flows indicate more skills in that pathway."
        )

    with tab3:
        st.subheader("📋 Career Readiness Summary")

        # Create summary cards
        col1, col2 = st.columns(2)

        with col1:
            create_info_card(
                title="Skill Strength",
                content=f"You have identified <strong>{total_skills} unique skills</strong> with an average confidence of <strong>{sum(s.final_confidence for s in profile.skills) / total_skills if total_skills > 0 else 0:.0%}</strong>. "
                f"<strong>{high_conf}</strong> skills have high confidence scores (75%+).",
                color="success",
                icon="💪"
            )

        with col2:
            create_info_card(
                title="Profile Coverage",
                content=f"Your profile is <strong>{int(profile_completeness * 100)}% complete</strong>. "
                f"You have provided <strong>{len(profile.data_sources)} data sources</strong>, which helps ensure comprehensive skill extraction.",
                color="secondary",
                icon="📚"
            )

        st.markdown("---")

        # Top skills section
        st.subheader("⭐ Top 10 Skills by Confidence")

        top_skills = sorted(profile.skills, key=lambda s: s.final_confidence, reverse=True)[:10]

        for idx, skill in enumerate(top_skills, 1):
            from src.visualization import get_confidence_color

            # Create a custom progress bar for each skill
            conf = skill.final_confidence
            color = get_confidence_color(conf) if hasattr(skill, 'final_confidence') else "#3B82F6"

            skill_row = f"""
            <div style="
                padding: 1rem;
                margin-bottom: 0.75rem;
                border-radius: 8px;
                background: white;
                border: 1px solid #E5E7EB;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div style="font-weight: 700; color: #0F172A;">
                        {idx}. {skill.name}
                    </div>
                    <div style="font-size: 0.875rem; color: {color}; font-weight: 700;">
                        {skill.final_confidence:.0%}
                    </div>
                </div>
                <div style="
                    width: 100%;
                    height: 8px;
                    background-color: #E5E7EB;
                    border-radius: 4px;
                    overflow: hidden;
                ">
                    <div style="
                        height: 100%;
                        width: {skill.final_confidence * 100}%;
                        background-color: {color};
                        border-radius: 4px;
                    "></div>
                </div>
            </div>
            """
            st.markdown(skill_row, unsafe_allow_html=True)

        st.markdown("---")

        # Recommendations
        st.subheader("💡 Next Steps")

        recommendations = []

        if profile_completeness < 0.6:
            recommendations.append("📌 **Expand Your Skills**: You have identified several skills. Consider adding more sources (references, projects) to discover additional competencies.")

        if low_conf > high_conf:
            recommendations.append("📌 **Validate Your Skills**: You have many skills with medium or low confidence. Add more evidence from your CV or work samples to strengthen these.")

        if len(profile.data_sources) < 3:
            recommendations.append("📌 **Diversify Your Sources**: Adding a GitHub profile, personal statement, or references will provide a more comprehensive skill picture.")

        if total_skills > 0:
            recommendations.append("📌 **Review Your Profile**: Visit the **🎓 Skill Profile** page to see detailed skill breakdown and evidence.")
            recommendations.append("📌 **Explore Job Matches**: Head to **💼 Job Matching** to discover opportunities that align with your skills.")

        for rec in recommendations:
            st.info(rec, icon="✨")


def main():
    """Main application"""
    initialize_session_state()
    render_header()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to:",
        ["🏠 Home", "📊 Data Input", "📈 Dashboard", "🎓 Skill Profile", "💼 Job Matching", "💬 Employer Q&A", "💾 Export"]
    )

    # Demo mode
    if st.sidebar.checkbox("🎬 Load Demo Profile"):
        st.sidebar.info("Demo profile loaded with sample data")
        # You can add a pre-built demo profile here

    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "SkillSense uses AI to analyze your CV, GitHub, and other sources "
        "to identify your skills and match you with relevant job opportunities."
    )

    # Route to pages
    if page == "🏠 Home":
        st.markdown("""
        ## Welcome to SkillSense!

        ### What am I good at?

        SkillSense helps you discover and validate your hidden skills by analyzing data from multiple sources:

        - **📄 CV/Resume**: Extract skills from your PDF resume
        - **💻 GitHub**: Analyze your repositories and code
        - **✍️ Personal Statement**: Assess communication and soft skills
        - **✉️ Reference Letters**: Validate skills through endorsements

        ### How it works:

        1. **Upload Your Data**: Provide your CV, GitHub username, or text information
        2. **AI Analysis**: Our NLP engine extracts both explicit and implicit skills
        3. **Skill Profile**: View your comprehensive skill profile with confidence scores
        4. **Job Matching**: Discover roles that match your skills and identify gaps
        5. **Export**: Download your profile for future use

        ### Get Started

        Click on **📊 Data Input** in the sidebar to begin your skill analysis!
        """)

    elif page == "📊 Data Input":
        st.markdown("### Provide Your Information")

        # Name input
        name = st.text_input("Your Name", placeholder="John Doe")

        inputs = render_data_input_page()

        if inputs and st.button("🚀 Analyze My Skills", type="primary"):
            inputs['name'] = name if name else None
            if build_profile_from_inputs(inputs):
                st.balloons()
                st.info("Navigate to **📈 Dashboard** to view your results!")

    elif page == "📈 Dashboard":
        render_dashboard_page()

    elif page == "🎓 Skill Profile":
        render_skill_profile_page()

    elif page == "💼 Job Matching":
        render_job_matching_page()

    elif page == "💬 Employer Q&A":
        render_employer_qa_page()

    elif page == "💾 Export":
        render_export_page()


if __name__ == "__main__":
    main()
