
def detect_deadlock(allocation, request_matrix, available):
    if len(allocation) != len(request_matrix):
        raise ValueError("Allocation and request matrices must have equal rows.")

    if not allocation:
        raise ValueError("Enter at least one process.")

    resource_count = len(available)

    if any(len(row) != resource_count for row in allocation + request_matrix):
        raise ValueError("Matrix rows must match the available vector size.")

    if any(value < 0 for row in allocation + request_matrix for value in row):
        raise ValueError("Resource values cannot be negative.")

    if any(value < 0 for value in available):
        raise ValueError("Available resources cannot be negative.")

    work = available[:]
    finished = [
        all(value == 0 for value in row)
        for row in allocation
    ]
    sequence = []

    while True:
        progress = False

        for i in range(len(allocation)):
            if finished[i]:
                continue

            if all(request_matrix[i][j] <= work[j]
                   for j in range(resource_count)):
                work = [
                    work[j] + allocation[i][j]
                    for j in range(resource_count)
                ]
                finished[i] = True
                sequence.append(f"P{i}")
                progress = True

        if not progress:
            break

    deadlocked = [
        f"P{i}" for i, done in enumerate(finished) if not done
    ]

    return {
        "algorithm": "Deadlock Detection",
        "deadlock_detected": bool(deadlocked),
        "deadlocked_processes": deadlocked,
        "completed_sequence": sequence,
        "message": (
            "Deadlock detected in the entered state."
            if deadlocked
            else "No deadlock detected in the entered state."
        )
    }
