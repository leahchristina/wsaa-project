import sqlite3


DATABASE_NAME = "capacity_planner.db"


def create_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS machines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_code TEXT NOT NULL UNIQUE,
            machine_name TEXT NOT NULL,
            production_area TEXT NOT NULL,
            daily_capacity INTEGER NOT NULL CHECK (daily_capacity > 0),
            active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
        )
    """)

    connection.commit()
    connection.close()

    print("Database and machines table created successfully.")


def test_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO machines (
            machine_code,
            machine_name,
            production_area,
            daily_capacity,
            active
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        "LEON-01",
        "Leonardo Machine 1",
        "LEON",
        4,
        1
    ))

    connection.commit()

    cursor.execute("SELECT * FROM machines")
    machines = cursor.fetchall()

    for machine in machines:
        print(machine)

    connection.close()

if __name__ == "__main__":
    create_database()
    test_database()