import sqlite3
from datetime import datetime

from flask import Flask, jsonify, request, render_template

import machineDAO
import demandDAO
import planner

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

def validate_demand(demand_data):
    required_fields = [
        "product_code",
        "product_name",
        "machine_type",
        "required_lots",
        "required_date"
    ]

    if not isinstance(demand_data, dict):
        return "Request body must contain valid JSON."

    for field in required_fields:
        if field not in demand_data:
            return f"Missing required field: {field}"

    if not isinstance(demand_data["product_code"], str):
        return "Product code must be text."

    if not demand_data["product_code"].strip():
        return "Product code cannot be empty."

    if not isinstance(demand_data["product_name"], str):
        return "Product name must be text."

    if not demand_data["product_name"].strip():
        return "Product name cannot be empty."

    valid_machine_types = ["LEON", "RAPH", "DONA", "MICH"]

    if demand_data["machine_type"] not in valid_machine_types:
        return "Machine type must be LEON, RAPH, DONA or MICH."

    required_lots = demand_data["required_lots"]

    if not isinstance(required_lots, int) or isinstance(required_lots, bool):
        return "Required lots must be a whole number."

    if required_lots <= 0:
        return "Required lots must be greater than zero."

    try:
        datetime.strptime(
            demand_data["required_date"],
            "%Y-%m-%d"
        )
    except (TypeError, ValueError):
        return "Required date must use YYYY-MM-DD format."

    if "active" in demand_data:
        if not isinstance(demand_data["active"], bool):
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

@app.route("/api/demand", methods=["GET"])
def get_all_demand():
    demand_records = demandDAO.get_all_demand()
    return jsonify(demand_records), 200

@app.route("/api/demand/<int:demand_id>", methods=["GET"])
def get_demand(demand_id):
    demand_record = demandDAO.get_demand_by_id(demand_id)

    if demand_record is None:
        return jsonify({
            "error": "Demand record not found"
        }), 404

    return jsonify(demand_record), 200

@app.route("/api/demand", methods=["POST"])
def create_demand():
    demand_data = request.get_json(silent=True)

    validation_error = validate_demand(demand_data)

    if validation_error:
        return jsonify({
            "error": "Validation failed",
            "message": validation_error
        }), 400

    if "active" not in demand_data:
        demand_data["active"] = True

    new_demand = demandDAO.create_demand(demand_data)

    return jsonify(new_demand), 201

@app.route("/api/demand/<int:demand_id>", methods=["PUT"])
def update_demand(demand_id):
    existing_demand = demandDAO.get_demand_by_id(demand_id)

    if existing_demand is None:
        return jsonify({
            "error": "Demand record not found"
        }), 404

    demand_data = request.get_json(silent=True)

    validation_error = validate_demand(demand_data)

    if validation_error:
        return jsonify({
            "error": "Validation failed",
            "message": validation_error
        }), 400

    if "active" not in demand_data:
        demand_data["active"] = True

    updated_demand = demandDAO.update_demand(
        demand_id,
        demand_data
    )

    return jsonify(updated_demand), 200

@app.route("/api/demand/<int:demand_id>", methods=["DELETE"])
def delete_demand(demand_id):
    existing_demand = demandDAO.get_demand_by_id(demand_id)

    if existing_demand is None:
        return jsonify({
            "error": "Demand record not found"
        }), 404

    demandDAO.delete_demand(demand_id)

    return "", 204

@app.route("/api/planning-summary", methods=["GET"])
def get_planning_summary():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)

    if year is None or month is None:
        return jsonify({
            "error": "Validation failed",
            "message": "Year and month are required."
        }), 400

    if month < 1 or month > 12:
        return jsonify({
            "error": "Validation failed",
            "message": "Month must be between 1 and 12."
        }), 400

    summary = planner.generate_capacity_summary(year, month)

    return jsonify({
        "year": year,
        "month": month,
        "summary": summary
    }), 200

if __name__ == "__main__":
    app.run(debug=True)