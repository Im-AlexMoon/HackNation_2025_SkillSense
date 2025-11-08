# 🎯 SkillSense - Unlock Your Hidden Potential

**HackNation 2025 - Corporate Track (SAP Challenge)**

SkillSense is an AI-powered skill extraction and career matching platform that answers the question: **"What am I good at?"**

By analyzing data from multiple sources (CV, GitHub, personal statements, reference letters), SkillSense uses NLP and machine learning to identify both explicit and implicit skills, generate comprehensive skill profiles with confidence scores, and recommend career opportunities with skill gap analysis.

---

## 🌟 Features

### Core Capabilities
- **Multi-Source Data Aggregation**: CV PDFs, GitHub profiles, LinkedIn, personal statements, reference letters
- **AI-Powered Skill Extraction**: Both explicit (keyword matching) and implicit (semantic analysis) skill detection
- **Confidence Scoring**: Source-weighted reliability scores with evidence trails
- **Job Matching**: Match profiles to 10+ job roles with skill gap identification
- **Soft Skill Analysis**: Infer communication and leadership skills from writing samples
- **Interactive Dashboard**: Streamlit web interface with visualizations
- **Export Options**: JSON and text format profile exports

### Distinctive Features
- **Aptitude Analysis**: Writing style analysis for soft skills (communication, leadership)
- **Career Path Recommendations**: Suggest roles based on skill clusters
- **Learning Path Generator**: Personalized upskilling recommendations
- **Evidence-Based Transparency**: Every skill links back to source evidence
- **Multi-Modal Analysis**: Combines technical (GitHub) and soft skills (writing)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- `uv` package manager (or pip)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/HackNation_2025_SkillSense.git
cd HackNation_2025_SkillSense

# Install dependencies
uv sync

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Unix/MacOS
source .venv/bin/activate

# Download spaCy language model (first time only)
python -m spacy download en_core_web_sm
```

### Running the Application

#### Web Interface (Recommended)
```bash
streamlit run app.py
# Or with uv
uv run streamlit run app.py
```

#### CLI Interface
```bash
python main.py
# Or with uv
uv run main.py
```

---

## 📊 Usage Examples

### Example 1: Analyze GitHub Profile
```python
from src.profile_generation.profile_builder import ProfileBuilder

builder = ProfileBuilder()
profile = builder.build_profile(
    name="John Doe",
    github_username="octocat"
)

print(f"Top Skills: {[s.skill_name for s in profile.top_skills[:5]]}")
```

### Example 2: Analyze Personal Statement
```python
statement = """
I am a software engineer with experience in Python, React, and AWS.
I have led teams and delivered complex projects successfully.
"""

profile = builder.build_profile(
    name="Jane Smith",
    personal_statement=statement
)
```

### Example 3: Job Matching
```python
from src.analysis.job_matcher import JobMatcher

matcher = JobMatcher()
matches = matcher.match_profile_to_jobs(profile.skills, top_n=5)

for match in matches:
    print(f"{match.job_title}: {match.match_score*100:.0f}% match")
