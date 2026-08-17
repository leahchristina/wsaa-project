async function loadDemand() {
    const tableBody = document.getElementById("demand-table-body");

    try {
        const response = await fetch("/api/demand");

        if (!response.ok) {
            throw new Error("Could not retrieve demand records.");
        }

        const demandRecords = await response.json();

        tableBody.innerHTML = "";

        for (const demand of demandRecords) {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${demand.product_code}</td>
                <td>${demand.product_name}</td>
                <td>${demand.machine_type}</td>
                <td>${demand.required_lots}</td>
                <td>${demand.required_date}</td>
                <td>${demand.active ? "Active" : "Inactive"}</td>
                <td>
<td>
    <button
        type="button"
        onclick="prepareDemandUpdate(${demand.id})"
    >
        Update
    </button>

    ${
        demand.active
            ? `
                <button
                    type="button"
                    onclick="deactivateDemand(${demand.id})"
                >
                    Deactivate
                </button>
            `
            : `
                <button
                    type="button"
                    class="reactivate-button"
                    onclick="reactivateDemand(${demand.id})"
                >
                    Reactivate
                </button>
            `
    }

    <button
        type="button"
        class="delete-button"
        onclick="deleteDemand(${demand.id})"
    >
        Delete
    </button>
</td>

                </td>
            `;

            tableBody.appendChild(row);
        }

        if (demandRecords.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7">
                        No demand records have been added.
                    </td>
                </tr>
            `;
        }
    } catch (error) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7">${error.message}</td>
            </tr>
        `;
    }
}


async function saveDemand(event) {
    event.preventDefault();

    const message = document.getElementById(
        "demand-form-message"
    );

    const demandId = document.getElementById("demand-id").value;

    const demand = {
        product_code: document
            .getElementById("product-code")
            .value
            .trim(),

        product_name: document
            .getElementById("product-name")
            .value
            .trim(),

        machine_type: document
            .getElementById("machine-type")
            .value,

        required_lots: Number(
            document.getElementById("required-lots").value
        ),

        required_date: document
            .getElementById("required-date")
            .value,

        active: document
            .getElementById("demand-active")
            .checked
    };

    const url = demandId
        ? `/api/demand/${demandId}`
        : "/api/demand";

    const method = demandId ? "PUT" : "POST";
    const wasUpdate = Boolean(demandId);

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(demand)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(
                result.message || result.error
            );
        }

        resetDemandForm();

        message.textContent = wasUpdate
            ? "Demand updated successfully."
            : "Demand added successfully.";

        await loadDemand();
    } catch (error) {
        message.textContent = error.message;
    }
}


async function prepareDemandUpdate(demandId) {
    const message = document.getElementById(
        "demand-form-message"
    );

    try {
        const response = await fetch(
            `/api/demand/${demandId}`
        );

        if (!response.ok) {
            throw new Error(
                "Could not retrieve the demand record."
            );
        }

        const demand = await response.json();

        document.getElementById("demand-id").value =
            demand.id;

        document.getElementById("product-code").value =
            demand.product_code;

        document.getElementById("product-name").value =
            demand.product_name;

        document.getElementById("machine-type").value =
            demand.machine_type;

        document.getElementById("required-lots").value =
            demand.required_lots;

        document.getElementById("required-date").value =
            demand.required_date;

        document.getElementById("demand-active").checked =
            demand.active;

        document.getElementById(
            "demand-submit-button"
        ).textContent = "Update Demand";

        document.getElementById(
            "cancel-demand-update-button"
        ).hidden = false;

        message.textContent =
            "Update the demand details below.";

        document.getElementById("demand-form").scrollIntoView({
            behavior: "smooth"
        });
    } catch (error) {
        message.textContent = error.message;
    }
}


async function deactivateDemand(demandId) {
    const confirmed = window.confirm(
        "Are you sure you want to deactivate this demand record?"
    );

    if (!confirmed) {
        return;
    }

    try {
        const demand = await getDemandRecord(demandId);

        demand.active = false;

        await updateDemandStatus(demandId, demand);
        await loadDemand();
    } catch (error) {
        window.alert(error.message);
    }
}


async function reactivateDemand(demandId) {
    const confirmed = window.confirm(
        "Are you sure you want to reactivate this demand record?"
    );

    if (!confirmed) {
        return;
    }

    try {
        const demand = await getDemandRecord(demandId);

        demand.active = true;

        await updateDemandStatus(demandId, demand);
        await loadDemand();
    } catch (error) {
        window.alert(error.message);
    }
}


async function getDemandRecord(demandId) {
    const response = await fetch(
        `/api/demand/${demandId}`
    );

    if (!response.ok) {
        throw new Error(
            "Could not retrieve the demand record."
        );
    }

    return await response.json();
}


async function updateDemandStatus(demandId, demand) {
    const response = await fetch(
        `/api/demand/${demandId}`,
        {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(demand)
        }
    );

    const result = await response.json();

    if (!response.ok) {
        throw new Error(
            result.message || result.error
        );
    }

    return result;
}

async function deleteDemand(demandId) {
    try {
        const demand = await getDemandRecord(demandId);

        const confirmed = window.confirm(
            `Permanently delete ${demand.product_code} - ` +
            `${demand.product_name}?\n\n` +
            "This action cannot be undone. " +
            "Use Deactivate instead if the demand should be " +
            "retained for historical purposes."
        );

        if (!confirmed) {
            return;
        }

        const response = await fetch(
            `/api/demand/${demandId}`,
            {
                method: "DELETE"
            }
        );

        if (!response.ok) {
            let errorMessage =
                "Could not delete the demand record.";

            try {
                const result = await response.json();

                errorMessage =
                    result.message || result.error;
            } catch {
                // A successful 204 response has no JSON body.
            }

            throw new Error(errorMessage);
        }

        resetDemandForm();

        document.getElementById(
            "demand-form-message"
        ).textContent =
            "Demand record deleted successfully.";

        await loadDemand();
    } catch (error) {
        window.alert(error.message);
    }
}


function resetDemandForm() {
    const form = document.getElementById("demand-form");

    form.reset();

    document.getElementById("demand-id").value = "";
    document.getElementById("demand-active").checked = true;

    document.getElementById(
        "demand-submit-button"
    ).textContent = "Add Demand";

    document.getElementById(
        "cancel-demand-update-button"
    ).hidden = true;

    document.getElementById(
        "demand-form-message"
    ).textContent = "";
}

async function importDemandCsv() {
    const fileInput = document.getElementById(
        "demand-csv-file"
    );

    const message = document.getElementById(
        "csv-import-message"
    );

    if (fileInput.files.length === 0) {
        message.textContent = "Please select a CSV file.";
        return;
    }

    const selectedFile = fileInput.files[0];
    const formData = new FormData();

    formData.append("file", selectedFile);

    message.textContent = "Importing demand records...";

    try {
        const response = await fetch(
            "/api/demand/import.csv",
            {
                method: "POST",
                body: formData
            }
        );

        const result = await response.json();

        if (!response.ok) {
            let errorMessage =
                result.message || result.error;

            if (result.details) {
                const rowErrors = result.details.map(
                    detail =>
                        `Row ${detail.row}: ${detail.message}`
                );

                errorMessage += " " + rowErrors.join(" ");
            }

            throw new Error(errorMessage);
        }

        message.textContent =
            `${result.records_imported} demand records ` +
            `imported successfully.`;

        fileInput.value = "";

        await loadDemand();
    } catch (error) {
        message.textContent = error.message;
    }
}


document.addEventListener("DOMContentLoaded", function () {
    loadDemand();

    const demandForm =
        document.getElementById("demand-form");

    const cancelButton =
        document.getElementById(
            "cancel-demand-update-button"
        );

    demandForm.addEventListener("submit", saveDemand);

    cancelButton.addEventListener(
        "click",
        resetDemandForm
    );

    const importButton = document.getElementById(
    "import-csv-button"
);

importButton.addEventListener(
    "click",
    importDemandCsv
);
});