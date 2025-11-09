# SkillSense Documentation

Welcome to the SkillSense RAG System documentation. This folder contains all the guides, troubleshooting resources, and technical documentation for the project.

## 📖 Getting Started

**Start here if you're new to SkillSense:**
- [TESTING_READY.md](TESTING_READY.md) - How to test the system and run it locally
- [RAG_GUIDE.md](RAG_GUIDE.md) - User guide for the RAG (Employer Q&A) features

## 🚀 Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Start the application
streamlit run app.py

# 3. Create a candidate profile (go to "Data Input" page)
# 4. Navigate to "Employer Q&A" page
# 5. Ask questions about the candidate
```

## 📚 Documentation Index

### For Users
- **[TESTING_READY.md](TESTING_READY.md)** - Complete testing guide with examples
- **[RAG_GUIDE.md](RAG_GUIDE.md)** - User guide for the Employer Q&A feature
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solutions for common issues

### For Developers
- **[RAG_IMPLEMENTATION_SUMMARY.md](RAG_IMPLEMENTATION_SUMMARY.md)** - Technical architecture and design
- **[STATUS.md](STATUS.md)** - Project status and feature overview
- **[DEBUG_SESSION_COMPLETE.md](DEBUG_SESSION_COMPLETE.md)** - Complete debugging log

### Bug Fixes & Known Issues
- **[GEMINI_RETRYERROR_FIXED.md](GEMINI_RETRYERROR_FIXED.md)** - RetryError fix summary
- **[GEMINI_FIX_SUMMARY.md](GEMINI_FIX_SUMMARY.md)** - Technical analysis of Gemini fixes
- **[GEMINI_RETRY_ERROR_FIX.md](GEMINI_RETRY_ERROR_FIX.md)** - Comprehensive error analysis
- **[DEBUG_FIXES_SUMMARY.md](DEBUG_FIXES_SUMMARY.md)** - Initial bug fixes summary

## 🎯 What is SkillSense?

SkillSense is an AI-powered platform that:
1. **Extracts Skills** from CVs, GitHub, and personal statements
2. **Analyzes Profiles** with machine learning and NLP
3. **Powers Q&A** with RAG (Retrieval-Augmented Generation)

Employers can ask natural language questions about candidates and get evidence-based answers with citations.

## ✨ Key Features

### Skill Extraction
- Automated skill detection from multiple sources
- Confidence scoring
- Category classification

### Job Matching
- Role fit assessment
- Skill gap analysis
- Recommendations

### Employer Q&A (RAG)
- Natural language questions: "Does this candidate have Python experience?"
- Evidence-based answers with citations
- Multi-turn conversations
- Multiple LLM providers (Gemini, OpenAI, Anthropic)

## 🔐 API Configuration

The system uses free LLM APIs by default:

```bash
# Required: Get a free Gemini API key
# Visit: https://makersuite.google.com/app/apikey
# Add to .env file:
GEMINI_API_KEY=your-key-here

# Optional: Add OpenAI or Anthropic keys
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
```

## 🐛 Common Issues

### "RetryError" or "API key not found"
→ See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### "Cannot initialize RAG system: Profile has no indexable data"
→ Create a candidate profile first in the "Data Input" page

### "First query is very slow"
→ Normal - models are downloading (~50MB). Subsequent queries are fast!

## 📊 Project Structure

```
SkillSense/
├── docs/                          # Documentation (this folder)
│   ├── README.md                 # You are here
│   ├── TESTING_READY.md          # How to test
│   ├── RAG_GUIDE.md              # User guide
│   ├── TROUBLESHOOTING.md        # Common issues
│   └── ... (other guides)
│
├── src/                           # Source code
│   ├── rag/                       # RAG system
│   │   ├── vector_store.py       # Semantic search
│   │   ├── llm_client.py         # Multi-provider LLM
│   │   ├── rag_system.py         # RAG orchestrator
│   │   └── prompts.py            # Prompt templates
│   ├── skill_extraction/          # Skill extraction
│   ├── profile_generation/        # Profile building
│   ├── data_ingestion/            # CV/GitHub parsing
│   └── analysis/                  # Job matching
│
├── app.py                         # Main Streamlit application
├── .env                           # API key configuration (not in git)
├── .env.example                   # Template for .env
├── .gitignore                     # Git ignore rules
└── README.md                      # Project readme
```

## 🧪 Testing

### Run All Tests
```bash
uv run python verify_gemini_fix.py
```

### Expected Output
```
*** ALL TESTS PASSED! ***
The Gemini API RetryError fix is working correctly.
```

## 📞 Need Help?

1. **Check the relevant guide** (see index above)
2. **Search [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**
3. **Review error messages** - they now include helpful guidance!
4. **Check git log** - recent commits explain changes

## 🚀 Next Steps

### For First-Time Users
1. Read [TESTING_READY.md](TESTING_READY.md)
2. Start the app with `streamlit run app.py`
3. Create a test profile
4. Test the Employer Q&A feature

### For Developers
1. Review [RAG_IMPLEMENTATION_SUMMARY.md](RAG_IMPLEMENTATION_SUMMARY.md)
2. Check [STATUS.md](STATUS.md) for architecture
3. Review [src/rag/](../src/rag/) code

### For Debugging
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [DEBUG_SESSION_COMPLETE.md](DEBUG_SESSION_COMPLETE.md)
3. Run test suite with `uv run python verify_gemini_fix.py`

## 📈 Performance Tips

- **First query**: 30-60 seconds (models download once)
- **Subsequent queries**: 2-5 seconds
- **Rate limits**: Gemini free tier has daily limits
- **Large profiles**: May take longer to index

## 🔮 Future Features

- Multi-candidate comparison
- Export chat transcripts
- Custom job role templates
- SAP SuccessFactors integration

## 📝 License

[Add your license here]

## 👥 Contributing

[Add contribution guidelines here]

---

**Happy testing! 🎉**

For questions or issues, check the relevant documentation above or review error messages carefully - they now include helpful guidance!