```

---

## 🏗️ Architecture

```
SkillSense/
├── src/
│   ├── data_ingestion/          # Multi-source data collectors
│   │   ├── pdf_extractor.py     # CV PDF text extraction
│   │   ├── github_collector.py  # GitHub API integration
│   │   └── text_processor.py    # Statement/letter processing
│   │
│   ├── skill_extraction/        # NLP-powered skill detection
│   │   ├── skill_extractor.py   # Explicit & implicit extraction
│   │   └── confidence_scorer.py # Source-weighted scoring
│   │
│   ├── profile_generation/      # Profile building
│   │   └── profile_builder.py   # Multi-source aggregation
│   │
│   └── analysis/                # Advanced features
│       └── job_matcher.py       # Job matching & gap analysis
│
├── config/
│   ├── skill_taxonomy.json      # Standardized skill framework
│   └── source_weights.json      # Confidence scoring weights
│
├── data/                        # Sample data for demos
├── app.py                       # Streamlit web application
└── main.py                      # CLI interface
```

---

## 🔧 Technical Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.13 |
| **NLP** | sentence-transformers, spaCy |
| **PDF Processing** | PyMuPDF |
| **API Integration** | PyGithub |
| **Web Interface** | Streamlit |
| **Visualization** | Plotly |
| **Data Processing** | pandas, numpy |
| **Package Manager** | uv |

---

## 🎯 How It Works

### 1. Data Ingestion
- **PDF Extractor**: Extracts text from CV PDFs with section detection (education, experience, skills)
- **GitHub Collector**: Fetches repos, languages, README files, and activity metrics
- **Text Processor**: Analyzes writing style and extracts soft skill indicators

### 2. Skill Extraction
- **Explicit Detection**: Keyword/phrase matching against skill taxonomy (400+ skills)
- **Contextual Patterns**: Detect skills from phrases like "experience with X", "proficient in Y"
- **Semantic Similarity**: Use sentence embeddings to infer related skills
- **Synonym Mapping**: Recognize variations (JS → JavaScript, ML → Machine Learning)

### 3. Confidence Scoring
- **Source Weighting**: GitHub = 0.95 for technical skills, Personal Statement = 0.85 for soft skills
- **Detection Method**: Explicit mention = 1.0, Semantic = 0.6
- **Multi-Source Bonus**: Up to 20% boost for skills found in multiple sources

### 4. Job Matching
- **Skill Overlap**: Calculate match % based on required vs possessed skills
- **Gap Analysis**: Identify missing critical and beneficial skills
- **Learning Recommendations**: Suggest prioritized upskilling paths

---

## 📈 Demo Scenarios

### Scenario 1: Technical Profile
**Input**: GitHub profile with Python/React repos + CV
**Output**:
- 45 technical skills identified
- Top match: Full Stack Developer (87%)
- Skill gap: TypeScript, Docker

### Scenario 2: Hybrid Profile
**Input**: CV + Personal Statement + GitHub
**Output**:
- 60 total skills (40 technical, 20 soft)
- Top match: Product Manager (78%)
- Strengths: Leadership, Communication, Python

### Scenario 3: Career Transition
**Input**: Data Analyst CV targeting ML Engineer
**Output**:
- Current match: 45%
- Missing: TensorFlow, PyTorch, Deep Learning
- Recommended learning path: Priority skills ranked

---

## 🎓 SAP Challenge Alignment

SkillSense directly addresses the SAP Corporate Track challenge:

- **Skills-Based Talent Management**: Move beyond credentials to actual capabilities
- **Internal Talent Mobility**: Identify experts within organizations
- **Learning & Development**: Generate personalized upskilling paths
- **Team Formation**: Match complementary skill sets for projects
- **Privacy-First**: Local processing, user-controlled data sharing

**Enterprise Use Case**: Deploy internally at SAP to:
1. Discover hidden experts across departments
2. Match employees to internal opportunities
3. Identify organization-wide skill gaps
4. Support SuccessFactors Skills Ontology integration

---

## 🔐 Privacy & Ethics

- **Local Processing**: All skill extraction runs locally (no data sent to external APIs except GitHub)
- **Data Minimization**: Only analyze explicitly provided information
- **User Control**: Toggle visibility of data sources in profile
- **Explainability**: Every skill shows evidence trail ("Python inferred from project X")
- **Bias Awareness**: Confidence scores acknowledge source reliability differences

---

## 🚧 Future Enhancements

- [ ] LinkedIn API integration (currently simulated)
- [ ] Portfolio website scraping
- [ ] Video interview analysis (speech-to-text + sentiment)
- [ ] Team compatibility scoring
- [ ] Integration with SAP SuccessFactors
- [ ] Multi-language support
- [ ] Chrome extension for one-click analysis
- [ ] API endpoints for enterprise integration

---

## 🏆 Competition Highlights

### Why SkillSense Wins

1. **Comprehensive Multi-Source Analysis**: Not just CV parsing - GitHub + writing + references
2. **Explainable AI**: Confidence scores + evidence trails = trustworthy results
3. **Actionable Insights**: Not just "what you know" but "where to go next"
4. **Enterprise-Ready**: Privacy-conscious, SAP-aligned, scalable architecture
5. **Polished Demo**: Interactive Streamlit UI + CLI + pre-loaded examples

### Demo Flow (5 minutes)

1. **Introduction** (30s): Problem statement - hidden skills go unnoticed
2. **Live Demo** (3m): Upload CV + GitHub → Skill extraction → Job matches
3. **Unique Features** (1m): Soft skill analysis, evidence trails, learning paths
4. **Enterprise Value** (30s): SAP integration potential, talent mobility

---

## 👥 Team

Built for HackNation 2025 by [Your Team Name]

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

- HackNation 2025 organizers
- SAP for the Corporate Track challenge
- Open-source NLP community (Hugging Face, spaCy)
- Sample data contributors

---

**SkillSense - Because your potential deserves to be discovered.**
