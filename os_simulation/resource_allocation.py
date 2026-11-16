
def bankers_algorithm(allocation, maximum, available):
    if len(allocation) != len(maximum):
        raise ValueError("Allocation and maximum matrices must have equal rows.")

    if not allocation:
        raise ValueError("Enter at least one process.")

    resource_count = len(available)

    if any(len(row) != resource_count for row in allocation + maximum):
        raise ValueError("Every matrix row must match the available vector size.")

    if any(value < 0 for row in allocation + maximum for value in row):
        raise ValueError("Resource values cannot be negative.")

    if any(value < 0 for value in available):
        raise ValueError("Available resources cannot be negative.")

    for alloc_row, max_row in zip(allocation, maximum):
        if any(a > m for a, m in zip(alloc_row, max_row)):
            raise ValueError("Allocation cannot exceed maximum demand.")

    need = [
        [maximum[i][j] - allocation[i][j]
         for j in range(resource_count)]
        for i in range(len(allocation))
    ]

    work = available[:]
    finished = [False] * len(allocation)
    safe_sequence = []

    while len(safe_sequence) < len(allocation):
        progress = False

        for i in range(len(allocation)):
            if finished[i]:
                continue

            if all(need[i][j] <= work[j] for j in range(resource_count)):
                work = [
                    work[j] + allocation[i][j]
                    for j in range(resource_count)
                ]
                finished[i] = True
                safe_sequence.append(f"P{i}")
                progress = True

        if not progress:
            break

    return {
        "algorithm": "Banker's Algorithm",
        "safe": all(finished),
        "safe_sequence": safe_sequence,
        "need_matrix": need,
        "message": (
            "System is in a safe state."
            if all(finished)
            else "System is not in a safe state."
        )
    }
