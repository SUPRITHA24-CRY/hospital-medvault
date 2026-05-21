# Hospital Management System — Python + MySQL

A mini DBMS project built with Python 3 and MySQL.

---

## Project Structure

```
hospital_dbms/
├── setup.sql          ← Run this first to create DB + tables + sample data
├── hospital_dbms.py   ← Main Python terminal application
└── README.md
```

---

## Setup Instructions

### Step 1 — Install dependencies

```bash
pip install mysql-connector-python
```

### Step 2 — Start MySQL and run the schema

```bash
mysql -u root -p < setup.sql
```

Or open MySQL Workbench / terminal and paste the contents of `setup.sql`.

### Step 3 — Configure credentials

Open `hospital_dbms.py` and edit the top section:

```python
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",       # ← your MySQL username
    "password": "",           # ← your MySQL password
    "database": "hospital_db"
}
```

### Step 4 — Run the app

```bash
python hospital_dbms.py
```

---

## Features

| Module            | Operations                                              |
|-------------------|---------------------------------------------------------|
| Patients          | View, Search, Add, Update, Delete                       |
| Doctors           | View, Filter by dept, Add, Delete                       |
| Appointments      | View, Filter by status, Book, Update status, Cancel     |
| Medical Records   | View all, View by patient, Add                          |
| Billing           | View, Unpaid bills, Add, Mark paid                      |
| Reports           | Blood group stats, Doctor workload, Revenue, Dept view  |
| Raw SQL Terminal  | Type any SQL query interactively                        |

---

## Database Schema

```
departments   → dept_id, dept_name, location, head_doctor
doctors       → doctor_id, name, specialization, phone, email, dept_id
patients      → patient_id, name, age, gender, phone, address, blood_group
appointments  → appointment_id, patient_id, doctor_id, appt_date, status
medical_records → record_id, patient_id, doctor_id, diagnosis, prescription
billing       → bill_id, patient_id, appointment_id, amount, paid
```

---

## Requirements

- Python 3.8+
- MySQL 8.0+
- mysql-connector-python (`pip install mysql-connector-python`)
