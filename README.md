# Production Capacity Scenario Planner

![Python](https://img.shields.io/badge/Python-3.12-2E4AED)
![Flask](https://img.shields.io/badge/Flask-Web%20API-000075)
![Database](https://img.shields.io/badge/Database-SQLite-00BFDE)
![JavaScript](https://img.shields.io/badge/JavaScript-AJAX-8054F2)
![Status](https://img.shields.io/badge/Status-Deployed-16834A)

A Flask web application for managing production machines, recording monthly production demand and generating capacity-based production plans.

The application was developed for the Web Services and Applications module. It demonstrates RESTful APIs, CRUD operations, JSON, XML, CSV processing, HTTP methods and status codes, SQLite, Python, HTML, JavaScript, AJAX and CSS.

## Hosted Application

[![Open Hosted Application](https://img.shields.io/badge/Open%20Application-PythonAnywhere-2E4AED?style=for-the-badge)](https://leahchristina.pythonanywhere.com)

> **Availability:** The application is hosted using a free PythonAnywhere account and is expected to remain available until **17 September 2026**.

## Quick Links

- [Open the hosted application](https://leahchristina.pythonanywhere.com)
- [Main Features](#main-features)
- [Suggested Demonstration](#suggested-demonstration)
- [Technologies Used](#technologies-used)
- [Local Installation](#local-installation)
- [Running the Automated Tests](#running-the-automated-tests)

## Project Purpose

I wanted to create something that would be useful in my current role. Production planning is currently completed using manual calculations and spreadsheets. This can make it difficult to compare demand against available capacity, identify shortfalls and understand the effect of taking a machine out of service for maintenance.

This project is a simplified, fictionalised version of a tool that could support production-planning activities in my current role, with company intellectual property removed.

The Production Capacity Scenario Planner provides a browser-based system that allows users to:

- Maintain a list of production machines and their daily capacities
- Add and update monthly production demand
- Import demand records from CSV files
- Decommission and recommission machines
- Calculate capacity by machine type
- Generate a daily production schedule
- Identify unallocated demand and capacity shortfalls
- Export the generated schedule to CSV
- Retrieve planning information through JSON and XML APIs

> **Data protection note:** All machine, product and demand names in this repository are fictional. Leonardo, Raphael, Donatello and Michelangelo are used as fictional machine types to avoid exposing company intellectual property.

## Main Features

| Area | Capability |
|---|---|
| Machine management | Add, view, update, decommission, recommission and delete machines |
| Demand management | Add, update, deactivate, reactivate and delete monthly demand |
| CSV processing | Validate and import demand from CSV files |
| Capacity planning | Compare monthly demand with available machine capacity |
| Scheduling | Allocate lots to active machines by production date |
| Exception management | Identify capacity shortfalls and unallocated demand |
| Data export | Export the generated production schedule to CSV |
| Web services | Access planning data through JSON and XML endpoints |
| Testing | Run automated API and calendar-rule tests |
| Hosting | Access the deployed application through PythonAnywhere |

### 1. Machine Management

Users can:

- Add a machine
- View all machines
- Update machine details and daily capacity
- Decommission or recommission a machine
- Permanently delete a machine entered in error

Machines can be decommissioned rather than permanently removed. This soft-delete approach preserves machine information for historical planning records, while the permanent-delete option is available for erroneous entries.

### 2. Production Demand Management

Users can:

- Add monthly production demand
- View all demand records
- Update demand details
- Deactivate or reactivate demand
- Permanently delete demand entered in error
- Import multiple demand records from CSV

Inactive demand remains in the database but is excluded from production planning.

#### CSV Import

Demand can be imported using a UTF-8 CSV file.

The required columns are:

```csv
product_code,product_name,machine_type,required_lots,required_date,active
```

Example:

```csv
PROD-004,Product Delta,MICH,10,2026-09-30,true
PROD-005,Product Echo,LEON,18,2026-09-30,true
PROD-006,Product Foxtrot,RAPH,14,2026-09-30,true
```

The application validates every row before saving any records. If one or more rows are invalid, the entire file is rejected. This prevents partial imports.

A CSV template can be downloaded from the application or directly from:

```text
/api/demand/template.csv
```

### 3. Production Planning

The user selects a planning month and generates a production plan.

The planning logic:

- Includes active machines and active demand only
- Matches demand to the required machine type
- Uses each machine's configured daily lot capacity
- Allocates demand in required-date and product-code order
- Assumes 24/7 manufacturing, excluding 25 and 26 December
- Reports any lots that cannot be allocated
- Identifies whether the plan is feasible

The four fictional machine types are:

```text
LEON - Leonardo
RAPH - Raphael
DONA - Donatello
MICH - Michelangelo
```

Demand for a machine type can use any active machine whose production area matches that type.

For example, demand assigned to `LEON` can be allocated to active machines such as `LEON-01` and `LEON-02`.

#### Planning Results

The generated plan displays:

- Total required lots
- Total allocated lots
- Total unallocated lots
- Feasibility status
- Planned completion date
- Capacity by machine type
- Daily production allocations
- Unallocated demand and its reason

#### CSV Export

The generated daily schedule can be downloaded as a CSV file containing:

```text
production_date
machine_code
machine_type
product_code
product_name
allocated_lots
```

#### JSON and XML

JSON is used for the main REST API requests and responses.

A read-only XML endpoint is also provided to demonstrate an alternative web-service data format:

```text
/api/planning-summary.xml?year=2026&month=8
```

## Suggested Demonstration

To explore the application:

1. Open the [hosted application](https://leahchristina.pythonanywhere.com).
2. Review the active and decommissioned machines.
3. Add or import a monthly demand record.
4. Select a planning month.
5. Click **Generate Plan**.
6. Review the capacity summary and daily production schedule.
7. Check whether any demand is unallocated.
8. Export the production schedule to CSV.
9. Open the XML planning-summary endpoint.

## Technologies Used

- **Back end:** Python and Flask
- **Database:** SQLite and Python's `sqlite3` module
- **Front end:** HTML5, CSS3 and vanilla JavaScript
- **Asynchronous communication:** Fetch API and AJAX
- **Data formats:** JSON, XML and CSV
- **Testing:** Python `unittest` and Flask test client
- **Version control:** Git and GitHub
- **Hosting:** PythonAnywhere

## Application Architecture

```text
Browser Interface
       |
       | Fetch / AJAX
       v
Flask REST API
       |
       +-------------------+
       |                   |
       v                   v
DAO Layer             Planning Service
       |                   |
       v                   |
SQLite Database <----------+
```

- The browser interface does not connect directly to SQLite.
- Flask receives and validates HTTP requests.
- DAO modules contain the SQL database operations.
- The planning service calculates capacity and creates the daily schedule.
- API responses are returned primarily as JSON, with one XML endpoint for an alternative data representation.

## Project Structure

```text
wsaa-project/
├── app.py
├── create_database.py
├── machineDAO.py
├── demandDAO.py
├── planner.py
├── capacity_planner.db
├── requirements.txt
├── README.md
├── static/
│   ├── css/
│   │   ├── styles.css
│   │   └── abbott-theme.css
│   └── js/
│       ├── machines.js
│       ├── demand.js
│       └── planning.js
├── templates/
│   └── index.html
├── sample_data/
│   ├── sample_demand.csv
│   └── browser_import_test.csv
└── tests/
    ├── test_api.py
    └── test_planner.py
```

## Local Installation

### Requirements

Before running the application, ensure the following are installed:

- Python
- Git
- A web browser

The project was developed on Windows using Anaconda and Visual Studio Code.

### 1. Clone the Repository

```bash
git clone https://github.com/leahchristina/wsaa-project.git
cd wsaa-project
```

### 2. Create a Python Environment

Using Conda:

```bash
conda create --name capacity-planner python=3.12
conda activate capacity-planner
```

### 3. Install the Project Requirements

```bash
pip install -r requirements.txt
```

### 4. Create the Database

```bash
python create_database.py
```

This creates the SQLite database and the required database tables if they do not already exist.

### 5. Run the Application

```bash
python app.py
```

Open the application in a browser:

[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

The Flask server used locally is a development server and should not be used as a production web server.

## Running the Automated Tests

Stop the Flask server before running the tests.

Run all tests from the main project folder:

```bash
python -m unittest discover -s tests
```

A successful test run should end with:

```text
OK
```
