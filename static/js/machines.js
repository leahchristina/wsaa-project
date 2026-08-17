async function loadMachines() {
    const tableBody = document.getElementById("machine-table-body");

    try {
        const response = await fetch("/api/machines");

        if (!response.ok) {
            throw new Error("Could not retrieve the machines.");
        }

        const machines = await response.json();

        tableBody.innerHTML = "";

        for (const machine of machines) {
            const row = document.createElement("tr");

row.innerHTML = `
    <td>${machine.machine_code}</td>
    <td>${machine.machine_name}</td>
    <td>${machine.production_area}</td>
    <td>${machine.daily_capacity}</td>
    <td>${machine.active ? "Active" : "Inactive"}</td>
    <td>
        <button
            type="button"
            onclick="prepareMachineUpdate(${machine.id})"
        >
            Update
        </button>

${
    machine.active
        ? `
            <button
                type="button"
                onclick="decommissionMachine(${machine.id})"
            >
                Decommission
            </button>
        `
        : `
            <button
            type="button"
            class="recommission-button"
            onclick="recommissionMachine(${machine.id})"
>
    Recommission
</button>
        `
}
<button
    type="button"
    class="delete-button"
    onclick="deleteMachine(${machine.id})"
>
    Delete
</button>
    </td>
`;

            tableBody.appendChild(row);
        }
    } catch (error) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6">${error.message}</td>
            </tr>
        `;
    }
}

async function saveMachine(event) {
    event.preventDefault();

    const message = document.getElementById("form-message");

    const machine = {
        machine_code: document
            .getElementById("machine-code")
            .value
            .trim(),

        machine_name: document
            .getElementById("machine-name")
            .value
            .trim(),

        production_area: document
            .getElementById("production-area")
            .value
            .trim(),

        daily_capacity: Number(
            document.getElementById("daily-capacity").value
        ),

        active: document.getElementById("active").checked
    };

    try {
        const machineId = document.getElementById("machine-id").value;

const url = machineId
    ? `/api/machines/${machineId}`
    : "/api/machines";

const method = machineId ? "PUT" : "POST";

const response = await fetch(url, {
    method: method,
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify(machine)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || result.error);
        }

const wasUpdate = Boolean(machineId);

resetMachineForm();

message.textContent = wasUpdate
    ? "Machine updated successfully."
    : "Machine added successfully.";

await loadMachines();

        document.getElementById("machine-form").reset();
        document.getElementById("active").checked = true;

        await loadMachines();
    } catch (error) {
        message.textContent = error.message;
    }
}

async function prepareMachineUpdate(machineId) {
    const message = document.getElementById("form-message");

    try {
        const response = await fetch(
            `/api/machines/${machineId}`
        );

        if (!response.ok) {
            throw new Error("Could not retrieve the machine.");
        }

        const machine = await response.json();

        document.getElementById("machine-id").value =
            machine.id;

        document.getElementById("machine-code").value =
            machine.machine_code;

        document.getElementById("machine-name").value =
            machine.machine_name;

        document.getElementById("production-area").value =
            machine.production_area;

        document.getElementById("daily-capacity").value =
            machine.daily_capacity;

        document.getElementById("active").checked =
            machine.active;

        document.getElementById("submit-button").textContent =
            "Update Machine";

        document.getElementById(
            "cancel-update-button"
        ).hidden = false;

        message.textContent = "Update the machine details below.";

        document.getElementById("machine-form").scrollIntoView({
            behavior: "smooth"
        });
    } catch (error) {
        message.textContent = error.message;
    }
}

async function decommissionMachine(machineId) {
    const confirmed = window.confirm(
        "Are you sure you want to decommission this machine?"
    );

    if (!confirmed) {
        return;
    }

    try {
        const getResponse = await fetch(
            `/api/machines/${machineId}`
        );

        if (!getResponse.ok) {
            throw new Error("Could not retrieve the machine.");
        }

        const machine = await getResponse.json();

        machine.active = false;

        const updateResponse = await fetch(
            `/api/machines/${machineId}`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(machine)
            }
        );

        const result = await updateResponse.json();

        if (!updateResponse.ok) {
            throw new Error(result.message || result.error);
        }

        await loadMachines();
    } catch (error) {
        window.alert(error.message);
    }
}

async function recommissionMachine(machineId) {
    const confirmed = window.confirm(
        "Are you sure you want to recommission this machine?"
    );

    if (!confirmed) {
        return;
    }

    try {
        const getResponse = await fetch(
            `/api/machines/${machineId}`
        );

        if (!getResponse.ok) {
            throw new Error("Could not retrieve the machine.");
        }

        const machine = await getResponse.json();

        machine.active = true;

        const updateResponse = await fetch(
            `/api/machines/${machineId}`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(machine)
            }
        );

        const result = await updateResponse.json();

        if (!updateResponse.ok) {
            throw new Error(result.message || result.error);
        }

        await loadMachines();
    } catch (error) {
        window.alert(error.message);
    }
}

async function getMachineRecord(machineId) {
    const response = await fetch(
        `/api/machines/${machineId}`
    );

    if (!response.ok) {
        throw new Error("Could not retrieve the machine.");
    }

    return await response.json();
}

async function deleteMachine(machineId) {
    const machine = await getMachineRecord(machineId);

    const confirmed = window.confirm(
        `Permanently delete ${machine.machine_code} - ` +
        `${machine.machine_name}?\n\n` +
        "This action cannot be undone. " +
        "Use Decommission instead if the machine should be " +
        "retained for historical purposes."
    );

    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(
            `/api/machines/${machineId}`,
            {
                method: "DELETE"
            }
        );

        if (!response.ok) {
            let errorMessage = "Could not delete the machine.";

            try {
                const result = await response.json();
                errorMessage = result.message || result.error;
            } catch {
                // A 204 response has no JSON body.
            }

            throw new Error(errorMessage);
        }

        resetMachineForm();

        document.getElementById(
            "form-message"
        ).textContent = "Machine deleted successfully.";

        await loadMachines();
    } catch (error) {
        window.alert(error.message);
    }
}

function resetMachineForm() {
    const form = document.getElementById("machine-form");

    form.reset();

    document.getElementById("machine-id").value = "";
    document.getElementById("active").checked = true;

    document.getElementById("submit-button").textContent =
        "Add Machine";

    document.getElementById(
        "cancel-update-button"
    ).hidden = true;

    document.getElementById("form-message").textContent = "";
}

document.addEventListener("DOMContentLoaded", function () {
    loadMachines();

    const machineForm =
        document.getElementById("machine-form");

    const cancelButton =
        document.getElementById("cancel-update-button");

    machineForm.addEventListener("submit", saveMachine);

    cancelButton.addEventListener("click", resetMachineForm);
});