
from flask import Blueprint, render_template, request
from routes.auth import role_required
from os_simulation.scheduler import fcfs, priority_scheduling, round_robin
from os_simulation.resource_allocation import bankers_algorithm
from os_simulation.deadlock import detect_deadlock

os_bp = Blueprint("os_simulation", __name__, url_prefix="/os")


@os_bp.route("/simulator", methods=["GET", "POST"])
@role_required("admin", "officer")
def simulator():
    result = None
    error = None
    algorithm = "fcfs"

    if request.method == "POST":
        algorithm = request.form.get("algorithm", "fcfs")

        try:
            if algorithm in {"fcfs", "priority", "round_robin"}:
                pids = request.form.getlist("pid")
                arrivals = request.form.getlist("arrival")
                bursts = request.form.getlist("burst")
                priorities = request.form.getlist("priority")

                processes = []
                for i, pid in enumerate(pids):
                    if not pid.strip():
                        continue
                    processes.append({
                        "pid": pid.strip(),
                        "arrival": int(arrivals[i]),
                        "burst": int(bursts[i]),
                        "priority": int(priorities[i]) if i < len(priorities) and priorities[i] else 0
                    })

                quantum = int(request.form.get("quantum", 2))

                if algorithm == "fcfs":
                    result = fcfs(processes)
                elif algorithm == "priority":
                    result = priority_scheduling(processes)
                else:
                    result = round_robin(processes, quantum)

            elif algorithm == "bankers":
                allocation = [[int(x) for x in row.split(",")]
                              for row in request.form.get("allocation", "").splitlines()
                              if row.strip()]
                maximum = [[int(x) for x in row.split(",")]
                           for row in request.form.get("maximum", "").splitlines()
                           if row.strip()]
                available = [int(x.strip()) for x in
                             request.form.get("available", "").split(",")
                             if x.strip()]
                result = bankers_algorithm(allocation, maximum, available)

            elif algorithm == "deadlock":
                allocation = [[int(x) for x in row.split(",")]
                              for row in request.form.get("allocation", "").splitlines()
                              if row.strip()]
                request_matrix = [[int(x) for x in row.split(",")]
                                  for row in request.form.get("request_matrix", "").splitlines()
                                  if row.strip()]
                available = [int(x.strip()) for x in
                             request.form.get("available", "").split(",")
                             if x.strip()]
                result = detect_deadlock(allocation, request_matrix, available)
            else:
                error = "Select a supported algorithm."

        except (ValueError, IndexError) as exc:
            error = f"Invalid input: {exc}"
        except Exception:
            error = "Simulation failed. Check the dimensions and values entered."

    return render_template(
        "os/simulator.html",
        result=result,
        error=error,
        algorithm=algorithm
    )
