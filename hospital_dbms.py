"""
╔══════════════════════════════════════════════════════╗
║       HOSPITAL MANAGEMENT SYSTEM — Python + MySQL    ║
╚══════════════════════════════════════════════════════╝
  Stack : Python 3 + mysql-connector-python
  DB    : MySQL (hospital_db)
  Run   : python hospital_dbms.py
"""

import mysql.connector
from mysql.connector import Error
from datetime import date
import os

# ─── CONFIG ────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",          # ← change if needed
    "password": "supritha@1.23",              # ← change to your MySQL password
    "database": "hospital_db"
}

# ─── COLOURS (ANSI) ────────────────────────────────────
C = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "cyan":   "\033[96m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "red":    "\033[91m",
    "blue":   "\033[94m",
    "magenta":"\033[95m",
    "white":  "\033[97m",
}

def clr(text, color): return f"{C[color]}{text}{C['reset']}"
def bold(text):       return f"{C['bold']}{text}{C['reset']}"

# ─── DB CONNECTION ─────────────────────────────────────
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(clr(f"\n[ERROR] Cannot connect to MySQL: {e}", "red"))
        print(clr("  → Check your DB_CONFIG at the top of this file.", "yellow"))
        return None

# ─── HELPERS ───────────────────────────────────────────
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    input(clr("\n  Press Enter to continue...", "yellow"))

def header(title):
    print(clr("\n" + "═" * 54, "cyan"))
    print(clr(f"  {title}", "cyan"))
    print(clr("═" * 54, "cyan"))

def print_table(cursor, rows):
    if not rows:
        print(clr("  (no records found)", "yellow"))
        return
    cols = [desc[0] for desc in cursor.description]
    widths = [max(len(str(col)), max((len(str(r[i])) for r in rows), default=0))
              for i, col in enumerate(cols)]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    fmt = "|" + "|".join(f" {{:<{w}}} " for w in widths) + "|"
    print(clr(sep, "blue"))
    print(clr(fmt.format(*cols), "cyan"))
    print(clr(sep, "blue"))
    for row in rows:
        print(fmt.format(*[str(v) if v is not None else "NULL" for v in row]))
    print(clr(sep, "blue"))
    print(clr(f"  {len(rows)} row(s) returned.", "green"))

def run_query(conn, sql, params=None, fetch=True):
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        if fetch:
            rows = cur.fetchall()
            print_table(cur, rows)
        else:
            conn.commit()
            print(clr(f"  ✔  {cur.rowcount} row(s) affected.", "green"))
        cur.close()
    except Error as e:
        print(clr(f"  [SQL ERROR] {e}", "red"))

def input_field(prompt, required=True, default=None):
    while True:
        val = input(f"  {prompt}{f' [{default}]' if default else ''}: ").strip()
        if val:
            return val
        if not required and default is not None:
            return default
        if not required:
            return None
        print(clr("  This field is required.", "red"))

# ══════════════════════════════════════════════════════
#  MODULES
# ══════════════════════════════════════════════════════

