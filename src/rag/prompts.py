"""
Prompt Templates for RAG System
System and user prompts for candidate profile Q&A
"""

SYSTEM_PROMPT = """You are an AI assistant helping employers evaluate job candidates based on their skill profiles.

Your role is to:
1. Answer questions about a candidate's skills, experience, and qualifications
2. Base ALL answers ONLY on the provided candidate profile data
3. Cite specific evidence from the profile (CV, GitHub, personal statement, etc.)
4. Include confidence levels when discussing skills
5. Be honest about limitations - if information is not in the profile, clearly state "Not found in candidate profile"
6. Provide clear, concise, and professional responses

Guidelines:
- Never make assumptions beyond the provided data
- Always cite sources when mentioning skills or experience
- Format confidence scores as percentages when relevant
- If a skill has low confidence (<0.5), mention this as a caveat
- Be objective and factual, not promotional
- Focus on evidence-based assessment

Remember: Your goal is to help employers make informed hiring decisions based on accurate profile data."""


def format_user_prompt(question: str, context: str, profile_summary: str, conversation_history: str = None) -> str:
    """
    Format user prompt with context

    Args:
        question: Employer's question
        context: Retrieved context from profile
        profile_summary: High-level profile summary
        conversation_history: Optional conversation history for multi-turn

    Returns:
        Formatted prompt string
    """
    prompt_parts = []

    # Add conversation history if available
    if conversation_history:
        prompt_parts.append("PREVIOUS CONVERSATION:")
        prompt_parts.append(conversation_history)
        prompt_parts.append("")

    # Profile summary
    prompt_parts.append("CANDIDATE PROFILE SUMMARY:")
    prompt_parts.append(profile_summary)
    prompt_parts.append("")

    # Retrieved context
    prompt_parts.append("RELEVANT INFORMATION FROM PROFILE:")
    prompt_parts.append(context)
    prompt_parts.append("")

    # Current question
    prompt_parts.append("EMPLOYER QUESTION:")
    prompt_parts.append(question)
    prompt_parts.append("")

    # Instructions
    prompt_parts.append("INSTRUCTIONS:")
    prompt_parts.append("Answer the question based on the candidate profile information provided above.")
    prompt_parts.append("- Cite specific evidence and sources (e.g., 'From GitHub:', 'From CV:')")
    prompt_parts.append("- Include confidence levels when discussing skills (e.g., '0.92 confidence - high')")
    prompt_parts.append("- If information is missing, state 'Not found in candidate profile'")
    prompt_parts.append("- Be concise but thorough")
    prompt_parts.append("")
    prompt_parts.append("ANSWER:")

    return "\n".join(prompt_parts)


# Quick question templates for UI
QUICK_QUESTIONS = {
    "Technical Skills": [
        "What are their strongest technical skills?",
        "What programming languages do they know?",
        "What frameworks and tools do they use?",
        "How experienced are they with cloud technologies?"
    ],
    "Soft Skills": [
        "What are their leadership qualities?",
        "How are their communication skills?",
        "Do they have team collaboration experience?",
        "What soft skills are demonstrated?"
    ],
    "Experience": [
        "What is their work experience?",
        "What projects have they worked on?",
        "What industries have they worked in?",
        "How many years of experience do they have?"
    ],
    "Role Fit": [
        "Is this candidate suitable for a Senior Developer role?",
        "Would they be a good fit for a Full Stack position?",
        "Are they qualified for a leadership role?",
        "What type of role would they excel in?"
    ],
    "Evidence": [
        "Show me evidence of their technical abilities",
        "What GitHub projects demonstrate their skills?",
        "What specific achievements are mentioned?",
        "Provide examples of their work"
    ]
}


# Skill verification specific prompt
SKILL_VERIFICATION_PROMPT = """You are verifying whether a candidate possesses a specific skill.

SKILL TO VERIFY: {skill_name}

CANDIDATE PROFILE:
{context}

Provide a structured answer with:
1. YES/NO - Does the candidate have this skill?
2. CONFIDENCE: High/Medium/Low based on evidence strength
3. EVIDENCE: Specific quotes or mentions from their profile
4. RELATED SKILLS: Other relevant skills they possess
5. RECOMMENDATION: Brief assessment for employers

Be precise and evidence-based."""


# Comparison prompt for multiple candidates
COMPARISON_PROMPT = """You are comparing candidates for an employer.

COMPARISON CRITERIA:
{criteria}

CANDIDATE DATA:
{candidates_data}

Provide a structured comparison:
1. OVERVIEW: Brief summary of each candidate
2. STRENGTHS: Key strengths of each
3. WEAKNESSES: Areas where each could improve
4. BEST FIT: Which candidate is better suited and why
5. RECOMMENDATION: Clear hiring recommendation

Focus on objective, data-driven comparison."""


def get_intent_prompt(intent: str) -> str:
    """Get specialized prompt based on query intent"""
    intent_prompts = {
        "skill_check": """Focus on verifying specific skills. Be direct about whether the candidate has the skill,
        with clear confidence levels and evidence citations.""",

        "evidence": """Provide specific evidence from the profile. Include direct quotes, project names,
        GitHub repository details, or CV excerpts that demonstrate the skill or quality in question.""",

        "comparison": """Compare the candidate's profile against the stated requirements.
        Provide a match percentage, list matched skills, identify gaps, and give a clear recommendation.""",

        "soft_skills": """Analyze soft skills and personal qualities. Look for evidence in writing style,
        project descriptions, leadership mentions, team collaboration, and communication abilities.""",

        "experience_level": """Assess the candidate's experience level in the specified area.
        Consider years mentioned, project complexity, technologies used, and leadership roles."""
    }

    return intent_prompts.get(intent, "")


# Example usage
if __name__ == "__main__":
    # Test prompt formatting
    test_question = "Does this candidate have Python experience?"
    test_context = """
    Python: Confidence 0.92, Sources: GitHub, CV
    Evidence: 15 GitHub repositories using Python, CV mentions 5 years experience
    """
    test_summary = "Software engineer with 5 years experience, 45 skills identified"

    prompt = format_user_prompt(test_question, test_context, test_summary)

    print("Sample Formatted Prompt:")
    print("=" * 60)
    print(prompt)
    print("=" * 60)

    print("\n✓ Prompts module loaded successfully")
