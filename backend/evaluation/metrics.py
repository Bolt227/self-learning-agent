def evaluate_retrieval(results):
    total = len(results)

    baseline_correct = 0
    contextual_correct = 0

    for result in results:

        expected = result.get("expected_memory")

        baseline = result.get("baseline", [])
        contextual = result.get("contextual", [])

        baseline_contents = {
            memory.get("content")
            for memory in baseline
        }

        contextual_contents = {
            memory.get("content")
            for memory in contextual
        }

        if expected is None:
            if not baseline:
                baseline_correct += 1

            if not contextual:
                contextual_correct += 1

        else:
            if expected in baseline_contents:
                baseline_correct += 1

            if expected in contextual_contents:
                contextual_correct += 1

    baseline_rate = (
        baseline_correct / total * 100
        if total > 0
        else 0
    )

    contextual_rate = (
        contextual_correct / total * 100
        if total > 0
        else 0
    )

    return {
        "total_scenarios": total,
        "baseline_correct": baseline_correct,
        "contextual_correct": contextual_correct,
        "baseline_success_rate": round(baseline_rate, 2),
        "contextual_success_rate": round(contextual_rate, 2)
    }