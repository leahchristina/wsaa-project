let generatedPlanningMonth = "";

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
                <td class="${
    item.result === "Capacity available"
        ? "result-available"
        : "result-shortfall"
}">
    ${item.result}
</td>
            `;

            tableBody.appendChild(row);
        }

        const planResponse = await fetch(
    `/api/production-plan?year=${year}&month=${month}`
);

const plan = await planResponse.json();

if (!planResponse.ok) {
    throw new Error(plan.message || plan.error);
}

const scheduleTableBody = document.getElementById(
    "schedule-table-body"
);

scheduleTableBody.innerHTML = "";

for (const allocation of plan.schedule) {
    const row = document.createElement("tr");

    row.innerHTML = `
        <td>${allocation.production_date}</td>
        <td>${allocation.machine_code}</td>
        <td>${allocation.machine_type}</td>
        <td>${allocation.product_code}</td>
        <td>${allocation.product_name}</td>
        <td>${allocation.allocated_lots}</td>
    `;

    scheduleTableBody.appendChild(row);
}

if (plan.schedule.length === 0) {
    scheduleTableBody.innerHTML = `
        <tr>
            <td colspan="6">
                No active demand was scheduled for this month.
            </td>
        </tr>
    `;
}

const unallocatedResults = document.getElementById(
    "unallocated-results"
);

const unallocatedTableBody = document.getElementById(
    "unallocated-table-body"
);

unallocatedTableBody.innerHTML = "";

if (plan.unallocated.length > 0) {
    for (const item of plan.unallocated) {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${item.product_code}</td>
            <td>${item.product_name}</td>
            <td>${item.machine_type}</td>
            <td>${item.required_lots}</td>
            <td>${item.unallocated_lots}</td>
            <td>${item.reason}</td>
        `;

        unallocatedTableBody.appendChild(row);
    }

    unallocatedResults.hidden = false;
} else {
    unallocatedResults.hidden = true;
}

const totalAllocated = plan.schedule.reduce(
    (total, allocation) =>
        total + allocation.allocated_lots,
    0
);

const totalUnallocated = plan.unallocated.reduce(
    (total, item) =>
        total + item.unallocated_lots,
    0
);

const totalRequired =
    totalAllocated + totalUnallocated;

let completionDate = "Not Available";

if (plan.schedule.length > 0) {
    completionDate = plan.schedule.reduce(
        (latestDate, allocation) =>
            allocation.production_date > latestDate
                ? allocation.production_date
                : latestDate,
        plan.schedule[0].production_date
    );
}

document.getElementById(
    "total-required-lots"
).textContent = totalRequired;

document.getElementById(
    "total-allocated-lots"
).textContent = totalAllocated;

const unallocatedLotsElement = document.getElementById(
    "total-unallocated-lots"
);

unallocatedLotsElement.textContent = totalUnallocated;

if (totalUnallocated > 0) {
    unallocatedLotsElement.className = "value-shortfall";
} else {
    unallocatedLotsElement.className = "value-feasible";
}

document.getElementById(
    "completion-date"
).textContent = completionDate;

const planStatus = document.getElementById("plan-status");

if (totalUnallocated === 0) {
    planStatus.textContent = "Feasible";
    planStatus.className = "status-feasible";
} else {
    planStatus.textContent = "Capacity Shortfall";
    planStatus.className = "status-shortfall";
}

        resultsSection.hidden = false;
        generatedPlanningMonth = planningMonth;

document.getElementById(
    "export-csv-button"
).disabled = false;
        message.textContent = "Production plan generated successfully.";
    } catch (error) {
        resultsSection.hidden = true;
        message.textContent = error.message;
    }
}

function exportScheduleToCsv() {
    if (!generatedPlanningMonth) {
        return;
    }

    const [year, month] =
        generatedPlanningMonth.split("-");

    const exportUrl =
        `/api/production-plan/export.csv` +
        `?year=${year}&month=${month}`;

    window.location.href = exportUrl;
}

document.addEventListener("DOMContentLoaded", function () {
    const planningForm = document.getElementById(
        "planning-form"
    );

    planningForm.addEventListener("submit", generatePlan);
});

const exportButton = document.getElementById(
    "export-csv-button"
);

exportButton.addEventListener(
    "click",
    exportScheduleToCsv
);