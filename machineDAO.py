import sqlite3


DATABASE_NAME = "capacity_planner.db"


def get_all_machines():
    connection = sqlite3.connect(DATABASE_NAME)

    # Access database columns by name.
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            machine_code,
            machine_name,
            production_area,
            daily_capacity,
            active
        FROM machines
        ORDER BY machine_code
    """)

    rows = cursor.fetchall()
    connection.close()

    machines = []

    for row in rows:
        machine = {
            "id": row["id"],
            "machine_code": row["machine_code"],
            "machine_name": row["machine_name"],
            "production_area": row["production_area"],
            "daily_capacity": row["daily_capacity"],
            "active": bool(row["active"])
        }

        machines.append(machine)

    return machines

def get_machine_by_id(machine_id):
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            machine_code,
            machine_name,
            production_area,
            daily_capacity,
            active
        FROM machines
        WHERE id = ?
    """, (machine_id,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    machine = {
        "id": row["id"],
        "machine_code": row["machine_code"],
        "machine_name": row["machine_name"],
        "production_area": row["production_area"],
        "daily_capacity": row["daily_capacity"],
        "active": bool(row["active"])
    }

    return machine

    for machine in machines:
        print(machine)

def create_machine(machine):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO machines (
            machine_code,
            machine_name,
            production_area,
            daily_capacity,
            active
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        machine["machine_code"],
        machine["machine_name"],
        machine["production_area"],
        machine["daily_capacity"],
        int(machine["active"])
    ))

    connection.commit()

    new_machine_id = cursor.lastrowid
    connection.close()

    return get_machine_by_id(new_machine_id)

def update_machine(machine_id, machine):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE machines
        SET machine_code = ?,
            machine_name = ?,
            production_area = ?,
            daily_capacity = ?,
            active = ?
        WHERE id = ?
    """, (
        machine["machine_code"],
        machine["machine_name"],
        machine["production_area"],
        machine["daily_capacity"],
        int(machine["active"]),
        machine_id
    ))

    connection.commit()
    rows_updated = cursor.rowcount
    connection.close()

    if rows_updated == 0:
        return None

    return get_machine_by_id(machine_id)

def delete_machine(machine_id):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM machines
        WHERE id = ?
    """, (machine_id,))

    connection.commit()
    rows_deleted = cursor.rowcount
    connection.close()

    return rows_deleted > 0

if __name__ == "__main__":
    machines = get_all_machines()

    for machine in machines:
        print(machine)

