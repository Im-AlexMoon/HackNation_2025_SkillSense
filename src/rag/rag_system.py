"""
RAG System
Main orchestrator for Retrieval-Augmented Generation on candidate profiles
"""
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from rag.vector_store import FAISSVectorStore
from rag.llm_client import LLMClient
from rag.prompts import SYSTEM_PROMPT, format_user_prompt


class RAGSystem:
    """RAG system for candidate profile Q&A"""

    def __init__(self, profile, llm_provider: str = "gemini", api_key: Optional[str] = None):
        """
        Initialize RAG system with a candidate profile

        Args:
            profile: SkillProfile object
            llm_provider: LLM provider to use ("gemini", "openai", "anthropic")
            api_key: Optional API key
        """
        self.profile = profile
        self.vector_store = FAISSVectorStore()
        self.llm = LLMClient(provider=llm_provider, api_key=api_key)
        self.conversation_history = []

        print(f"\nInitializing RAG system with {llm_provider}...")
        self._index_profile()

    def _index_profile(self):
        """Index profile data for semantic search"""
        documents = []
        metadatas = []

        # Index skills
        if hasattr(self.profile, 'skills') and self.profile.skills:
            print(f"   Indexing {len(self.profile.skills)} skills...")
            for skill in self.profile.skills:
                text = self._skill_to_text(skill)
                documents.append(text)
                metadatas.append({
                    "type": "skill",
                    "skill_name": skill.skill_name,
                    "confidence": skill.final_confidence,
                    "category": skill.category,
                    "sources": skill.sources
                })

        # Index raw data sources
        if hasattr(self.profile, 'raw_data') and isinstance(self.profile.raw_data, dict):
            # Index CV data
            if 'cv' in self.profile.raw_data:
                cv_data = self.profile.raw_data.get('cv', {})
                if isinstance(cv_data, dict) and cv_data.get('raw_text'):
                    raw_text = cv_data['raw_text']
                    if isinstance(raw_text, str) and raw_text.strip():
                        chunks = self._chunk_text(raw_text, chunk_size=400)
                        print(f"   Indexing {len(chunks)} CV chunks...")
                        for i, chunk in enumerate(chunks):
                            documents.append(chunk)
                            metadatas.append({
                                "type": "cv_text",
                                "source": "cv",
                                "chunk_id": i
                            })

            # Index GitHub data
            if 'github' in self.profile.raw_data:
                github_data = self.profile.raw_data.get('github', {})
                if isinstance(github_data, dict):
                    repos = github_data.get('repositories', [])
                    # Validate repos is a list
                    if isinstance(repos, list) and repos:
                        print(f"   Indexing {len(repos)} GitHub repositories...")
                        for repo in repos[:10]:  # Limit to top 10
                            if isinstance(repo, dict):
                                repo_text = f"{repo.get('name', '')}: {repo.get('description', '')}. "
                                languages = repo.get('languages', [])
                                if isinstance(languages, list):
                                    repo_text += f"Languages: {', '.join(languages)}. "
                                topics = repo.get('topics', [])
                                if isinstance(topics, list):
                                    repo_text += f"Topics: {', '.join(topics)}"
                                documents.append(repo_text)
                                metadatas.append({
                                    "type": "github_repo",
                                    "source": "github",
                                    "repo_name": repo.get('name', '')
                                })

            # Index personal statement
            if 'personal_statement' in self.profile.raw_data:
                statement_data = self.profile.raw_data.get('personal_statement', {})
                if isinstance(statement_data, dict):
                    content = statement_data.get('content', '')
                    if isinstance(content, str) and content.strip():
                        documents.append(content)
                        metadatas.append({
                            "type": "personal_statement",
                            "source": "personal_statement"
                        })

        # Add to vector store
        if documents:
            self.vector_store.add_documents(documents, metadatas)
            print(f"   RAG system ready with {len(documents)} indexed documents")
        else:
            # Raise error if no documents found
            raise ValueError(
                "Cannot initialize RAG system: Profile has no indexable data. "
                "Please ensure the profile has skills, CV text, GitHub data, or a personal statement."
            )

    def _skill_to_text(self, skill) -> str:
        """Convert skill object to searchable text"""
        text_parts = [
            f"Skill: {skill.skill_name}",
            f"Category: {skill.category}",
            f"Confidence: {skill.final_confidence:.2f}",
            f"Sources: {', '.join(skill.sources)}"
        ]

        if skill.evidence:
            # Add top 3 evidence snippets
            evidence_text = " ".join(skill.evidence[:3])
            text_parts.append(f"Evidence: {evidence_text}")

        return ". ".join(text_parts)

    def _chunk_text(self, text: str, chunk_size: int = 400) -> List[str]:
        """Split text into chunks"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)

        return chunks

    def query(self, question: str, k: int = 5) -> Tuple[str, List[Dict]]:
        """
        Query the candidate profile

        Args:
            question: Employer's question
            k: Number of relevant documents to retrieve

        Returns:
            Tuple of (answer, sources)
        """
        # Retrieve relevant context
        results = self.vector_store.search(question, k=k)

        if not results:
            return "No relevant information found in candidate profile.", []

        # Format context
        context = self._format_context(results)

        # Build conversation history (last 3 exchanges)
        conv_history = self._build_conversation_history(max_turns=3)

        # Generate answer
        user_prompt = format_user_prompt(
            question=question,
            context=context,
            profile_summary=self.profile.summary,
            conversation_history=conv_history
        )

        try:
            answer = self.llm.generate(SYSTEM_PROMPT, user_prompt, temperature=0.3)
        except Exception as e:
            answer = f"Error generating response: {str(e)}\n\nPlease check your API key configuration."

        # Extract sources for citations
        sources = self._extract_sources(results)

        # Update conversation history
        self.conversation_history.append({
            "role": "user",
            "content": question
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        return answer, sources

    def _format_context(self, results: List[Dict]) -> str:
        """Format retrieved documents into context"""
        context_parts = []

        for i, doc in enumerate(results, 1):
            doc_type = doc['metadata'].get('type', 'unknown')
            text = doc['text']

            # Format based on document type
            if doc_type == 'skill':
                skill_name = doc['metadata'].get('skill_name', 'Unknown')
                confidence = doc['metadata'].get('confidence', 0)
                context_parts.append(f"[{i}] {skill_name} (Confidence: {confidence:.2f})")
                context_parts.append(f"    {text[:200]}...")

            else:
                source = doc['metadata'].get('source', 'unknown')
                context_parts.append(f"[{i}] Source: {source}")
                context_parts.append(f"    {text[:300]}...")

            context_parts.append("")  # Blank line

        return "\n".join(context_parts)

    def _extract_sources(self, results: List[Dict]) -> List[Dict]:
        """Extract source information for citations"""
        sources = []

        for doc in results:
            metadata = doc['metadata']
            doc_type = metadata.get('type', 'unknown')

            source_info = {
                "type": doc_type,
                "text": doc['text'][:200] + "..." if len(doc['text']) > 200 else doc['text'],
                "similarity": doc.get('similarity', 0),
                "metadata": metadata
            }

            # Add specific details based on type
            if doc_type == 'skill':
                source_info['skill_name'] = metadata.get('skill_name')
                source_info['confidence'] = metadata.get('confidence')
                source_info['source_list'] = metadata.get('sources', [])

            elif doc_type == 'github_repo':
                source_info['repo_name'] = metadata.get('repo_name')

            sources.append(source_info)

        return sources

    def _build_conversation_history(self, max_turns: int = 3) -> Optional[str]:
        """Build conversation history string"""
        if not self.conversation_history:
            return None

        # Get last N turns (each turn = user + assistant)
        recent_messages = self.conversation_history[-(max_turns * 2):]

        history_parts = []
        for msg in recent_messages:
            role = msg['role'].upper()
            content = msg['content'][:150]  # Truncate for context window
            history_parts.append(f"{role}: {content}...")

        return "\n".join(history_parts)

    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_stats(self) -> Dict:
        """Get RAG system statistics"""
        return {
            "profile_name": self.profile.name,
            "total_skills": len(self.profile.skills),
            "data_sources": self.profile.data_sources,
            "vector_store": self.vector_store.get_stats(),
            "conversation_turns": len(self.conversation_history) // 2,
            "llm_provider": self.llm.provider
        }


# Example usage
if __name__ == "__main__":
    print("RAG System module loaded")
    print("\nTo use:")
    print("  from rag.rag_system import RAGSystem")
    print("  rag = RAGSystem(profile, llm_provider='gemini')")
    print("  answer, sources = rag.query('Does candidate know Python?')")
