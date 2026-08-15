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

def generate_daily_schedule(year, month):
    available_dates = get_available_dates(year, month)

    machines = [
        machine
        for machine in machineDAO.get_all_machines()
        if machine["active"]
    ]

    demand_records = []

    for demand in demandDAO.get_all_demand():
        if not demand["active"]:
            continue

        demand_year, demand_month, _ = map(
            int,
            demand["required_date"].split("-")
        )

        if demand_year == year and demand_month == month:
            demand_records.append(demand)

    demand_records.sort(
        key=lambda item: (
            item["required_date"],
            item["product_code"]
        )
    )

    machines.sort(key=lambda item: item["machine_code"])

    schedule = []
    unallocated = []

    used_capacity = {}

    for demand in demand_records:
        remaining_lots = demand["required_lots"]

        eligible_machines = [
            machine
            for machine in machines
            if machine["production_area"]
            == demand["machine_type"]
        ]

        for planning_date in available_dates:
            for machine in eligible_machines:
                capacity_key = (
                    planning_date.isoformat(),
                    machine["id"]
                )

                lots_already_used = used_capacity.get(
                    capacity_key,
                    0
                )

                remaining_machine_capacity = (
                    machine["daily_capacity"]
                    - lots_already_used
                )

                if remaining_machine_capacity <= 0:
                    continue

                allocated_lots = min(
                    remaining_lots,
                    remaining_machine_capacity
                )

                schedule.append({
                    "production_date":
                        planning_date.isoformat(),
                    "machine_code":
                        machine["machine_code"],
                    "machine_type":
                        machine["production_area"],
                    "product_code":
                        demand["product_code"],
                    "product_name":
                        demand["product_name"],
                    "allocated_lots":
                        allocated_lots
                })

                used_capacity[capacity_key] = (
                    lots_already_used + allocated_lots
                )

                remaining_lots -= allocated_lots

                if remaining_lots == 0:
                    break

            if remaining_lots == 0:
                break

        if remaining_lots > 0:
            unallocated.append({
                "product_code": demand["product_code"],
                "product_name": demand["product_name"],
                "machine_type": demand["machine_type"],
                "required_lots": demand["required_lots"],
                "unallocated_lots": remaining_lots,
                "reason": "Insufficient active machine capacity"
            })

    return {
        "schedule": schedule,
        "unallocated": unallocated
    }


if __name__ == "__main__":
    plan = generate_daily_schedule(2026, 8)

    print("Schedule:")

    for allocation in plan["schedule"]:
        print(allocation)

    print("\nUnallocated demand:")

    for item in plan["unallocated"]:
        print(item)