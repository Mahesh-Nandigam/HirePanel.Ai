import json
from src.agents.github_agent import GitHubAgent

def run_tests():
    agent = GitHubAgent()
    
    test_urls = [
        "https://github.com/torvalds",
        "https://github.com/kamranahmedse",
        "https://github.com/this-user-does-not-exist-123456789"
    ]
    
    for url in test_urls:
        print("="*80)
        print(f"TESTING URL: {url}")
        print("="*80)
        
        username = agent.extract_username(url)
        print(f"Extracted Username: {username}")
        
        print("\n--- Fetching Raw Data ---")
        raw_data = agent.fetch_github_data(username)
        
        # We only print the high-level keys to save console space
        # but we print some of the core profile metrics
        if raw_data.get('profile'):
            print("Profile Data:", {
                "followers": raw_data['profile'].get('followers'),
                "public_repos": raw_data['profile'].get('public_repos')
            })
            print(f"Repositories Fetched: {len(raw_data.get('repositories', []))}")
            print(f"Recent Events Fetched: {raw_data.get('recent_activity', {}).get('total_recent_events', 0)}")
        else:
            print("RAW DATA: None (API Limit or Invalid User)")
            
        print("\n--- Running Gemini Evaluation ---")
        result = agent.evaluate_profile(url)
        print(json.dumps(result, indent=2))
        
        # Determine Pass/Fail based on expected behavior
        if "does-not-exist" in url:
            if result.get("github_score") == 0.0:
                print("\n[PASS] (Graceful Fallback)")
            else:
                print("\n[FAIL] (Should have returned 0.0)")
        else:
            if result.get("github_score", 0) > 0:
                print("\n[PASS] (Valid Profile Score Generated)")
            else:
                print("\n[FAIL] (Score was 0.0 - check API limits)")
                
        print("\n\n")

if __name__ == "__main__":
    run_tests()
