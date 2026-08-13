import calendar
from datetime import date
import machineDAO
import demandDAO


def get_available_dates(year, month):
    days_in_month = calendar.monthrange(year, month)[1]
    available_dates = []

    for day_number in range(1, days_in_month + 1):
        planning_date = date(year, month, day_number)

        is_christmas_shutdown = (
            month == 12
            and day_number in (25, 26)
        )

        if not is_christmas_shutdown:
            available_dates.append(planning_date)

    return available_dates

def calculate_capacity(year, month):
    available_dates = get_available_dates(year, month)
    available_days = len(available_dates)

    machines = machineDAO.get_all_machines()
    capacity_by_type = {}

    for machine in machines:
        if not machine["active"]:
            continue

        machine_type = machine["production_area"]

        if machine_type not in capacity_by_type:
            capacity_by_type[machine_type] = {
                "machine_type": machine_type,
                "available_machines": 0,
                "available_days": available_days,
                "total_capacity": 0
            }

        capacity_by_type[machine_type][
            "available_machines"
        ] += 1

        capacity_by_type[machine_type][
            "total_capacity"
        ] += machine["daily_capacity"] * available_days

    return list(capacity_by_type.values())

def calculate_demand(year, month):
    demand_records = demandDAO.get_all_demand()
    demand_by_type = {}

    for demand in demand_records:
        if not demand["active"]:
            continue

        required_year, required_month, _ = map(
            int,
            demand["required_date"].split("-")
        )

        if required_year != year or required_month != month:
            continue

        machine_type = demand["machine_type"]

        if machine_type not in demand_by_type:
            demand_by_type[machine_type] = {
                "machine_type": machine_type,
                "required_lots": 0
            }

        demand_by_type[machine_type]["required_lots"] += (
            demand["required_lots"]
        )

    return list(demand_by_type.values())

def generate_capacity_summary(year, month):
    capacity_results = calculate_capacity(year, month)
    demand_results = calculate_demand(year, month)

    capacity_lookup = {
        item["machine_type"]: item
        for item in capacity_results
    }

    demand_lookup = {
        item["machine_type"]: item
        for item in demand_results
    }

    machine_types = ["LEON", "RAPH", "DONA", "MICH"]
    summary = []

    for machine_type in machine_types:
        capacity = capacity_lookup.get(machine_type, {
            "available_machines": 0,
            "available_days": len(
                get_available_dates(year, month)
            ),
            "total_capacity": 0
        })

        demand = demand_lookup.get(machine_type, {
            "required_lots": 0
        })

        total_capacity = capacity["total_capacity"]
        required_lots = demand["required_lots"]
        capacity_balance = total_capacity - required_lots

        if capacity_balance >= 0:
            result = "Capacity available"
        else:
            result = "Capacity shortfall"

        summary.append({
            "machine_type": machine_type,
            "available_machines": capacity["available_machines"],
            "available_days": capacity["available_days"],
            "total_capacity": total_capacity,
            "required_lots": required_lots,
            "capacity_balance": capacity_balance,
            "result": result
        })

    return summary


if __name__ == "__main__":
    summary_results = generate_capacity_summary(2026, 8)

    for result in summary_results:
        print(result)