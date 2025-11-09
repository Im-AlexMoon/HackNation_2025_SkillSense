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
    """Render data input page - supports simultaneous multi-source input"""
    st.header("📊 Data Input")
    st.markdown("Provide information from **multiple sources** for comprehensive skill analysis. You can use any combination of sources below:")

    # Initialize session state for collected inputs
    if 'collected_inputs' not in st.session_state:
        st.session_state.collected_inputs = {}

    # Dictionary to accumulate all inputs from this render
    inputs = {}

    # Section 1: CV Upload (supports multiple files)
    with st.expander("📄 Upload CV(s)", expanded=True):
        st.markdown("Upload one or more CVs in PDF format")
        cv_files = st.file_uploader(
            "Upload CV(s) in PDF format",
            type=['pdf'],
            accept_multiple_files=True,
            key="cv_uploader"
        )

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
            st.success(f"CV(s) uploaded: {len(cv_paths)} file(s)")

    # Section 2: GitHub Connection
    with st.expander("💻 Connect GitHub Profile", expanded=True):
        st.markdown("Fetch repositories, contributions, and project data")
        github_username = st.text_input(
            "GitHub Username",
            placeholder="e.g., octocat",
            key="github_input"
        )

        if github_username:
            inputs['github_username'] = github_username
            st.info(f"Will fetch data for: github.com/{github_username}")

    # Section 3: Text Input
    with st.expander("✍️ Text Input", expanded=True):
        st.markdown("Provide additional context through text")

        col1, col2 = st.columns(2)

        with col1:
            personal_statement = st.text_area(
                "Personal Statement",
                placeholder="Describe your background, skills, and career goals...",
                height=200,
                key="statement_input"
            )

        with col2:
            reference_letter = st.text_area(
                "Reference Letter (Optional)",
                placeholder="Paste a reference letter or recommendation...",
                height=200,
                key="reference_input"
            )

        if personal_statement:
            inputs['personal_statement'] = personal_statement
        if reference_letter:
            inputs['reference_letter'] = reference_letter

    # Display collected sources summary
    if inputs:
        st.markdown("---")
        st.subheader("📋 Collected Sources")

        sources = []
        if 'cv_paths' in inputs:
            sources.append(f"CV(s): {len(inputs['cv_paths'])} file(s)")
        if 'github_username' in inputs:
            sources.append(f"GitHub: {inputs['github_username']}")
        if 'personal_statement' in inputs:
            sources.append("Personal Statement")
        if 'reference_letter' in inputs:
            sources.append("Reference Letter")

        for source in sources:
            st.markdown(f"- {source}")

        return inputs

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


def render_employer_qa_page():
    """Render Employer Q&A page with RAG system"""
    if st.session_state.profile is None:
        st.warning("⚠️ Please build a candidate profile first in the Data Input page")
        return

    st.header("💬 Employer Q&A - Ask About This Candidate")
    st.markdown("Ask natural language questions about the candidate's skills, experience, and qualifications")

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
        show_similarity = st.checkbox("Show Similarity Scores", value=False)

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

            # Show evidence if available and enabled
            if show_evidence and msg.get("sources") and msg["role"] == "assistant":
                with st.expander("📚 View Evidence & Sources"):
                    for i, src in enumerate(msg["sources"], 1):
                        st.markdown(f"**[{i}] {src['type'].replace('_', ' ').title()}**")
                        st.info(src['text'])

                        if show_similarity:
                            st.caption(f"Similarity: {src.get('similarity', 0):.2f}")

                        if src.get('skill_name'):
                            st.caption(f"Skill: {src['skill_name']} | Confidence: {src.get('confidence', 0):.2f}")

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

                    # Show evidence
                    if show_evidence and sources:
                        with st.expander("📚 View Evidence & Sources"):
                            for i, src in enumerate(sources, 1):
                                st.markdown(f"**[{i}] {src['type'].replace('_', ' ').title()}**")
                                st.info(src['text'])

                                if show_similarity:
                                    st.caption(f"Similarity: {src.get('similarity', 0):.2f}")

                                if src.get('skill_name'):
                                    st.caption(f"Skill: {src['skill_name']} | Confidence: {src.get('confidence', 0):.2f}")

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


def main():
    """Main application"""
    initialize_session_state()
    render_header()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to:",
        ["🏠 Home", "📊 Data Input", "🎓 Skill Profile", "💼 Job Matching", "💬 Employer Q&A", "💾 Export"]
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

    elif page == "💬 Employer Q&A":
        render_employer_qa_page()

    elif page == "💾 Export":
        render_export_page()


if __name__ == "__main__":
    main()
