import json

from backend.memory.memory_store import save_memory
from backend.retrieval.baseline_retrieval import search_memories_baseline
from backend.retrieval.contextual_retrieval import search_memories_contextually
from backend.evaluation.metrics import evaluate_retrieval


SCENARIO_FILE = "evaluations/scenarios.json"
OUTPUT_FILE = "evaluations/baseline_vs_contextual_results.json"


def run_scenario(scenario):

    baseline_user_id = f"baseline_{scenario['id']}"
    contextual_user_id = f"contextual_{scenario['id']}"

    for memory in scenario["memories"]:
        save_memory(baseline_user_id, memory)
        save_memory(contextual_user_id, memory)

    baseline = search_memories_baseline(
        baseline_user_id,
        scenario["query"]
    )

    contextual = search_memories_contextually(
        contextual_user_id,
        scenario["query"]
    )

    return {
        "id": scenario["id"],
        "description": scenario["description"],
        "query": scenario["query"],
        "expected_memory": scenario["expected_memory"],
        "baseline": baseline,
        "contextual": contextual
    }


def main():

    with open(SCENARIO_FILE, "r") as file:
        scenarios = json.load(file)

    results = []

    for scenario in scenarios:

        print(f"\n{'=' * 60}")
        print(f"Running {scenario['id']}")
        print(f"{'=' * 60}")

        result = run_scenario(scenario)

        results.append(result)

        print("\nQuery:")
        print(result["query"])

        print("\nExpected:")
        print(result["expected_memory"])

        print("\nBASELINE RETRIEVAL:")

        if result["baseline"]:
            for memory in result["baseline"]:
                print(
                    f"- {memory.get('content')} "
                    f"[scope={memory.get('scope')}]"
                )
        else:
            print("- Nothing retrieved")

        print("\nCONTEXTUAL RETRIEVAL:")

        if result["contextual"]:
            for memory in result["contextual"]:
                print(
                    f"- {memory.get('content')} "
                    f"[scope={memory.get('scope')}]"
                )
        else:
            print("- Nothing retrieved")

    metrics = evaluate_retrieval(results)

    print(f"\n{'=' * 60}")
    print("EVALUATION SUMMARY")
    print(f"{'=' * 60}")

    print(f"Total scenarios: {metrics['total_scenarios']}")
    print(f"Baseline correct: {metrics['baseline_correct']}")
    print(f"Contextual correct: {metrics['contextual_correct']}")
    print(f"Baseline success rate: {metrics['baseline_success_rate']}%")
    print(f"Contextual success rate: {metrics['contextual_success_rate']}%")

    with open(OUTPUT_FILE, "w") as file:
        json.dump(
            {
                "results": results,
                "metrics": metrics
            },
            file,
            indent=4
        )

    print(f"\nSaved results to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
