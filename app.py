from flask import Flask, jsonify, request, render_template

import machineDAO
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

def validate_machine(machine_data):
    required_fields = [
        "machine_code",
        "machine_name",
        "production_area",
        "daily_capacity"
    ]

    if not isinstance(machine_data, dict):
        return "Request body must contain valid JSON."

    for field in required_fields:
        if field not in machine_data:
            return f"Missing required field: {field}"

    if not isinstance(machine_data["machine_code"], str):
        return "Machine code must be text."

    if not machine_data["machine_code"].strip():
        return "Machine code cannot be empty."

    if not isinstance(machine_data["machine_name"], str):
        return "Machine name must be text."

    if not machine_data["machine_name"].strip():
        return "Machine name cannot be empty."

    if not isinstance(machine_data["production_area"], str):
        return "Production area must be text."

    if not machine_data["production_area"].strip():
        return "Production area cannot be empty."

    capacity = machine_data["daily_capacity"]

    if not isinstance(capacity, int) or isinstance(capacity, bool):
        return "Daily capacity must be a whole number."

    if capacity <= 0:
        return "Daily capacity must be greater than zero."

    if "active" in machine_data:
        if not isinstance(machine_data["active"], bool):
            return "Active must be true or false."

    return None


@app.route("/api/machines", methods=["GET"])
def get_machines():
    machines = machineDAO.get_all_machines()
    return jsonify(machines)

@app.route("/api/machines/<int:machine_id>", methods=["GET"])
def get_machine(machine_id):
    machine = machineDAO.get_machine_by_id(machine_id)

    if machine is None:
        return jsonify({
            "error": "Machine not found"
        }), 404

    return jsonify(machine), 200

@app.route("/api/machines", methods=["POST"])
def create_machine():
    machine_data = request.get_json(silent=True)

    validation_error = validate_machine(machine_data)

    if validation_error:
        return jsonify({
            "error": "Validation failed",
            "message": validation_error
        }), 400

    if "active" not in machine_data:
        machine_data["active"] = True

    try:
        new_machine = machineDAO.create_machine(machine_data)
    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Duplicate machine code",
            "message": "A machine with this machine code already exists."
        }), 409

    return jsonify(new_machine), 201

@app.route("/api/machines/<int:machine_id>", methods=["PUT"])
def update_machine(machine_id):
    existing_machine = machineDAO.get_machine_by_id(machine_id)

    if existing_machine is None:
        return jsonify({
            "error": "Machine not found"
        }), 404

    machine_data = request.get_json(silent=True)

    validation_error = validate_machine(machine_data)

    if validation_error:
        return jsonify({
            "error": "Validation failed",
            "message": validation_error
        }), 400

    if "active" not in machine_data:
        machine_data["active"] = True

    try:
        updated_machine = machineDAO.update_machine(
            machine_id,
            machine_data
        )
    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Duplicate machine code",
            "message": "A machine with this machine code already exists."
        }), 409

    return jsonify(updated_machine), 200

@app.route("/api/machines/<int:machine_id>", methods=["DELETE"])
def delete_machine(machine_id):
    existing_machine = machineDAO.get_machine_by_id(machine_id)

    if existing_machine is None:
        return jsonify({
            "error": "Machine not found"
        }), 404

    machineDAO.delete_machine(machine_id)

    return "", 204

if __name__ == "__main__":
    app.run(debug=True)