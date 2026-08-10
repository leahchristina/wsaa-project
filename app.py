from flask import Flask, jsonify, request

import machineDAO


app = Flask(__name__)


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
    machine_data = request.get_json()

    new_machine = machineDAO.create_machine(machine_data)

    return jsonify(new_machine), 201


if __name__ == "__main__":
    app.run(debug=True)