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
from typing import Optional

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from profile_generation.profile_builder import ProfileBuilder
from analysis.job_matcher import JobMatcher


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
    """Render data input page"""
    st.header("📊 Data Input")
    st.markdown("Provide your information from multiple sources for comprehensive skill analysis")

    # Create tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["📄 Upload CV", "💻 Connect GitHub", "✍️ Text Input"])

    with tab1:
        st.subheader("Upload Your CV (PDF)")
        cv_file = st.file_uploader("Upload CV in PDF format", type=['pdf'])
        if cv_file:
            # Save uploaded file temporarily
            temp_path = Path("temp_cv.pdf")
            with open(temp_path, 'wb') as f:
                f.write(cv_file.getbuffer())
            st.success("✅ CV uploaded successfully!")
            return {'cv_path': str(temp_path)}

    with tab2:
        st.subheader("Connect Your GitHub Profile")
        github_username = st.text_input("GitHub Username", placeholder="e.g., octocat")
        if github_username:
            st.info(f"Will fetch data for: github.com/{github_username}")
            return {'github_username': github_username}

    with tab3:
        st.subheader("Provide Text Information")

        col1, col2 = st.columns(2)

        with col1:
            personal_statement = st.text_area(
                "Personal Statement",
                placeholder="Describe your background, skills, and career goals...",
                height=200
            )

        with col2:
            reference_letter = st.text_area(
                "Reference Letter (Optional)",
                placeholder="Paste a reference letter or recommendation...",
                height=200
            )

        if personal_statement:
            return {
                'personal_statement': personal_statement,
                'reference_letter': reference_letter if reference_letter else None
            }

    return None


def build_profile_from_inputs(inputs: dict):
    """Build profile from user inputs"""
    with st.spinner("🔍 Analyzing your data and extracting skills..."):
        try:
            profile = st.session_state.profile_builder.build_profile(
                name=inputs.get('name', 'User'),
                cv_path=inputs.get('cv_path'),
                github_username=inputs.get('github_username'),
                personal_statement=inputs.get('personal_statement'),
                reference_letter=inputs.get('reference_letter')
            )
            st.session_state.profile = profile
            st.success("✅ Profile analysis complete!")
            return True
        except Exception as e:
            st.error(f"❌ Error building profile: {str(e)}")
            return False


def render_skill_profile_page():
    """Render skill profile visualization page"""
    if st.session_state.profile is None:
        st.warning("⚠️ Please provide your data first in the Data Input page")
        return

    profile = st.session_state.profile

    st.header("🎓 Your Skill Profile")

    # Summary
    st.info(profile.summary)

    # Metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Skills Identified", len(profile.skills))
    with col2:
        st.metric("Data Sources Analyzed", len(profile.data_sources))
    with col3:
        high_confidence = len([s for s in profile.skills if s.final_confidence >= 0.75])
        st.metric("High Confidence Skills", high_confidence)

    # Top Skills
    st.subheader("🏆 Top 20 Skills")

    # Create radar chart for top skills
    if profile.top_skills:
        fig = create_radar_chart(profile.top_skills[:10])
        st.plotly_chart(fig, use_container_width=True)

    # Skills by category
    st.subheader("📚 Skills by Category")

    for category, skills in profile.skill_categories.items():
        if skills:
            with st.expander(f"{category.replace('_', ' ').title()} ({len(skills)} skills)"):
                # Sort by confidence
                sorted_skills = sorted(skills, key=lambda x: x.final_confidence, reverse=True)

                for skill in sorted_skills[:15]:  # Limit display
                    conf_level = "high" if skill.final_confidence >= 0.75 else "medium" if skill.final_confidence >= 0.5 else "low"

                    col1, col2, col3 = st.columns([3, 1, 2])
                    with col1:
                        st.write(f"**{skill.skill_name}**")
                    with col2:
                        st.write(f"{skill.final_confidence:.2f}")
                    with col3:
                        st.write(f"Sources: {', '.join(skill.sources)}")

    # Detailed skill list with evidence
    with st.expander("🔍 View Detailed Evidence"):
        for skill in profile.top_skills[:10]:
            st.markdown(f"### {skill.skill_name}")
            st.write(f"**Confidence:** {skill.final_confidence:.2f}")
            st.write(f"**Sources:** {', '.join(skill.sources)}")
            if skill.evidence:
                st.write("**Evidence:**")
                for ev in skill.evidence[:3]:
                    st.caption(f"- {ev}")
            st.divider()


def render_job_matching_page():
    """Render job matching and recommendations page"""
    if st.session_state.profile is None:
        st.warning("⚠️ Please build your profile first")
        return

    profile = st.session_state.profile
    matcher = st.session_state.job_matcher

    st.header("💼 Job Matching & Recommendations")

    # Get job matches
    with st.spinner("🔎 Finding best job matches..."):
        matches = matcher.match_profile_to_jobs(profile.skills, top_n=10)

    # Display top matches
    st.subheader("🎯 Top Job Matches")

    for i, match in enumerate(matches[:5], 1):
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### {i}. {match.job_title}")
                st.write(match.recommendation)

            with col2:
                # Match score gauge
                st.metric("Match Score", f"{match.match_score * 100:.0f}%")

            # Details in expander
            with st.expander("View Details"):
                col_a, col_b = st.columns(2)

                with col_a:
                    st.write("**✅ Matched Skills:**")
                    for skill in match.matched_skills[:10]:
                        st.write(f"- {skill}")

                with col_b:
                    st.write("**📌 Skill Gaps:**")
                    if match.missing_required:
                        st.write("*Required:*")
                        for skill in match.missing_required:
                            st.write(f"- {skill}")
                    if match.missing_preferred[:3]:
                        st.write("*Preferred:*")
                        for skill in match.missing_preferred[:3]:
                            st.write(f"- {skill}")

            st.divider()

    # Skill Gap Analysis
    st.subheader("📊 Skill Gap Analysis")

    target_job = st.selectbox(
        "Select a target role for detailed gap analysis:",
        [match.job_title for match in matches[:10]]
    )

    if target_job:
        gap_analysis = matcher.identify_skill_gaps(profile.skills, target_job)

        if 'error' not in gap_analysis:
            # Readiness score
            st.metric("Readiness Score", f"{gap_analysis['readiness_score'] * 100:.0f}%")

            # Critical gaps
            if gap_analysis['gaps']['critical']:
                st.warning("**Critical Skills to Develop:**")
                for skill in gap_analysis['gaps']['critical']:
                    st.write(f"- {skill}")

            # Learning recommendations
            if gap_analysis['recommendations']:
                st.success("**📚 Learning Path Recommendations:**")
                for rec in gap_analysis['recommendations']:
                    st.write(f"**[{rec['priority']} Priority]** {rec['action']}")


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


def main():
    """Main application"""
    initialize_session_state()
    render_header()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to:",
        ["🏠 Home", "📊 Data Input", "🎓 Skill Profile", "💼 Job Matching", "💾 Export"]
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
                st.info("Navigate to **🎓 Skill Profile** to view your results!")

    elif page == "🎓 Skill Profile":
        render_skill_profile_page()

    elif page == "💼 Job Matching":
        render_job_matching_page()

    elif page == "💾 Export":
        render_export_page()


if __name__ == "__main__":
    main()
