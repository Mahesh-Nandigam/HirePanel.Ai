import json
from src.agents.github_agent import GitHubAgent

class MockGitHubAgent(GitHubAgent):
    def __init__(self, mock_data):
        super().__init__()
        self.mock_data = mock_data
        
    def fetch_github_data(self, username: str) -> dict:
        # Override the API fetcher to return our custom mock data
        return self.mock_data

def run_tests():
    # Test Case 1 — Empty Profile / Student Profile
    test_1_data = {
        "profile": {
            "followers": 2, 
            "public_repos": 3
        },
        "repositories": [
            {"name": "hello-world", "stars": 0, "fork": False, "language": "Python", "description": "My first project"}
        ],
        "recent_activity": {
            "total_recent_events": 1,
            "recent_pushes": 1,
            "recent_pull_requests": 0
        }
    }

    # Test Case 2 — Contradictory Superstar Profile
    test_2_data = {
        "profile": {
            "followers": 1200, 
            "public_repos": 150
        },
        "repositories": [
            {"name": "huge-open-source", "stars": 5000, "fork": False, "language": "Go", "description": "Massive framework"},
            {"name": "python-utils", "stars": 1500, "fork": False, "language": "Python", "description": ""},
            {"name": "ts-lib", "stars": 800, "fork": False, "language": "TypeScript", "description": ""}
        ],
        "recent_activity": {
            "total_recent_events": 0,
            "recent_pushes": 0,
            "recent_pull_requests": 0
        }
    }

    print("================================================================================")
    print("TEST CASE 1: Empty / Student Profile")
    print("================================================================================")
    agent_1 = MockGitHubAgent(test_1_data)
    result_1 = agent_1.evaluate_profile("https://github.com/student-dev")
    print(json.dumps(result_1, indent=2))
    
    print("\n\n")
    print("================================================================================")
    print("TEST CASE 2: Contradictory Superstar (Zero Recent Activity)")
    print("================================================================================")
    agent_2 = MockGitHubAgent(test_2_data)
    result_2 = agent_2.evaluate_profile("https://github.com/burnt-out-superstar")
    print(json.dumps(result_2, indent=2))

if __name__ == "__main__":
    run_tests()
