"""
SkillSense - CLI Interface
Command-line interface for skill extraction and analysis
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from profile_generation.profile_builder import ProfileBuilder
from analysis.job_matcher import JobMatcher


def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║              🎯 SkillSense                            ║
    ║         Unlock Your Hidden Potential                 ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    print(banner)


def demo_github_analysis():
    """Demo: Analyze a GitHub profile"""
    print("\n" + "="*60)
    print("DEMO: GitHub Profile Analysis")
    print("="*60)

    username = input("\nEnter GitHub username (or press Enter for 'torvalds'): ").strip()
    if not username:
        username = "torvalds"

    print(f"\n🔍 Analyzing GitHub profile: {username}")
    print("-" * 60)

    builder = ProfileBuilder()

    try:
        profile = builder.build_profile(
            name=username,
            github_username=username
        )

        print(f"\n✅ Analysis Complete!")
        print(f"\n📊 Summary:")
        print(profile.summary)

        print(f"\n🏆 Top 10 Skills:")
        for i, skill in enumerate(profile.top_skills[:10], 1):
            print(f"  {i:2d}. {skill.skill_name:<30} (Confidence: {skill.final_confidence:.2f})")

        # Job matching
        print(f"\n💼 Top Job Matches:")
        matcher = JobMatcher()
        matches = matcher.match_profile_to_jobs(profile.skills, top_n=5)

        for i, match in enumerate(matches, 1):
            print(f"  {i}. {match.job_title:<30} (Match: {match.match_score*100:.0f}%)")
            if match.skill_gaps:
                print(f"     Skill gaps: {', '.join(match.skill_gaps[:3])}")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("This might be due to rate limiting or invalid username.")


def demo_text_analysis():
    """Demo: Analyze personal statement"""
    print("\n" + "="*60)
    print("DEMO: Personal Statement Analysis")
    print("="*60)

    sample_statement = """
    I am a passionate software engineer with 5 years of experience in building
    scalable web applications using Python, JavaScript, and React. Throughout my
    career, I have led cross-functional teams to deliver complex projects on time
    and under budget. I excel at problem-solving and have a proven track record of
    implementing innovative solutions that drive business value.

    My technical expertise includes machine learning, cloud architecture (AWS),
    and DevOps practices. I'm proficient in Docker, Kubernetes, and CI/CD pipelines.
    I have strong communication skills and enjoy mentoring junior developers.
    I'm passionate about clean code, test-driven development, and agile methodologies.
    """

    print("\nAnalyzing sample personal statement...")
    print("-" * 60)

    builder = ProfileBuilder()

    try:
        profile = builder.build_profile(
            name="Sample User",
            personal_statement=sample_statement
        )

        print(f"\n✅ Analysis Complete!")
        print(f"\n📊 Summary:")
        print(profile.summary)

        print(f"\n🏆 Top Skills Identified:")
        for i, skill in enumerate(profile.top_skills[:15], 1):
            print(f"  {i:2d}. {skill.skill_name:<30} (Confidence: {skill.final_confidence:.2f})")

        # Show soft skills
        soft_skills = [s for s in profile.skills if 'soft' in s.category]
        if soft_skills:
            print(f"\n💡 Soft Skills Detected:")
            for skill in soft_skills[:5]:
                print(f"  - {skill.skill_name}")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def interactive_mode():
    """Interactive mode for custom input"""
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)

    print("\nChoose input method:")
    print("1. GitHub username")
    print("2. Personal statement")
    print("3. Both")

    choice = input("\nEnter choice (1-3): ").strip()

    github_username = None
    personal_statement = None

    if choice in ['1', '3']:
        github_username = input("Enter GitHub username: ").strip()

    if choice in ['2', '3']:
        print("\nEnter your personal statement (press Ctrl+D or Ctrl+Z when done):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            personal_statement = '\n'.join(lines)

    if not github_username and not personal_statement:
        print("❌ No input provided")
        return

    print("\n🔍 Building your skill profile...")
    print("-" * 60)

    builder = ProfileBuilder()

    try:
        profile = builder.build_profile(
            name="User",
            github_username=github_username if github_username else None,
            personal_statement=personal_statement if personal_statement else None
        )

        print(f"\n✅ Profile Complete!")
        print(f"\n📊 {profile.summary}")

        print(f"\n🏆 Your Top Skills:")
        for i, skill in enumerate(profile.top_skills[:20], 1):
            conf_icon = "🟢" if skill.final_confidence >= 0.75 else "🟡" if skill.final_confidence >= 0.5 else "🔴"
            print(f"  {conf_icon} {i:2d}. {skill.skill_name:<35} ({skill.final_confidence:.2f})")

        # Job recommendations
        print(f"\n💼 Recommended Career Paths:")
        matcher = JobMatcher()
        matches = matcher.match_profile_to_jobs(profile.skills, top_n=5)

        for i, match in enumerate(matches, 1):
            print(f"\n  {i}. {match.job_title} ({match.match_score*100:.0f}% match)")
            print(f"     {match.recommendation}")
            if match.missing_required:
                print(f"     Missing: {', '.join(match.missing_required[:3])}")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def main():
    """Main CLI entry point"""
    print_banner()

    print("\nWelcome to SkillSense!")
    print("AI-powered skill extraction and career matching")

    print("\nSelect mode:")
    print("1. Demo: GitHub Profile Analysis")
    print("2. Demo: Personal Statement Analysis")
    print("3. Interactive Mode (Custom Input)")
    print("4. Launch Web Interface")
    print("5. Exit")

    choice = input("\nEnter your choice (1-5): ").strip()

    if choice == '1':
        demo_github_analysis()
    elif choice == '2':
        demo_text_analysis()
    elif choice == '3':
        interactive_mode()
    elif choice == '4':
        print("\n🚀 Launching Streamlit web interface...")
        print("\nRun the following command:")
        print("  streamlit run app.py")
        print("\nOr use: uv run streamlit run app.py")
    elif choice == '5':
        print("\n👋 Thank you for using SkillSense!")
    else:
        print("\n❌ Invalid choice")

    print("\n")


if __name__ == "__main__":
    main()
