# SkillSense RAG System Guide

## 🎯 Overview

The **Employer Q&A** feature uses Retrieval-Augmented Generation (RAG) to allow employers to ask natural language questions about candidate profiles.

**Example Questions:**
- "Does this candidate have Kubernetes experience?"
- "What are their leadership qualities?"
- "How experienced are they with Python?"
- "Is this candidate suitable for a Senior Developer role?"

---

## 🚀 Quick Start

### 1. Build a Candidate Profile

First, create a profile using the **Data Input** page:
- Upload a CV (PDF)
- Connect GitHub account
- Provide personal statement

### 2. Navigate to Employer Q&A

Click **💬 Employer Q&A** in the sidebar navigation.

### 3. Ask Questions

Type your question in the chat box or click a quick question template.

---

## ⚙️ Configuration

### LLM Providers

Choose from three providers in the sidebar:

| Provider | Cost | Speed | Quality | API Key Required? |
|----------|------|-------|---------|-------------------|
| **Gemini** | Free | Fast | Good | Optional |
| **OpenAI** | $0.38/1K queries | Fast | Excellent | Yes |
| **Anthropic** | $3/1K queries | Medium | Excellent | Yes |

**Recommended**: Start with Gemini (free tier, no API key needed for basic use)

### API Key Setup

**Option 1: Environment Variable** (Recommended)
```bash
# Create .env file in project root
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

**Option 2: Streamlit UI**
- Expand "⚙️ API Configuration" in sidebar
- Enter API key in password field
- Keys are session-only (not saved)

### Get API Keys

**Google Gemini (Free):**
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Get API Key"
3. Create new key or use existing

**OpenAI:**
1. Visit: https://platform.openai.com/api-keys
2. Create new secret key
3. Add $5-10 credit to account

**Anthropic Claude:**
1. Visit: https://console.anthropic.com/
2. Get API key from settings
3. Add credits if needed

---

## 💡 How It Works

### RAG Architecture

```
User Question
     ↓
Vector Search (FAISS)
     ↓
Retrieve Relevant Skill Data
     ↓
Context + Question → LLM
     ↓
Answer with Citations
```

### What Gets Indexed?

1. **Skills** (40-60 per profile)
   - Skill name, category, confidence
   - Evidence from all sources
   - Source attribution

2. **CV Text** (chunked)
   - Work experience
   - Education
   - Projects

3. **GitHub Data**
   - Repository descriptions
   - Languages used
   - Topics/technologies

4. **Personal Statements**
   - Full text
   - Writing analysis

### Confidence Scores

Answers include confidence levels based on:
- **Source Reliability**: GitHub (0.95) > CV (0.80) > Statement (0.70)
- **Detection Method**: Explicit (1.0) > Contextual (0.80) > Semantic (0.60)
- **Multi-Source Bonus**: Skills found in multiple sources get +20%

---

## 📚 Features

### Chat Interface

- **Multi-turn conversations**: Ask follow-up questions
- **Conversation history**: See previous Q&A
- **Reset button**: Clear conversation and start fresh

### Evidence Citations

Every answer includes:
- Source type (CV, GitHub, personal statement)
- Specific text excerpts
- Similarity scores (optional)
- Confidence levels for skills

**Example:**
```
Q: Does this candidate have Python experience?

A: Yes, this candidate has strong Python experience with high confidence (0.92).

Evidence:
[1] Skill: Python (Confidence: 0.92)
    Sources: GitHub, CV
    Found in 15 GitHub repositories...

[2] CV Text
    "5 years of Python development experience, including Django and Flask..."
