import json
import uuid
import requests

from backend.memory.memory_store import save_memory

SCENARIO_FILE = "evaluations/scenarios.json"
OUTPUT_FILE = "evaluations/baseline_results.json"
API_URL = "http://127.0.0.1:8000/chat"


def run_scenario(scenario):
    user_id = f"eval_{uuid.uuid4().hex[:8]}"
    session_id = f"session_{uuid.uuid4().hex[:8]}"

    for memory in scenario["memories"]:
        save_memory(user_id, memory)

    try:
        response = requests.post(
            API_URL,
            json={
                "user_id": user_id,
                "session_id": session_id,
                "message": scenario["query"]
            },
            timeout=120
        )

        response.raise_for_status()

        return {
            "id": scenario["id"],
            "description": scenario["description"],
            "query": scenario["query"],
            "expected": scenario["expected"],
            "response": response.json()["response"],
            "status": "success"
        }

    except requests.RequestException as error:
        return {
            "id": scenario["id"],
            "description": scenario["description"],
            "query": scenario["query"],
            "expected": scenario["expected"],
            "response": "",
            "status": "failed",
            "error": str(error)
        }


def main():
    with open(SCENARIO_FILE, "r") as file:
        scenarios = json.load(file)

    results = []

    for scenario in scenarios:
        print(f"Running {scenario['id']}...")

        result = run_scenario(scenario)
        results.append(result)

        if result["status"] == "success":
            print(f"Response: {result['response']}\n")
        else:
            print(f"Failed: {result['error']}\n")

    with open(OUTPUT_FILE, "w") as file:
        json.dump(results, file, indent=4)

    print(f"Saved results to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()