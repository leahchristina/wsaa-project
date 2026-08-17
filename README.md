# Production Capacity Scenario Planner

A Flask web application for managing production machines, recording monthly production demand, and generating capacity-based production plans.

The application was developed for the Web Services and Applications module. It demonstrates RESTful APIs, CRUD operations, JSON, XML, CSV processing, HTTP methods and status codes, SQLite, Python, HTML, JavaScript, AJAX and CSS.

## Hosted Application

The hosted application will be available at:

**Hosted URL:** https://leahchristina.pytho**nywhere.com

Note that this has been hosted on PythonAnywhere under a free domain. The webpage will be available until **September 17, 2026.**

## GitHub Repository

https://github.com/leahchristina/wsaa-project

## Project Purpose

Production planning is often completed using spreadsheets. This can make it difficult to compare demand against available capacity, identify shortfalls and understand the effect of taking a machine out of service.

The Production Capacity Scenario Planner provides a simple browser-based system that allows users to:

- Maintain production machines and their daily capacities
- Add and update monthly production demand
- Import demand records from CSV
- Decommission and recommission machines
- Deactivate and reactivate demand records
- Calculate capacity by machine type
- Generate a daily production schedule
- Identify unallocated demand and capacity shortfalls
- Export the generated schedule to CSV
- Retrieve planning information through JSON and XML APIs

All machine, product and demand names in this repository are fictional. Leonardo, Raphael, Donatello and Michelangelo are used as fictional machine types to avoid exposing company intellectual property.

## Main Features

### Machine Management

Users can:

- Add a machine
- View all machines
- Update machine details and daily capacity
- Decommission a machine
- Recommission a machine

Machines are decommissioned rather than permanently removed. This is a soft-delete approach that preserves machine information for historical planning records.

### Production Demand Management

Users can:

- Add monthly production demand
- View all demand records
- Update demand details
- Deactivate demand
- Reactivate demand
- Import multiple demand records from CSV

Inactive demand remains in the database but is excluded from production planning.

### CSV Import

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

### Production Planning

The user selects a planning month and generates a production plan.

The planning logic:

- Includes active machines only
- Includes active demand only
- Matches demand to the required machine type
- Uses each machine's configured daily lot capacity
- Allocates demand in required-date and product-code order
- Assumes 24/7 manufacturing
- Excludes 25 and 26 December
- Reports any lots that cannot be allocated
- Calculates the planned completion date
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

### Planning Results

The generated plan displays:

- Total required lots
- Total allocated lots
- Total unallocated lots
- Feasibility status
- Planned completion date
- Capacity by machine type
- Daily production allocations
- Unallocated demand and its reason

### CSV Export

The generated daily schedule can be downloaded as a CSV file.

The exported file contains:

```text
production_date
machine_code
machine_type
product_code
product_name
allocated_lots
```

### JSON and XML

JSON is used for the main REST API requests and responses.

A read-only XML endpoint is also provided to demonstrate an alternative web-service data format:

```text
/api/planning-summary.xml?year=2026&month=8
```

## Technologies Used

- Python
- Flask
- SQLite
- Python `sqlite3`
- HTML5
- CSS3
- Vanilla JavaScript
- Fetch API and AJAX
- JSON
- XML
- CSV
- Git and GitHub
- PythonAnywhere

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
│   │   └── styles.css
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

### 1. Clone the repository

```bash
git clone https://github.com/leahchristina/wsaa-project.git
```

Move into the project folder:

```bash
cd wsaa-project
```

### 2. Create a Python environment

Using Conda:

```bash
conda create --name capacity-planner python=3.12
```

Activate the environment:

```bash
conda activate capacity-planner
```

### 3. Install the project requirements

```bash
pip install -r requirements.txt
```

### 4. Create the database

```bash
python create_database.py
```

This creates the SQLite database and the required database tables if they do not already exist.

### 5. Run the application

```bash
python app.py
```

Open the following address in a browser:

```text
http://127.0.0.1:5000/
```

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

