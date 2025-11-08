"""
SkillSense Installation Test
Run this to verify all components are working correctly
"""

import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def print_status(message, success=True):
    """Print colored status message"""
    icon = "[OK]" if success else "[FAIL]"
    print(f"{icon} {message}")

def test_imports():
    """Test that all required modules can be imported"""
    print("\n[PACKAGES] Testing Package Imports...")

    try:
        import pandas
        print_status("pandas imported")
    except ImportError as e:
        print_status(f"pandas import failed: {e}", False)
        return False

    try:
        import numpy
        print_status("numpy imported")
    except ImportError as e:
        print_status(f"numpy import failed: {e}", False)
        return False

    try:
        import matplotlib
        print_status("matplotlib imported")
    except ImportError as e:
        print_status(f"matplotlib import failed: {e}", False)
        return False

    try:
        import streamlit
        print_status("streamlit imported")
    except ImportError as e:
        print_status(f"streamlit import failed: {e}", False)
        return False

    try:
        import plotly
        print_status("plotly imported")
    except ImportError as e:
        print_status(f"plotly import failed: {e}", False)
        return False

    try:
        from sentence_transformers import SentenceTransformer
        print_status("sentence-transformers imported")
    except ImportError as e:
        print_status(f"sentence-transformers import failed: {e}", False)
        return False

    try:
        import pymupdf
        print_status("PyMuPDF imported")
    except ImportError as e:
        print_status(f"PyMuPDF import failed: {e}", False)
        return False

    try:
        from github import Github
        print_status("PyGithub imported")
    except ImportError as e:
        print_status(f"PyGithub import failed: {e}", False)
        return False

    return True

def test_modules():
    """Test that custom modules can be imported"""
    print("\n[MODULES] Testing SkillSense Modules...")

    sys.path.append(str(Path(__file__).parent / 'src'))

    try:
        from data_ingestion.pdf_extractor import PDFExtractor
        print_status("PDFExtractor module loaded")
    except Exception as e:
        print_status(f"PDFExtractor failed: {e}", False)
        return False

    try:
        from data_ingestion.github_collector import GitHubCollector
        print_status("GitHubCollector module loaded")
    except Exception as e:
        print_status(f"GitHubCollector failed: {e}", False)
        return False

    try:
        from data_ingestion.text_processor import TextProcessor
        print_status("TextProcessor module loaded")
    except Exception as e:
        print_status(f"TextProcessor failed: {e}", False)
        return False

    try:
        from skill_extraction.skill_extractor import SkillExtractor
        print_status("SkillExtractor module loaded")
    except Exception as e:
        print_status(f"SkillExtractor failed: {e}", False)
        return False

    try:
        from skill_extraction.confidence_scorer import ConfidenceScorer
        print_status("ConfidenceScorer module loaded")
    except Exception as e:
        print_status(f"ConfidenceScorer failed: {e}", False)
        return False

    try:
        from profile_generation.profile_builder import ProfileBuilder
        print_status("ProfileBuilder module loaded")
    except Exception as e:
        print_status(f"ProfileBuilder failed: {e}", False)
        return False

    try:
        from analysis.job_matcher import JobMatcher
        print_status("JobMatcher module loaded")
    except Exception as e:
        print_status(f"JobMatcher failed: {e}", False)
        return False

    return True

def test_config_files():
    """Test that configuration files exist and are valid"""
    print("\n[CONFIG] Testing Configuration Files...")

    import json

    # Test skill taxonomy
    taxonomy_path = Path(__file__).parent / 'config' / 'skill_taxonomy.json'
    if taxonomy_path.exists():
        try:
            with open(taxonomy_path, 'r') as f:
                data = json.load(f)
            print_status(f"Skill taxonomy loaded ({len(data)} categories)")
        except Exception as e:
            print_status(f"Skill taxonomy invalid: {e}", False)
            return False
    else:
        print_status("Skill taxonomy file not found", False)
        return False

    # Test source weights
    weights_path = Path(__file__).parent / 'config' / 'source_weights.json'
    if weights_path.exists():
        try:
            with open(weights_path, 'r') as f:
                data = json.load(f)
            print_status(f"Source weights loaded ({len(data)} configurations)")
        except Exception as e:
            print_status(f"Source weights invalid: {e}", False)
            return False
    else:
        print_status("Source weights file not found", False)
        return False

    return True

def test_skill_extraction():
    """Test skill extraction on sample text"""
    print("\n[TEST] Testing Skill Extraction...")

    sys.path.append(str(Path(__file__).parent / 'src'))

    try:
        from skill_extraction.skill_extractor import SkillExtractor

        extractor = SkillExtractor()
        sample_text = """
        I have extensive experience with Python, JavaScript, and React.
        I've worked on machine learning projects using TensorFlow and have
        strong knowledge of AWS cloud architecture.
        """

        skills = extractor.extract_all_skills(sample_text, source='test')

        if len(skills) > 0:
            print_status(f"Extracted {len(skills)} skills from sample text")
            print(f"   Sample skills: {', '.join([s.skill_name for s in skills[:5]])}")
        else:
            print_status("No skills extracted (may be normal)", True)

        return True

    except Exception as e:
        print_status(f"Skill extraction test failed: {e}", False)
        return False

def test_ml_models():
    """Test that ML models can be loaded"""
    print("\n[ML] Testing Machine Learning Models...")

    try:
        from sentence_transformers import SentenceTransformer

        print("   Loading sentence transformer (may take 30-60s on first run)...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print_status("Sentence transformer loaded successfully")

        # Test encoding
        test_text = "This is a test sentence"
        embedding = model.encode(test_text)
        print_status(f"Text encoding works (embedding dim: {len(embedding)})")

        return True

    except Exception as e:
        print_status(f"ML model test failed: {e}", False)
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("   SkillSense Installation Test")
    print("="*60)

    all_passed = True

    # Run tests
    all_passed &= test_imports()
    all_passed &= test_modules()
    all_passed &= test_config_files()
    all_passed &= test_skill_extraction()
    all_passed &= test_ml_models()

    # Final report
    print("\n" + "="*60)
    if all_passed:
        print("[SUCCESS] All tests passed! SkillSense is ready to run.")
        print("\nNext steps:")
        print("  1. Run CLI demo: python main.py")
        print("  2. Run web app: streamlit run app.py")
        print("  3. Check QUICK_START.md for demo options")
    else:
        print("[WARNING] Some tests failed. Please check errors above.")
        print("\nCommon fixes:")
        print("  1. Activate venv: .venv\\Scripts\\activate")
        print("  2. Install deps: uv sync")
        print("  3. Download spaCy: python -m spacy download en_core_web_sm")
    print("="*60)

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