# ─── 1. PATIENTS ──────────────────────────────────────
def patients_menu(conn):
    while True:
        header("PATIENTS")
        print("  1. View all patients")
        print("  2. Search patient by name")
        print("  3. Add new patient")
        print("  4. Update patient details")
        print("  5. Delete patient")
        print("  0. Back")
        ch = input(clr("\n  Choice: ", "yellow"))

        if ch == "1":
            header("All Patients")
            run_query(conn, "SELECT patient_id, name, age, gender, blood_group, phone, admitted_on FROM patients ORDER BY patient_id")

        elif ch == "2":
            name = input_field("Enter name to search")
            header(f"Search: {name}")
            run_query(conn,
                "SELECT patient_id, name, age, gender, blood_group, phone, address FROM patients WHERE name LIKE %s",
                (f"%{name}%",))

        elif ch == "3":
            header("Add New Patient")
            name  = input_field("Full name")
            age   = input_field("Age")
            gender = input_field("Gender (Male/Female/Other)")
            phone  = input_field("Phone", required=False)
            address = input_field("Address", required=False)
            bg = input_field("Blood group (e.g. O+)", required=False)
            run_query(conn,
                "INSERT INTO patients (name, age, gender, phone, address, blood_group, admitted_on) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (name, age, gender, phone, address, bg, date.today()), fetch=False)

        elif ch == "4":
            pid = input_field("Patient ID to update")
            field = input_field("Field to update (name/age/phone/address/blood_group)")
            value = input_field("New value")
            allowed = {"name", "age", "phone", "address", "blood_group"}
            if field not in allowed:
                print(clr("  Invalid field.", "red"))
            else:
                run_query(conn, f"UPDATE patients SET {field}=%s WHERE patient_id=%s",
                          (value, pid), fetch=False)

        elif ch == "5":
            pid = input_field("Patient ID to delete")
            confirm = input(clr(f"  Delete patient #{pid}? (yes/no): ", "red"))
            if confirm.lower() == "yes":
                run_query(conn, "DELETE FROM patients WHERE patient_id=%s", (pid,), fetch=False)

        elif ch == "0":
            break
        pause()

# ─── 2. DOCTORS ───────────────────────────────────────
def doctors_menu(conn):
    while True:
        header("DOCTORS")
        print("  1. View all doctors")
        print("  2. Doctors by department")
        print("  3. Add new doctor")
        print("  4. Delete doctor")
        print("  0. Back")
        ch = input(clr("\n  Choice: ", "yellow"))

        if ch == "1":
            header("All Doctors")
            run_query(conn, """
                SELECT d.doctor_id, d.name, d.specialization, dept.dept_name, d.phone, d.available_days
                FROM doctors d LEFT JOIN departments dept ON d.dept_id = dept.dept_id
                ORDER BY d.doctor_id
            """)

        elif ch == "2":
            header("Departments")
            run_query(conn, "SELECT dept_id, dept_name FROM departments")
            did = input_field("Enter dept_id")
            run_query(conn, """
                SELECT doctor_id, name, specialization, phone, available_days
                FROM doctors WHERE dept_id=%s
            """, (did,))

        elif ch == "3":
            header("Add New Doctor")
            name  = input_field("Full name (e.g. Dr. X)")
            spec  = input_field("Specialization")
            phone = input_field("Phone", required=False)
            email = input_field("Email", required=False)
            run_query(conn, "SELECT dept_id, dept_name FROM departments")
            did   = input_field("Department ID")
            days  = input_field("Available days", required=False, default="Mon-Fri")
            run_query(conn,
                "INSERT INTO doctors (name, specialization, phone, email, dept_id, available_days) VALUES (%s,%s,%s,%s,%s,%s)",
                (name, spec, phone, email, did, days), fetch=False)

        elif ch == "4":
            did = input_field("Doctor ID to delete")
            confirm = input(clr(f"  Delete doctor #{did}? (yes/no): ", "red"))
            if confirm.lower() == "yes":
                run_query(conn, "DELETE FROM doctors WHERE doctor_id=%s", (did,), fetch=False)

        elif ch == "0":
            break
        pause()

# ─── 3. APPOINTMENTS ──────────────────────────────────
def appointments_menu(conn):
    while True:
        header("APPOINTMENTS")
        print("  1. View all appointments")
        print("  2. Filter by status")
        print("  3. Book new appointment")
        print("  4. Update appointment status")
        print("  5. Cancel appointment")
        print("  0. Back")
        ch = input(clr("\n  Choice: ", "yellow"))

        if ch == "1":
            header("All Appointments")
            run_query(conn, """
                SELECT a.appointment_id, p.name AS patient, d.name AS doctor,
                       a.appt_date, a.appt_time, a.status, a.notes
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN doctors  d ON a.doctor_id  = d.doctor_id
                ORDER BY a.appt_date DESC
            """)

        elif ch == "2":
            status = input_field("Status (Scheduled/Completed/Cancelled)")
            run_query(conn, """
                SELECT a.appointment_id, p.name AS patient, d.name AS doctor,
                       a.appt_date, a.appt_time, a.notes
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN doctors  d ON a.doctor_id  = d.doctor_id
                WHERE a.status = %s ORDER BY a.appt_date
            """, (status,))

        elif ch == "3":
            header("Book Appointment")
            run_query(conn, "SELECT patient_id, name FROM patients ORDER BY patient_id")
            pid = input_field("Patient ID")
            run_query(conn, "SELECT doctor_id, name, specialization FROM doctors ORDER BY doctor_id")
            did = input_field("Doctor ID")
            dt  = input_field("Date (YYYY-MM-DD)")
            tm  = input_field("Time (HH:MM)")
            notes = input_field("Notes", required=False)
            run_query(conn,
                "INSERT INTO appointments (patient_id, doctor_id, appt_date, appt_time, notes) VALUES (%s,%s,%s,%s,%s)",
                (pid, did, dt, tm, notes), fetch=False)

        elif ch == "4":
            aid = input_field("Appointment ID")
            status = input_field("New status (Scheduled/Completed/Cancelled)")
            run_query(conn, "UPDATE appointments SET status=%s WHERE appointment_id=%s",
                      (status, aid), fetch=False)

        elif ch == "5":
            aid = input_field("Appointment ID to cancel")
            run_query(conn, "UPDATE appointments SET status='Cancelled' WHERE appointment_id=%s",
                      (aid,), fetch=False)

        elif ch == "0":
            break
        pause()

# ─── 4. MEDICAL RECORDS ───────────────────────────────
def records_menu(conn):
    while True:
        header("MEDICAL RECORDS")
        print("  1. View all records")
        print("  2. View records for a patient")
        print("  3. Add medical record")
        print("  0. Back")
        ch = input(clr("\n  Choice: ", "yellow"))

        if ch == "1":
            run_query(conn, """
                SELECT r.record_id, p.name AS patient, d.name AS doctor,
                       r.diagnosis, r.treatment, r.record_date
                FROM medical_records r
                JOIN patients p ON r.patient_id = p.patient_id
                JOIN doctors  d ON r.doctor_id  = d.doctor_id
                ORDER BY r.record_date DESC
            """)

        elif ch == "2":
            pid = input_field("Patient ID")
            run_query(conn, """
                SELECT r.record_id, d.name AS doctor, r.diagnosis,
                       r.treatment, r.prescription, r.record_date
                FROM medical_records r
                JOIN doctors d ON r.doctor_id = d.doctor_id
                WHERE r.patient_id = %s ORDER BY r.record_date DESC
            """, (pid,))

        elif ch == "3":
            header("Add Medical Record")
            run_query(conn, "SELECT patient_id, name FROM patients")
            pid  = input_field("Patient ID")
            run_query(conn, "SELECT doctor_id, name FROM doctors")
            did  = input_field("Doctor ID")
            diag = input_field("Diagnosis")
            treat = input_field("Treatment", required=False)
            presc = input_field("Prescription", required=False)
            run_query(conn,
                "INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment, prescription, record_date) VALUES (%s,%s,%s,%s,%s,%s)",
                (pid, did, diag, treat, presc, date.today()), fetch=False)

        elif ch == "0":
            break
        pause()

# ─── 5. BILLING ───────────────────────────────────────
def billing_menu(conn):
    while True:
        header("BILLING")
        print("  1. View all bills")
        print("  2. Unpaid bills")
        print("  3. Add bill")
        print("  4. Mark bill as paid")
        print("  0. Back")
        ch = input(clr("\n  Choice: ", "yellow"))

        if ch == "1":
            run_query(conn, """
                SELECT b.bill_id, p.name AS patient, b.amount,
                       IF(b.paid,'Yes','No') AS paid, b.bill_date
                FROM billing b JOIN patients p ON b.patient_id = p.patient_id
                ORDER BY b.bill_date DESC
            """)

        elif ch == "2":
            header("Unpaid Bills")
            run_query(conn, """
                SELECT b.bill_id, p.name AS patient, b.amount, b.bill_date
                FROM billing b JOIN patients p ON b.patient_id = p.patient_id
                WHERE b.paid = FALSE ORDER BY b.bill_date
            """)

        elif ch == "3":
            run_query(conn, "SELECT patient_id, name FROM patients")
            pid = input_field("Patient ID")
            amt = input_field("Amount (₹)")
            run_query(conn,
                "INSERT INTO billing (patient_id, amount, bill_date) VALUES (%s,%s,%s)",
                (pid, amt, date.today()), fetch=False)

        elif ch == "4":
            bid = input_field("Bill ID to mark paid")
            run_query(conn, "UPDATE billing SET paid=TRUE WHERE bill_id=%s", (bid,), fetch=False)

        elif ch == "0":
            break
        pause()

# ─── 6. SQL TERMINAL ──────────────────────────────────
def sql_terminal(conn):
    header("RAW SQL TERMINAL")
    print(clr("  Type any SQL query. Type 'exit' to go back.", "yellow"))
    print(clr("  Type 'tables' to list all tables.\n", "yellow"))
    while True:
        try:
            sql = input(clr("  SQL> ", "magenta")).strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not sql:
            continue
        if sql.lower() == "exit":
            break
        if sql.lower() == "tables":
            sql = "SHOW TABLES"
        fetch = sql.strip().upper().startswith(("SELECT", "SHOW", "DESCRIBE", "DESC", "EXPLAIN"))
        run_query(conn, sql, fetch=fetch)

# ─── 7. REPORTS ───────────────────────────────────────
def reports_menu(conn):
    while True:
        header("REPORTS & ANALYTICS")
        print("  1. Patient count by blood group")
        print("  2. Appointments per doctor")
        print("  3. Revenue summary")
        print("  4. Department overview")
        print("  5. Today's appointments")
        print("  0. Back")
        ch = input(clr("\n  Choice: ", "yellow"))

        if ch == "1":
            run_query(conn, "SELECT blood_group, COUNT(*) AS total FROM patients GROUP BY blood_group ORDER BY total DESC")

        elif ch == "2":
            run_query(conn, """
                SELECT d.name AS doctor, d.specialization,
                       COUNT(a.appointment_id) AS total_appointments
                FROM doctors d LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
                GROUP BY d.doctor_id ORDER BY total_appointments DESC
            """)

        elif ch == "3":
            run_query(conn, """
                SELECT
                  SUM(amount)              AS total_billed,
                  SUM(CASE WHEN paid THEN amount ELSE 0 END) AS collected,
                  SUM(CASE WHEN NOT paid THEN amount ELSE 0 END) AS pending
                FROM billing
            """)

        elif ch == "4":
            run_query(conn, """
                SELECT dept.dept_name, dept.location, dept.head_doctor,
                       COUNT(d.doctor_id) AS num_doctors
                FROM departments dept
                LEFT JOIN doctors d ON dept.dept_id = d.dept_id
                GROUP BY dept.dept_id
            """)

        elif ch == "5":
            run_query(conn, """
                SELECT a.appointment_id, p.name AS patient, d.name AS doctor,
                       a.appt_time, a.status
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                JOIN doctors  d ON a.doctor_id  = d.doctor_id
                WHERE a.appt_date = CURDATE()
                ORDER BY a.appt_time
            """)

        elif ch == "0":
            break
        pause()

# ══════════════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════════════
def main():
    clear()
    print(clr("""
  ╔══════════════════════════════════════════════════╗
  ║     HOSPITAL MANAGEMENT SYSTEM — Python+MySQL    ║
  ╚══════════════════════════════════════════════════╝""", "cyan"))

    conn = get_connection()
    if not conn:
        return

    print(clr("  ✔  Connected to MySQL — hospital_db\n", "green"))

    while True:
        header("MAIN MENU")
        print("  1. Patients")
        print("  2. Doctors")
        print("  3. Appointments")
        print("  4. Medical Records")
        print("  5. Billing")
        print("  6. Reports & Analytics")
        print("  7. Raw SQL Terminal")
        print("  0. Exit")
        ch = input(clr("\n  Choice: ", "yellow"))

        if   ch == "1": patients_menu(conn)
        elif ch == "2": doctors_menu(conn)
        elif ch == "3": appointments_menu(conn)
        elif ch == "4": records_menu(conn)
        elif ch == "5": billing_menu(conn)
        elif ch == "6": reports_menu(conn)
        elif ch == "7": sql_terminal(conn)
        elif ch == "0":
            print(clr("\n  Goodbye!\n", "cyan"))
            break

    conn.close()

if __name__ == "__main__":
    main()
