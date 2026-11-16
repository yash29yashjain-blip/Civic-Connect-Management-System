
def _validate(processes):
    if not processes:
        raise ValueError("Add at least one process.")

    for process in processes:
        if int(process["arrival"]) < 0:
            raise ValueError("Arrival time cannot be negative.")
        if int(process["burst"]) <= 0:
            raise ValueError("Burst time must be greater than zero.")


def _metrics(processes, completion):
    rows = []
    total_waiting = 0
    total_turnaround = 0

    for p in processes:
        pid = p["pid"]
        turnaround = completion[pid] - int(p["arrival"])
        waiting = turnaround - int(p["burst"])
        total_waiting += waiting
        total_turnaround += turnaround

        rows.append({
            "pid": pid,
            "arrival": int(p["arrival"]),
            "burst": int(p["burst"]),
            "completion": completion[pid],
            "turnaround": turnaround,
            "waiting": waiting
        })

    count = len(rows)
    return {
        "processes": rows,
        "average_waiting": round(total_waiting / count, 2),
        "average_turnaround": round(total_turnaround / count, 2)
    }


def fcfs(processes):
    _validate(processes)
    ordered = sorted(processes, key=lambda p: (int(p["arrival"]), str(p["pid"])))
    time = 0
    completion = {}

    for p in ordered:
        time = max(time, int(p["arrival"]))
        time += int(p["burst"])
        completion[p["pid"]] = time

    result = _metrics(processes, completion)
    result["algorithm"] = "First Come First Served (FCFS)"
    result["execution_order"] = [p["pid"] for p in ordered]
    return result


def priority_scheduling(processes):
    _validate(processes)
    pending = [dict(p) for p in processes]
    time = 0
    completion = {}
    execution_order = []

    while pending:
        ready = [p for p in pending if int(p["arrival"]) <= time]

        if not ready:
            time = min(int(p["arrival"]) for p in pending)
            ready = [p for p in pending if int(p["arrival"]) <= time]

        # Lower priority number means higher priority.
        chosen = min(
            ready,
            key=lambda p: (int(p.get("priority", 0)), int(p["arrival"]), str(p["pid"]))
        )
        time += int(chosen["burst"])
        completion[chosen["pid"]] = time
        execution_order.append(chosen["pid"])
        pending.remove(chosen)

    result = _metrics(processes, completion)
    result["algorithm"] = "Non-preemptive Priority Scheduling"
    result["execution_order"] = execution_order
    return result


def round_robin(processes, quantum=2):
    _validate(processes)

    if int(quantum) <= 0:
        raise ValueError("Time quantum must be greater than zero.")

    quantum = int(quantum)
    ordered = sorted(processes, key=lambda p: (int(p["arrival"]), str(p["pid"])))
    remaining = {p["pid"]: int(p["burst"]) for p in ordered}
    completion = {}
    first_start = {}
    queue = []
    time = 0
    index = 0
    execution_order = []

    while index < len(ordered) or queue:
        if not queue and index < len(ordered):
            time = max(time, int(ordered[index]["arrival"]))
            while index < len(ordered) and int(ordered[index]["arrival"]) <= time:
                queue.append(ordered[index])
                index += 1

        if not queue:
            continue

        p = queue.pop(0)
        pid = p["pid"]
        first_start.setdefault(pid, time)

        run_time = min(quantum, remaining[pid])
        time += run_time
        remaining[pid] -= run_time
        execution_order.append(pid)

        while index < len(ordered) and int(ordered[index]["arrival"]) <= time:
            queue.append(ordered[index])
            index += 1

        if remaining[pid] > 0:
            queue.append(p)
        else:
            completion[pid] = time

    result = _metrics(processes, completion)
    for row in result["processes"]:
        row["first_start"] = first_start[row["pid"]]

    result["algorithm"] = f"Round Robin (quantum={quantum})"
    result["execution_order"] = execution_order
    return result
