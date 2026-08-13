async function generatePlan(event) {
    event.preventDefault();

    const planningMonth = document.getElementById(
        "planning-month"
    ).value;

    const message = document.getElementById(
        "planning-message"
    );

    const resultsSection = document.getElementById(
        "planning-results"
    );

    const tableBody = document.getElementById(
        "planning-table-body"
    );

    if (!planningMonth) {
        message.textContent = "Please select a planning month.";
        return;
    }

    const [year, month] = planningMonth.split("-");

    message.textContent = "Generating production plan...";

    try {
        const response = await fetch(
            `/api/planning-summary?year=${year}&month=${month}`
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || result.error);
        }

        tableBody.innerHTML = "";

        for (const item of result.summary) {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${item.machine_type}</td>
                <td>${item.available_machines}</td>
                <td>${item.available_days}</td>
                <td>${item.total_capacity}</td>
                <td>${item.required_lots}</td>
                <td>${item.capacity_balance}</td>
                <td>${item.result}</td>
            `;

            tableBody.appendChild(row);
        }

        resultsSection.hidden = false;
        message.textContent = "Production plan generated successfully.";
    } catch (error) {
        resultsSection.hidden = true;
        message.textContent = error.message;
    }
}


document.addEventListener("DOMContentLoaded", function () {
    const planningForm = document.getElementById(
        "planning-form"
    );

    planningForm.addEventListener("submit", generatePlan);
});