
document.addEventListener("DOMContentLoaded", () => {
    const algorithm = document.getElementById("algorithm");
    const processFields = document.getElementById("process-fields");
    const resourceFields = document.getElementById("resource-fields");

    if (!algorithm || !processFields || !resourceFields) return;

    function updateVisibleFields() {
        const cpuAlgorithm = ["fcfs", "priority", "round_robin"].includes(algorithm.value);
        processFields.hidden = !cpuAlgorithm;
        resourceFields.hidden = cpuAlgorithm;

        processFields.querySelectorAll("input").forEach((input) => {
            input.disabled = !cpuAlgorithm;
        });
        resourceFields.querySelectorAll("input, textarea").forEach((input) => {
            input.disabled = cpuAlgorithm;
        });
    }

    algorithm.addEventListener("change", updateVisibleFields);
    updateVisibleFields();
});
