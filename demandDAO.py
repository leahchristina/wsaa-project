import sqlite3


DATABASE_NAME = "capacity_planner.db"


def get_all_demand():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            product_code,
            product_name,
            machine_type,
            required_lots,
            required_date,
            active
        FROM demand
        ORDER BY required_date, product_code
    """)

    rows = cursor.fetchall()
    connection.close()

    demand_records = []

    for row in rows:
        demand_record = {
            "id": row["id"],
            "product_code": row["product_code"],
            "product_name": row["product_name"],
            "machine_type": row["machine_type"],
            "required_lots": row["required_lots"],
            "required_date": row["required_date"],
            "active": bool(row["active"])
        }

        demand_records.append(demand_record)

    return demand_records

def get_demand_by_id(demand_id):
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            product_code,
            product_name,
            machine_type,
            required_lots,
            required_date,
            active
        FROM demand
        WHERE id = ?
    """, (demand_id,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "product_code": row["product_code"],
        "product_name": row["product_name"],
        "machine_type": row["machine_type"],
        "required_lots": row["required_lots"],
        "required_date": row["required_date"],
        "active": bool(row["active"])
    }

def create_demand(demand):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO demand (
            product_code,
            product_name,
            machine_type,
            required_lots,
            required_date,
            active
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        demand["product_code"],
        demand["product_name"],
        demand["machine_type"],
        demand["required_lots"],
        demand["required_date"],
        int(demand["active"])
    ))

    connection.commit()

    new_demand_id = cursor.lastrowid
    connection.close()

    return get_demand_by_id(new_demand_id)

def update_demand(demand_id, demand):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE demand
        SET product_code = ?,
            product_name = ?,
            machine_type = ?,
            required_lots = ?,
            required_date = ?,
            active = ?
        WHERE id = ?
    """, (
        demand["product_code"],
        demand["product_name"],
        demand["machine_type"],
        demand["required_lots"],
        demand["required_date"],
        int(demand["active"]),
        demand_id
    ))

    connection.commit()
    rows_updated = cursor.rowcount
    connection.close()

    if rows_updated == 0:
        return None

    return get_demand_by_id(demand_id)

def delete_demand(demand_id):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM demand
        WHERE id = ?
    """, (demand_id,))

    connection.commit()
    rows_deleted = cursor.rowcount
    connection.close()

    return rows_deleted > 0


if __name__ == "__main__":
    demand_records = get_all_demand()

    for demand_record in demand_records:
        print(demand_record)