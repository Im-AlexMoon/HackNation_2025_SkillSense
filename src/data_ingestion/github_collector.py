"""
GitHub Collector Module
Collects repository data, languages, and project information from GitHub
"""
from github import Github, GithubException
from typing import Dict, List, Optional
from dataclasses import dataclass
import os
from datetime import datetime


@dataclass
class GitHubRepo:
    """Represents a GitHub repository"""
    name: str
    description: Optional[str]
    languages: Dict[str, int]  # Language -> bytes of code
    topics: List[str]
    stars: int
    forks: int
    url: str
    readme: Optional[str]
    created_at: datetime
    updated_at: datetime


class GitHubCollector:
    """Collects and structures data from GitHub profiles"""

    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize GitHub API client

        Args:
            access_token: GitHub personal access token (optional, but recommended for higher rate limits)
        """
        if access_token:
            self.github = Github(access_token)
        else:
            # Use unauthenticated access (lower rate limit)
            self.github = Github()

    def get_user_profile(self, username: str) -> Dict[str, any]:
        """
        Get GitHub user profile information

        Args:
            username: GitHub username

        Returns:
            Dictionary with user profile data
        """
        try:
            user = self.github.get_user(username)

            profile_data = {
                'username': user.login,
                'name': user.name,
                'bio': user.bio,
                'location': user.location,
                'email': user.email,
                'blog': user.blog,
                'company': user.company,
                'followers': user.followers,
                'following': user.following,
                'public_repos': user.public_repos,
                'created_at': user.created_at,
                'updated_at': user.updated_at
            }

            return profile_data

        except GithubException as e:
            raise Exception(f"Error fetching GitHub profile for {username}: {str(e)}")

    def get_user_repositories(self, username: str, max_repos: int = 30) -> List[GitHubRepo]:
        """
        Get user's public repositories with details

        Args:
            username: GitHub username
            max_repos: Maximum number of repositories to fetch

        Returns:
            List of GitHubRepo objects
        """
        try:
            user = self.github.get_user(username)
            repos = user.get_repos(type='owner', sort='updated', direction='desc')

            repo_list = []
            count = 0

            for repo in repos:
                if count >= max_repos:
                    break

                # Skip forks if desired (can be configurable)
                if repo.fork:
                    continue

                # Get README content
                readme_content = None
                try:
                    readme = repo.get_readme()
                    readme_content = readme.decoded_content.decode('utf-8')
                except:
                    pass  # README doesn't exist or can't be read

                # Get languages
                languages = repo.get_languages()

                repo_data = GitHubRepo(
                    name=repo.name,
                    description=repo.description,
                    languages=languages,
                    topics=repo.get_topics(),
                    stars=repo.stargazers_count,
                    forks=repo.forks_count,
                    url=repo.html_url,
                    readme=readme_content,
                    created_at=repo.created_at,
                    updated_at=repo.updated_at
                )

                repo_list.append(repo_data)
                count += 1

            return repo_list

        except GithubException as e:
            raise Exception(f"Error fetching repositories for {username}: {str(e)}")

    def extract_skills_from_repos(self, repos: List[GitHubRepo]) -> Dict[str, any]:
        """
        Extract skills and insights from repository data

        Args:
            repos: List of GitHubRepo objects

        Returns:
            Dictionary with extracted skills and insights
        """
        # Aggregate languages
        language_stats = {}
        all_topics = []
        total_stars = 0
        total_forks = 0
        project_descriptions = []

        for repo in repos:
            # Aggregate languages
            for lang, bytes_count in repo.languages.items():
                if lang in language_stats:
                    language_stats[lang] += bytes_count
                else:
                    language_stats[lang] = bytes_count

            # Collect topics
            all_topics.extend(repo.topics)

            # Stats
            total_stars += repo.stars
            total_forks += repo.forks

            # Project descriptions
            if repo.description:
                project_descriptions.append({
                    'name': repo.name,
                    'description': repo.description,
                    'url': repo.url
                })

        # Calculate language percentages
        total_bytes = sum(language_stats.values())
        language_percentages = {
            lang: (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
            for lang, bytes_count in language_stats.items()
        }

        # Sort languages by usage
        sorted_languages = sorted(
            language_percentages.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Get unique topics
        unique_topics = list(set(all_topics))

        return {
            'primary_languages': [lang for lang, _ in sorted_languages[:5]],
            'language_distribution': dict(sorted_languages),
            'topics': unique_topics,
            'total_repositories': len(repos),
            'total_stars': total_stars,
            'total_forks': total_forks,
            'project_descriptions': project_descriptions,
            'activity_metrics': {
                'avg_stars_per_repo': total_stars / len(repos) if repos else 0,
                'avg_forks_per_repo': total_forks / len(repos) if repos else 0
            }
        }

    def get_comprehensive_profile(self, username: str) -> Dict[str, any]:
        """
        Get comprehensive GitHub profile with repos and extracted skills

        Args:
            username: GitHub username

        Returns:
            Dictionary with complete profile data
        """
        profile = self.get_user_profile(username)
        repos = self.get_user_repositories(username)
        skills = self.extract_skills_from_repos(repos)

        return {
            'source': 'github',
            'profile': profile,
            'repositories': [
                {
                    'name': repo.name,
                    'description': repo.description,
                    'languages': list(repo.languages.keys()),
                    'topics': repo.topics,
                    'url': repo.url,
                    'stars': repo.stars
                }
                for repo in repos
            ],
            'extracted_skills': skills,
            'metadata': {
                'fetched_at': datetime.now().isoformat(),
                'username': username
            }
        }


# Example usage
if __name__ == "__main__":
    # Example: Fetch GitHub data
    # collector = GitHubCollector()  # Or pass access_token for higher limits
    # profile = collector.get_comprehensive_profile("octocat")
    # print(f"Languages: {profile['extracted_skills']['primary_languages']}")
    # print(f"Total repos: {profile['extracted_skills']['total_repositories']}")

    print("GitHub Collector module loaded successfully")