```

### Quick Question Templates

Pre-built questions organized by category:

- **Technical Skills**: "What programming languages do they know?"
- **Soft Skills**: "What are their leadership qualities?"
- **Experience**: "What projects have they worked on?"
- **Role Fit**: "Is this candidate suitable for a Senior Developer role?"
- **Evidence**: "Show me evidence of their technical abilities"

---

## 🎯 Use Cases

### 1. Skill Verification

**Question**: "Does this candidate have Kubernetes experience?"

**What RAG does**:
- Searches for Kubernetes mentions
- Checks GitHub repos for K8s usage
- Reviews CV for keywords
- Returns confidence score + evidence

### 2. Role Fit Assessment

**Question**: "Is this candidate suitable for a Full Stack Developer role?"

**What RAG does**:
- Compares skills vs Full Stack requirements
- Identifies matched skills (React, Node.js, SQL)
- Lists missing skills (TypeScript, Docker)
- Provides recommendation

### 3. Soft Skill Analysis

**Question**: "What are their leadership qualities?"

**What RAG does**:
- Analyzes writing style from personal statement
- Searches for leadership indicators ("led team", "managed")
- Reviews reference letter for endorsements
- Synthesizes findings

### 4. Evidence Requests

**Question**: "Show me proof of their React experience"

**What RAG does**:
- Retrieves GitHub repos using React
- Finds CV mentions
- Extracts project descriptions
- Provides direct links/quotes

---

## 🔧 Advanced Settings

### Show Evidence Citations

Toggle to show/hide source information with each answer.

**When to use**:
- ✅ Enable for important hiring decisions (verify claims)
- ❌ Disable for quick exploratory questions

### Show Similarity Scores

Display semantic similarity between question and retrieved documents.

**When to use**:
- Debugging why certain information was retrieved
- Understanding relevance of sources

### Conversation Reset

Clear chat history and start fresh.

**When to use**:
- Switching to analyze different candidate
- Starting new line of questioning

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Indexing Time** | 5-15 seconds (one-time per profile) |
| **Query Time** | 2-5 seconds |
| **Accuracy** | 85-95% (depends on profile quality) |
| **Context Window** | Last 3 conversation turns |
| **Max Documents** | 5-10 per query |

---

## ⚠️ Limitations & Best Practices

### Limitations

1. **Data Dependency**: Quality of answers depends on profile completeness
2. **No External Knowledge**: LLM cannot add information beyond profile
3. **Hallucination Risk**: Rare, but LLM may occasionally infer incorrectly
4. **API Rate Limits**: Free tiers have usage caps

### Best Practices

✅ **DO:**
- Build comprehensive profiles (CV + GitHub + statement)
- Verify critical claims using evidence citations
- Use specific questions ("Python experience?" not "tell me about them")
- Reset conversation when switching candidates

❌ **DON'T:**
- Rely solely on RAG for hiring decisions (use as supplement)
- Assume absence of mention = absence of skill
- Ask questions outside candidate domain (e.g., "What's the weather?")
- Share API keys publicly

---

## 🐛 Troubleshooting

### "Error initializing RAG system"

**Cause**: Missing or invalid API key

**Fix**:
1. Check API key is entered correctly
2. Try Gemini (doesn't require key for basic use)
3. Verify API key has credits/quota

### "No relevant information found"

**Cause**: Profile lacks data on topic

**Fix**:
1. Build more comprehensive profile
2. Rephrase question to match profile content
3. Check if skill exists in profile (Skill Profile page)

### "API rate limit exceeded"

**Cause**: Too many requests to free tier

**Fix**:
1. Wait 60 seconds
2. Upgrade to paid tier
3. Switch to different provider

### Slow responses

**Cause**: First query downloads ML models

**Fix**:
- Normal on first use (30-60s)
- Subsequent queries are fast (<5s)
- Models cached automatically

---

## 🔐 Privacy & Security

### Data Handling

- **Local Processing**: Skill extraction runs locally
- **API Transmission**: Only query + retrieved context sent to LLM
- **No Storage**: LLM providers don't store queries (per ToS)
- **Session-Only**: API keys in UI not persisted

### What's Shared with LLM?

**Sent**:
- Your question
- Relevant skill snippets (5-10)
- Profile summary

**NOT Sent**:
- Full CV text
- Complete profile
- Personal identifiable information (if redacted)

### Best Practices

- Use environment variables for API keys
- Don't share `.env` file
- Review evidence before making decisions
- Clear conversation when done

---

## 📈 Future Enhancements

Planned features:

- [ ] Multi-candidate comparison
- [ ] Export chat transcripts
- [ ] Custom job role templates
- [ ] Batch question processing
- [ ] Advanced filtering (confidence thresholds)
- [ ] Integration with ATS systems

---

## 📞 Support

**Issues**: https://github.com/yourusername/SkillSense/issues

**Documentation**: See README.md for general SkillSense docs

**RAG Specific Questions**: Check this guide first

---

**SkillSense RAG - Empowering data-driven hiring decisions!** 🎯
