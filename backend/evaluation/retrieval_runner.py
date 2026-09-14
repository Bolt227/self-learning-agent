import json

from backend.memory.memory_store import save_memory

from backend.retrieval.contextual_retrieval import search_memories_contextually

SCENARIO_FILE = "evaluations/scenarios.json"

OUTPUT_FILE = "evaluations/retrieval_results.json"

def run_scenario(scenario):

    user_id = f"retrieval_{scenario['id']}"

    for memory in scenario["memories"]:

        save_memory(user_id, memory)

    retrieved = search_memories_contextually(

        user_id,

        scenario["query"]

    )

    return {

        "id": scenario["id"],

        "description": scenario["description"],

        "query": scenario["query"],

        "expected": scenario["expected"],

        "retrieved_memories": retrieved

    }

def main():

    with open(SCENARIO_FILE, "r") as file:

        scenarios = json.load(file)

    results = []

    for scenario in scenarios:

        print(f"\nRunning {scenario['id']}...")

        result = run_scenario(scenario)

        results.append(result)

        print("Expected:", result["expected"])

        print("Retrieved:")

        for memory in result["retrieved_memories"]:

            print(

                f"- {memory.get('content')} "

                f"[scope={memory.get('scope')}]"

            )

    with open(OUTPUT_FILE, "w") as file:

        json.dump(results, file, indent=4)

    print(f"\nSaved results to {OUTPUT_FILE}")

if __name__ == "__main__":

    main()