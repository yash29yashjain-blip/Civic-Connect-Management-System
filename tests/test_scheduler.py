
from os_simulation.scheduler import fcfs, priority_scheduling, round_robin


def sample_processes():
    return [
        {"pid": "P1", "arrival": 0, "burst": 5, "priority": 2},
        {"pid": "P2", "arrival": 1, "burst": 3, "priority": 1},
        {"pid": "P3", "arrival": 2, "burst": 2, "priority": 3},
    ]


def test_fcfs_execution_order():
    result = fcfs(sample_processes())
    assert result["execution_order"] == ["P1", "P2", "P3"]


def test_fcfs_waiting_and_turnaround():
    result = fcfs(sample_processes())
    rows = {p["pid"]: p for p in result["processes"]}
    assert rows["P1"]["waiting"] == 0
    assert rows["P2"]["waiting"] == 4
    assert rows["P3"]["turnaround"] == 8


def test_priority_scheduling():
    result = priority_scheduling(sample_processes())
    assert result["execution_order"][0] == "P1"
    assert result["average_waiting"] >= 0


def test_round_robin_completes_all_processes():
    result = round_robin(sample_processes(), quantum=2)
    assert len(result["processes"]) == 3
    assert all(p["completion"] > 0 for p in result["processes"])


def test_round_robin_rejects_invalid_quantum():
    try:
        round_robin(sample_processes(), quantum=0)
    except ValueError:
        return
    assert False, "Expected ValueError for zero quantum"
