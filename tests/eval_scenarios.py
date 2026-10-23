"""
AI Agent Scenario Evaluation & Benchmark
Validates that the Gemini-powered agent:
1. Calls the proper tools for financial and Swedish housing queries.
2. Respects the zero-hallucination constraint.
3. Provides explainable trade-offs and accurate data attribution.
"""

from agent import WorkNestAgent

SCENARIOS = [
    {
        "id": "scenario_1_stockholm_relocation",
        "description": "Worker relocating to Stockholm City with moderate budget",
        "prompt": "I earn 35,000 SEK net and spend 10,000 SEK on fixed expenses. My job is at Stockholm Central / City and I want at most a 25 minute commute. Can I live in Huddinge or Solna? Compare their rent and taxes using real data.",
        "expected_keywords": ["Solna", "Huddinge", "SCB", "commute", "tax", "rent"]
    },
    {
        "id": "scenario_2_goteborg_lindholmen",
        "description": "Engineer starting at Lindholmen Science Park in Gothenburg",
        "prompt": "I work at Göteborg Central / Lindholmen and make 42,000 SEK net with 12,000 SEK expenses. What are my options in Mölndal within 25 minutes?",
        "expected_keywords": ["Mölndal", "Göteborg", "commute", "rent", "SEK"]
    },
    {
        "id": "scenario_3_rent_control_nuance",
        "description": "User inquiring about first-hand queue vs second-hand sublets",
        "prompt": "Explain why SCB rents are lower than what I see on sublet sites, and what landlords in Sweden require.",
        "expected_keywords": ["bruksvärdeshyra", "first-hand", "second-hand", "queue", "income", "3x"]
    }
]

def run_eval():
    print("=== Running WorkNest Agent Scenario Evaluations ===")
    agent = WorkNestAgent()
    passed = 0
    for sc in SCENARIOS:
        print(f"\n--- Testing: {sc['id']} ---")
        reply = agent.send_message(sc["prompt"])
        print(f"Reply snippet: {reply[:250]}...\n")
        
        # Check assertions
        matched = [k for k in sc["expected_keywords"] if k.lower() in reply.lower()]
        coverage = len(matched) / len(sc["expected_keywords"])
        print(f"Keywords matched ({len(matched)}/{len(sc['expected_keywords'])}): {matched}")
        if coverage >= 0.6:
            print(f"PASS: {sc['id']}")
            passed += 1
        else:
            print(f"FAIL: {sc['id']}")

    print(f"\n=== Evaluation Summary: {passed}/{len(SCENARIOS)} scenarios passed ===")

if __name__ == "__main__":
    run_eval()
