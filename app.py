import sqlite3
from datetime import datetime

from flask import (Flask, jsonify, request, render_template, make_response, Response)

import machineDAO
import demandDAO
import planner

import csv
import io

import xml.etree.ElementTree as ET

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

@app.route("/api/production-plan", methods=["GET"])
def get_production_plan():
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

    plan = planner.generate_daily_schedule(year, month)

    return jsonify({
        "year": year,
        "month": month,
        "schedule": plan["schedule"],
        "unallocated": plan["unallocated"]
    }), 200

@app.route("/api/production-plan/export.csv", methods=["GET"])
def export_production_plan_csv():
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

    plan = planner.generate_daily_schedule(year, month)

    csv_output = io.StringIO()

    field_names = [
        "production_date",
        "machine_code",
        "machine_type",
        "product_code",
        "product_name",
        "allocated_lots"
    ]

    writer = csv.DictWriter(
        csv_output,
        fieldnames=field_names
    )

    writer.writeheader()
    writer.writerows(plan["schedule"])

    response = make_response(csv_output.getvalue())

    response.headers["Content-Type"] = "text/csv"

    response.headers["Content-Disposition"] = (
        f"attachment; filename=production_plan_{year}_{month:02d}.csv"
    )

    return response

@app.route("/api/planning-summary.xml", methods=["GET"])
def get_planning_summary_xml():
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

    root = ET.Element("planningSummary")
    root.set("year", str(year))
    root.set("month", str(month))

    for item in summary:
        machine_element = ET.SubElement(
            root,
            "machineType"
        )

        machine_element.set(
            "code",
            item["machine_type"]
        )

        ET.SubElement(
            machine_element,
            "availableMachines"
        ).text = str(item["available_machines"])

        ET.SubElement(
            machine_element,
            "availableDays"
        ).text = str(item["available_days"])

        ET.SubElement(
            machine_element,
            "totalCapacity"
        ).text = str(item["total_capacity"])

        ET.SubElement(
            machine_element,
            "requiredLots"
        ).text = str(item["required_lots"])

        ET.SubElement(
            machine_element,
            "capacityBalance"
        ).text = str(item["capacity_balance"])

        ET.SubElement(
            machine_element,
            "result"
        ).text = item["result"]

    xml_content = ET.tostring(
        root,
        encoding="utf-8",
        xml_declaration=True
    )

    return Response(
        xml_content,
        status=200,
        mimetype="application/xml"
    )

@app.route("/api/demand/import.csv", methods=["POST"])
def import_demand_csv():
    if "file" not in request.files:
        return jsonify({
            "error": "No file provided",
            "message": "Please select a CSV file."
        }), 400

    uploaded_file = request.files["file"]

    if not uploaded_file.filename:
        return jsonify({
            "error": "No file selected",
            "message": "Please select a CSV file."
        }), 400

    if not uploaded_file.filename.lower().endswith(".csv"):
        return jsonify({
            "error": "Invalid file type",
            "message": "The uploaded file must be a CSV file."
        }), 400

    try:
        file_text = uploaded_file.stream.read().decode("utf-8-sig")
        csv_reader = csv.DictReader(io.StringIO(file_text))
    except UnicodeDecodeError:
        return jsonify({
            "error": "Invalid file encoding",
            "message": "The CSV file must use UTF-8 encoding."
        }), 400

    required_columns = {
        "product_code",
        "product_name",
        "machine_type",
        "required_lots",
        "required_date",
        "active"
    }

    actual_columns = set(csv_reader.fieldnames or [])

    if not required_columns.issubset(actual_columns):
        missing_columns = sorted(
            required_columns - actual_columns
        )

        return jsonify({
            "error": "Missing CSV columns",
            "message": (
                "Missing required columns: "
                + ", ".join(missing_columns)
            )
        }), 400

    validated_records = []
    validation_errors = []

    for row_number, row in enumerate(csv_reader, start=2):
        try:
            required_lots = int(row["required_lots"])
        except (TypeError, ValueError):
            validation_errors.append({
                "row": row_number,
                "message": "Required lots must be a whole number."
            })
            continue

        active_text = row["active"].strip().lower()

        if active_text not in ("true", "false"):
            validation_errors.append({
                "row": row_number,
                "message": "Active must be true or false."
            })
            continue

        demand_record = {
            "product_code": row["product_code"].strip(),
            "product_name": row["product_name"].strip(),
            "machine_type": row["machine_type"].strip().upper(),
            "required_lots": required_lots,
            "required_date": row["required_date"].strip(),
            "active": active_text == "true"
        }

        validation_error = validate_demand(demand_record)

        if validation_error:
            validation_errors.append({
                "row": row_number,
                "message": validation_error
            })
        else:
            validated_records.append(demand_record)

    if validation_errors:
        return jsonify({
            "error": "CSV validation failed",
            "message": "No records were imported.",
            "details": validation_errors
        }), 400

    if not validated_records:
        return jsonify({
            "error": "Empty CSV file",
            "message": "The CSV file contains no demand records."
        }), 400

    created_records = []

    for demand_record in validated_records:
        created_record = demandDAO.create_demand(
            demand_record
        )

        created_records.append(created_record)

    return jsonify({
        "message": "Demand imported successfully.",
        "records_imported": len(created_records),
        "records": created_records
    }), 201

@app.route("/api/demand/template.csv", methods=["GET"])
def download_demand_csv_template():
    csv_output = io.StringIO()

    writer = csv.writer(csv_output)

    writer.writerow([
        "product_code",
        "product_name",
        "machine_type",
        "required_lots",
        "required_date",
        "active"
    ])

    writer.writerow([
        "PROD-EXAMPLE",
        "Example Product",
        "LEON",
        "10",
        "2026-09-30",
        "true"
    ])

    response = make_response(csv_output.getvalue())

    response.headers["Content-Type"] = (
        "text/csv; charset=utf-8"
    )

    response.headers["Content-Disposition"] = (
        "attachment; filename=demand_import_template.csv"
    )

    return response

if __name__ == "__main__":
    app.run(debug=True)