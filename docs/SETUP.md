# SkillSense Setup Guide

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
# Make sure you're in the project directory
cd HackNation_2025_SkillSense

# Install all dependencies
uv sync

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### 2. Test the Installation

```bash
# Test CLI
python main.py

# Should show the SkillSense banner and menu
```

### 3. Run Demo

```bash
# Option 1: CLI Demo (Personal Statement Analysis)
python main.py
# Select option 2 for quick demo

# Option 2: Web Interface
streamlit run app.py
# Opens browser at http://localhost:8501
```

---

## Common Issues & Solutions

### Issue: "Module not found" error
**Solution**: Make sure you activated the virtual environment
```bash
# Windows
.venv\Scripts\activate

# Unix/MacOS
source .venv/bin/activate
```

### Issue: spaCy model not found
**Solution**: Download the language model
```bash
python -m spacy download en_core_web_sm
```

### Issue: Slow first run
**Solution**: The first run downloads the sentence-transformers model (~90MB). Subsequent runs are much faster.

### Issue: GitHub API rate limiting
**Solution**:
1. Create a GitHub personal access token at https://github.com/settings/tokens
2. Add to environment:
```bash
# Windows
set GITHUB_TOKEN=your_token_here

# Unix/MacOS
export GITHUB_TOKEN=your_token_here
```

---

## Running the Demo for Judges

### Quick Demo Script (3 minutes)

1. **Start with Text Analysis** (fastest, no API calls)
```bash
python main.py
# Select option 2 (Personal Statement Demo)
```

This will analyze a sample statement and show:
- Extracted skills (15-20)
- Soft skills detected
- Job matches
- Confidence scores

2. **Show Web Interface**
```bash
streamlit run app.py
```

Navigate through:
- Home page (explanation)
- Data Input → Enter a personal statement
- Skill Profile → View radar chart and categories
- Job Matching → See recommendations
- Export → Download profile

3. **GitHub Profile Analysis** (if internet available)
```bash
python main.py
# Select option 1
# Enter username: torvalds (or any GitHub user)
```

---

## File Structure Overview

```
HackNation_2025_SkillSense/
├── app.py                    # Streamlit web app (main demo)
├── main.py                   # CLI interface
├── src/                      # Core modules
│   ├── data_ingestion/       # PDF, GitHub, text processing
│   ├── skill_extraction/     # NLP extraction & scoring
│   ├── profile_generation/   # Profile building
│   └── analysis/             # Job matching
├── config/                   # Skill taxonomy & weights
└── README.md                # Full documentation
```

---

## Testing Each Module

### Test PDF Extraction
```python
from src.data_ingestion.pdf_extractor import PDFExtractor
extractor = PDFExtractor()
# (Requires a PDF file)
```

### Test GitHub Collection
```python
from src.data_ingestion.github_collector import GitHubCollector
collector = GitHubCollector()
profile = collector.get_comprehensive_profile("octocat")
print(profile['extracted_skills']['primary_languages'])
```

### Test Skill Extraction
```python
from src.skill_extraction.skill_extractor import SkillExtractor
extractor = SkillExtractor()
text = "I have experience with Python, React, and machine learning"
skills = extractor.extract_all_skills(text, source='test')
for skill in skills[:5]:
    print(f"{skill.skill_name} ({skill.confidence:.2f})")
```

### Test Job Matching
```python
from src.analysis.job_matcher import JobMatcher
matcher = JobMatcher()
# (Requires a profile with skills)
```

---

## Performance Notes

- **First run**: 30-60 seconds (downloads ML models)
- **Subsequent runs**: 5-10 seconds
- **GitHub analysis**: 10-30 seconds (API calls)
- **PDF processing**: 2-5 seconds per page
- **Text analysis**: < 5 seconds

---

## Hackathon Presentation Tips

1. **Start with the problem**: "70% of skills go unnoticed in traditional hiring"
2. **Show the web interface first** (more visual)
3. **Have a backup**: Pre-loaded demo profile if internet fails
4. **Highlight unique features**: Evidence trails, soft skill analysis
5. **End with SAP alignment**: Enterprise use case, talent mobility

---

## Next Steps After Demo

- Customize skill taxonomy for your industry
- Add more job role templates
- Integrate with your own data sources
- Deploy to cloud (Streamlit Cloud, Heroku)
- Build API endpoints for integration

---

**Need help?** Check [README.md](README.md) for full documentation.
