from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from datetime import date
import functools
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "hospital_secret_key_2025")


def get_db_config():
    config = {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", "supritha@1.23"),
        "database": os.environ.get("MYSQL_DATABASE", "hospital_db"),
    }
    port = os.environ.get("MYSQL_PORT")
    if port:
        config["port"] = int(port)
    if os.environ.get("MYSQL_SSL", "").lower() in ("1", "true", "yes"):
        config["ssl_disabled"] = False
    return config


def db():
    return mysql.connector.connect(**get_db_config())

# ── AUTH DECORATORS ───────────────────────────────────
def login_required(role=None):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            if "user" not in session:
                flash("Please login first.", "error")
                return redirect(url_for("login"))
            if role and session["user"]["role"] != role:
                flash("Access denied.", "error")
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return wrapped
    return decorator

# ── LOGIN / LOGOUT ────────────────────────────────────
@app.route("/", methods=["GET","POST"])
def login():
    if "user" in session:
        role = session["user"]["role"]
        if role == "admin":   return redirect(url_for("admin_home"))
        if role == "doctor":  return redirect(url_for("doctor_home"))
        if role == "patient": return redirect(url_for("patient_home"))

    if request.method == "POST":
        role     = request.form["role"]
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = db(); cur = conn.cursor(dictionary=True)

        if role == "admin":
            if username == "admin" and password == "admin123":
                session["user"] = {"role":"admin","name":"Administrator","id":0}
                cur.close(); conn.close()
                return redirect(url_for("admin_home"))
            else:
                flash("Invalid admin credentials.", "error")

        elif role == "doctor":
            cur.execute("SELECT * FROM doctors WHERE license_number=%s AND password=%s", (username, password))
            doc = cur.fetchone()
            if doc:
                session["user"] = {"role":"doctor","name":doc["name"],"id":doc["doctor_id"]}
                cur.close(); conn.close()
                return redirect(url_for("doctor_home"))
            else:
                flash("Invalid license number or password.", "error")

        elif role == "patient":
            cur.execute("SELECT * FROM patients WHERE email=%s AND password=%s", (username, password))
            pat = cur.fetchone()
            if pat:
                session["user"] = {"role":"patient","name":pat["name"],"id":pat["patient_id"]}
                cur.close(); conn.close()
                return redirect(url_for("patient_home"))
            else:
                flash("Invalid email or password.", "error")

        cur.close(); conn.close()
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ══════════════════════════════════════════════════════
#  ADMIN ROUTES
# ══════════════════════════════════════════════════════
@app.route("/admin")
@login_required("admin")
def admin_home():
    conn = db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS c FROM patients"); pc = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM doctors");  dc = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM appointments WHERE status='Scheduled'"); ac = cur.fetchone()["c"]
    cur.execute("SELECT SUM(amount) AS t FROM billing WHERE paid=FALSE"); up = cur.fetchone()["t"] or 0
    cur.close(); conn.close()
    return render_template("admin/home.html", patients_count=pc, doctors_count=dc, appt_count=ac, unpaid=up)

@app.route("/admin/patients")
@login_required("admin")
def admin_patients():
    conn = db(); cur = conn.cursor(dictionary=True)
    search = request.args.get("search","").strip()
    if search:
        cur.execute("SELECT * FROM patients WHERE name LIKE %s OR patient_id=%s ORDER BY patient_id DESC",
                    (f"%{search}%", search if search.isdigit() else -1))
    else:
        cur.execute("SELECT * FROM patients ORDER BY patient_id DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("admin/patients.html", patients=rows, search=search)

@app.route("/admin/patients/add", methods=["GET","POST"])
@login_required("admin")
def admin_add_patient():
    if request.method == "POST":
        conn = db(); cur = conn.cursor()
        cur.execute("INSERT INTO patients (name,age,gender,phone,address,blood_group,email,password,admitted_on) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (request.form["name"], request.form["age"], request.form["gender"],
             request.form["phone"], request.form.get("address",""),
             request.form.get("blood_group",""), request.form.get("email",""),
             request.form.get("password","patient123"), date.today()))
        conn.commit(); cur.close(); conn.close()
        flash("Patient added!", "success")
        return redirect(url_for("admin_patients"))
    return render_template("admin/add_patient.html")

@app.route("/admin/patients/delete/<int:pid>")
@login_required("admin")
def admin_delete_patient(pid):
    conn = db(); cur = conn.cursor()
    cur.execute("DELETE FROM patients WHERE patient_id=%s", (pid,))
    conn.commit(); cur.close(); conn.close()
    flash("Patient deleted.", "info")
    return redirect(url_for("admin_patients"))

@app.route("/admin/doctors")
@login_required("admin")
def admin_doctors():
    conn = db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT d.*, dept.dept_name FROM doctors d LEFT JOIN departments dept ON d.dept_id=dept.dept_id ORDER BY d.doctor_id")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("admin/doctors.html", doctors=rows)

@app.route("/admin/doctors/add", methods=["GET","POST"])
@login_required("admin")
def admin_add_doctor():
    conn = db(); cur = conn.cursor(dictionary=True)
    if request.method == "POST":
        cur2 = conn.cursor()
        cur2.execute("INSERT INTO doctors (name,specialization,phone,email,dept_id,available_days,license_number,password) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (request.form["name"], request.form["specialization"],
             request.form.get("phone",""), request.form.get("email",""),
             request.form["dept_id"], request.form.get("available_days","Mon-Fri"),
             request.form["license_number"], request.form.get("password","doctor123")))
        conn.commit(); cur2.close(); cur.close(); conn.close()
        flash("Doctor added!", "success")
        return redirect(url_for("admin_doctors"))
    cur.execute("SELECT * FROM departments ORDER BY dept_name")
    depts = cur.fetchall()
    cur.close(); conn.close()
    return render_template("admin/add_doctor.html", depts=depts)

@app.route("/admin/appointments")
@login_required("admin")
def admin_appointments():
    conn = db(); cur = conn.cursor(dictionary=True)
    status = request.args.get("status","")
    if status:
        cur.execute("SELECT a.*,p.name AS patient,d.name AS doctor,d.specialization FROM appointments a JOIN patients p ON a.patient_id=p.patient_id JOIN doctors d ON a.doctor_id=d.doctor_id WHERE a.status=%s ORDER BY a.appt_date DESC", (status,))
    else:
        cur.execute("SELECT a.*,p.name AS patient,d.name AS doctor,d.specialization FROM appointments a JOIN patients p ON a.patient_id=p.patient_id JOIN doctors d ON a.doctor_id=d.doctor_id ORDER BY a.appt_date DESC")
    rows = cur.fetchall()
    cur.close(); conn.close()
    return render_template("admin/appointments.html", appts=rows, status=status)

@app.route("/admin/appointments/update/<int:aid>/<status>")
@login_required("admin")
def admin_update_appt(aid, status):
    conn = db(); cur = conn.cursor()
    cur.execute("UPDATE appointments SET status=%s WHERE appointment_id=%s", (status, aid))
    conn.commit(); cur.close(); conn.close()
    flash(f"Appointment marked as {status}.", "info")
    return redirect(url_for("admin_appointments"))

@app.route("/admin/billing")
@login_required("admin")
def admin_billing():
    conn = db(); cur = conn.cursor(dictionary=True)
    paid = request.args.get("paid","")
    if paid == "0":
        cur.execute("SELECT b.*,p.name AS patient FROM billing b JOIN patients p ON b.patient_id=p.patient_id WHERE b.paid=FALSE ORDER BY b.bill_date DESC")
    elif paid == "1":
        cur.execute("SELECT b.*,p.name AS patient FROM billing b JOIN patients p ON b.patient_id=p.patient_id WHERE b.paid=TRUE ORDER BY b.bill_date DESC")
    else:
        cur.execute("SELECT b.*,p.name AS patient FROM billing b JOIN patients p ON b.patient_id=p.patient_id ORDER BY b.bill_date DESC")
    rows = cur.fetchall()
    cur.execute("SELECT SUM(amount) AS t FROM billing"); total = cur.fetchone()["t"] or 0
    cur.execute("SELECT SUM(amount) AS t FROM billing WHERE paid=TRUE"); collected = cur.fetchone()["t"] or 0
    cur.execute("SELECT SUM(amount) AS t FROM billing WHERE paid=FALSE"); pending = cur.fetchone()["t"] or 0
    cur.close(); conn.close()
    return render_template("admin/billing.html", bills=rows, total=total, collected=collected, pending=pending, paid=paid)

@app.route("/admin/billing/pay/<int:bid>")
@login_required("admin")
def admin_pay_bill(bid):
    conn = db(); cur = conn.cursor()
    cur.execute("UPDATE billing SET paid=TRUE WHERE bill_id=%s", (bid,))
    conn.commit(); cur.close(); conn.close()
    flash("Bill marked as paid!", "success")
    return redirect(url_for("admin_billing"))

@app.route("/admin/billing/add", methods=["GET","POST"])
@login_required("admin")
def admin_add_bill():
    conn = db(); cur = conn.cursor(dictionary=True)
    if request.method == "POST":
        cur2 = conn.cursor()
        cur2.execute("INSERT INTO billing (patient_id,amount,bill_date) VALUES (%s,%s,%s)",
            (request.form["patient_id"], request.form["amount"], date.today()))
        conn.commit(); cur2.close(); cur.close(); conn.close()
        flash("Bill added!", "success")
        return redirect(url_for("admin_billing"))
    cur.execute("SELECT patient_id,name FROM patients ORDER BY name")
    patients = cur.fetchall()
    cur.close(); conn.close()
    return render_template("admin/add_bill.html", patients=patients)

@app.route("/admin/reports")
@login_required("admin")
def admin_reports():
    conn = db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT blood_group, COUNT(*) AS total FROM patients GROUP BY blood_group ORDER BY total DESC")
    blood_groups = cur.fetchall()
    cur.execute("SELECT d.name AS doctor, COUNT(a.appointment_id) AS total FROM doctors d LEFT JOIN appointments a ON d.doctor_id=a.doctor_id GROUP BY d.doctor_id ORDER BY total DESC")
    doctor_stats = cur.fetchall()
    cur.execute("SELECT status, COUNT(*) AS total FROM appointments GROUP BY status")
    appt_stats = cur.fetchall()
    cur.execute("SELECT SUM(amount) AS total, SUM(CASE WHEN paid THEN amount ELSE 0 END) AS collected, SUM(CASE WHEN NOT paid THEN amount ELSE 0 END) AS pending FROM billing")
    revenue = cur.fetchone()
    cur.close(); conn.close()
    return render_template("admin/reports.html", blood_groups=blood_groups, doctor_stats=doctor_stats, appt_stats=appt_stats, revenue=revenue)

# ══════════════════════════════════════════════════════
#  DOCTOR ROUTES
# ══════════════════════════════════════════════════════
@app.route("/doctor")
@login_required("doctor")
def doctor_home():
    did = session["user"]["id"]
    conn = db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT d.*, dept.dept_name FROM doctors d LEFT JOIN departments dept ON d.dept_id=dept.dept_id WHERE d.doctor_id=%s", (did,))
    doctor = cur.fetchone()
    cur.execute("SELECT COUNT(*) AS c FROM appointments WHERE doctor_id=%s AND status='Scheduled'", (did,)); scheduled = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM appointments WHERE doctor_id=%s AND status='Completed'", (did,)); completed = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM appointments WHERE doctor_id=%s AND appt_date=CURDATE()", (did,)); today = cur.fetchone()["c"]
    cur.execute("""SELECT a.*, p.name AS patient, p.age, p.blood_group FROM appointments a
                   JOIN patients p ON a.patient_id=p.patient_id
                   WHERE a.doctor_id=%s AND a.appt_date=CURDATE() ORDER BY a.appt_time""", (did,))
    today_appts = cur.fetchall()
    cur.close(); conn.close()
    return render_template("doctor/home.html", doctor=doctor, scheduled=scheduled, completed=completed, today=today, today_appts=today_appts)

@app.route("/doctor/appointments")
@login_required("doctor")
def doctor_appointments():
    did = session["user"]["id"]
    conn = db(); cur = conn.cursor(dictionary=True)
    status = request.args.get("status","")
    if status:
        cur.execute("SELECT a.*,p.name AS patient,p.age,p.blood_group,p.phone FROM appointments a JOIN patients p ON a.patient_id=p.patient_id WHERE a.doctor_id=%s AND a.status=%s ORDER BY a.appt_date DESC", (did, status))
    else:
        cur.execute("SELECT a.*,p.name AS patient,p.age,p.blood_group,p.phone FROM appointments a JOIN patients p ON a.patient_id=p.patient_id WHERE a.doctor_id=%s ORDER BY a.appt_date DESC", (did,))
    appts = cur.fetchall()
    cur.close(); conn.close()
    return render_template("doctor/appointments.html", appts=appts, status=status)

@app.route("/doctor/appointments/update/<int:aid>/<status>")
@login_required("doctor")
def doctor_update_appt(aid, status):
    conn = db(); cur = conn.cursor()
    cur.execute("UPDATE appointments SET status=%s WHERE appointment_id=%s", (status, aid))
    conn.commit(); cur.close(); conn.close()
    flash(f"Appointment marked as {status}.", "info")
    return redirect(url_for("doctor_appointments"))

@app.route("/doctor/patients")
@login_required("doctor")
def doctor_patients():
    did = session["user"]["id"]
    conn = db(); cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT DISTINCT p.* FROM patients p
                   JOIN appointments a ON p.patient_id=a.patient_id
                   WHERE a.doctor_id=%s ORDER BY p.name""", (did,))
    patients = cur.fetchall()
    cur.close(); conn.close()
    return render_template("doctor/patients.html", patients=patients)

@app.route("/doctor/profile")
@login_required("doctor")
def doctor_profile():
    did = session["user"]["id"]
    conn = db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT d.*, dept.dept_name FROM doctors d LEFT JOIN departments dept ON d.dept_id=dept.dept_id WHERE d.doctor_id=%s", (did,))
    doctor = cur.fetchone()
    cur.close(); conn.close()
    return render_template("doctor/profile.html", doctor=doctor)

# ══════════════════════════════════════════════════════
#  PATIENT ROUTES
# ══════════════════════════════════════════════════════
@app.route("/patient")
@login_required("patient")
def patient_home():
    pid = session["user"]["id"]
    conn = db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM patients WHERE patient_id=%s", (pid,))
    patient = cur.fetchone()
    cur.execute("SELECT COUNT(*) AS c FROM appointments WHERE patient_id=%s AND status='Scheduled'", (pid,)); scheduled = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM medical_records WHERE patient_id=%s", (pid,)); records = cur.fetchone()["c"]
    cur.execute("SELECT COUNT(*) AS c FROM billing WHERE patient_id=%s AND paid=FALSE", (pid,)); unpaid = cur.fetchone()["c"]
    cur.execute("""SELECT a.*, d.name AS doctor, d.specialization FROM appointments a
                   JOIN doctors d ON a.doctor_id=d.doctor_id
                   WHERE a.patient_id=%s ORDER BY a.appt_date DESC LIMIT 5""", (pid,))
    recent_appts = cur.fetchall()
    cur.close(); conn.close()
    return render_template("patient/home.html", patient=patient, scheduled=scheduled, records=records, unpaid=unpaid, recent_appts=recent_appts)

@app.route("/patient/appointments")
@login_required("patient")
def patient_appointments():
    pid = session["user"]["id"]
    conn = db(); cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT a.*, d.name AS doctor, d.specialization, d.phone AS doc_phone
                   FROM appointments a JOIN doctors d ON a.doctor_id=d.doctor_id
                   WHERE a.patient_id=%s ORDER BY a.appt_date DESC""", (pid,))
    appts = cur.fetchall()
    cur.close(); conn.close()
    return render_template("patient/appointments.html", appts=appts)

@app.route("/patient/records")
@login_required("patient")
def patient_records():
    pid = session["user"]["id"]
    conn = db(); cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT r.*, d.name AS doctor, d.specialization FROM medical_records r
                   JOIN doctors d ON r.doctor_id=d.doctor_id
                   WHERE r.patient_id=%s ORDER BY r.record_date DESC""", (pid,))
    records = cur.fetchall()
    cur.close(); conn.close()
    return render_template("patient/records.html", records=records)

@app.route("/patient/billing")
@login_required("patient")
def patient_billing():
    pid = session["user"]["id"]
    conn = db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM billing WHERE patient_id=%s ORDER BY bill_date DESC", (pid,))
    bills = cur.fetchall()
    cur.execute("SELECT SUM(amount) AS t FROM billing WHERE patient_id=%s AND paid=FALSE", (pid,))
    pending = cur.fetchone()["t"] or 0
    cur.close(); conn.close()
    return render_template("patient/billing.html", bills=bills, pending=pending)

@app.route("/patient/profile")
@login_required("patient")
def patient_profile():
    pid = session["user"]["id"]
    conn = db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM patients WHERE patient_id=%s", (pid,))
    patient = cur.fetchone()
    cur.close(); conn.close()
    return render_template("patient/profile.html", patient=patient)


# ── REGISTER (New Patient) ────────────────────────────
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name     = request.form["name"]
        age      = request.form["age"]
        gender   = request.form["gender"]
        phone    = request.form["phone"]
        email    = request.form["email"]
        password = request.form["password"]
        blood    = request.form.get("blood_group","")

        conn = db(); cur = conn.cursor(dictionary=True)
        # Check if email already exists
        cur.execute("SELECT * FROM patients WHERE email=%s", (email,))
        existing = cur.fetchone()
        if existing:
            cur.close(); conn.close()
            flash("Email already registered! Please login.", "error")
            return redirect(url_for("register"))

        cur2 = conn.cursor()
        cur2.execute("INSERT INTO patients (name,age,gender,phone,blood_group,email,password,admitted_on) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (name, age, gender, phone, blood, email, password, date.today()))
        conn.commit()
        patient_id = cur2.lastrowid
        cur2.close(); cur.close(); conn.close()

        # Auto login after register
        session["user"] = {"role":"patient","name":name,"id":patient_id}
        flash("Registration successful! Welcome to MediCare!", "success")
        return redirect(url_for("patient_home"))
    return render_template("register.html")

# ── PATIENT BOOK APPOINTMENT ──────────────────────────
@app.route("/patient/book", methods=["GET","POST"])
@login_required("patient")
def patient_book():
    pid = session["user"]["id"]
    conn = db(); cur = conn.cursor(dictionary=True)
    if request.method == "POST":
        cur2 = conn.cursor()
        cur2.execute("INSERT INTO appointments (patient_id,doctor_id,appt_date,appt_time,notes) VALUES (%s,%s,%s,%s,%s)",
            (pid, request.form["doctor_id"], request.form["appt_date"],
             request.form["appt_time"], request.form.get("notes","")))
        conn.commit()
        appt_id = cur2.lastrowid
        cur2.close(); cur.close(); conn.close()
        flash("Appointment booked successfully!", "success")
        return redirect(url_for("patient_appointments"))
    cur.execute("SELECT d.*, dept.dept_name FROM doctors d LEFT JOIN departments dept ON d.dept_id=dept.dept_id ORDER BY dept.dept_name")
    doctors = cur.fetchall()
    cur.close(); conn.close()
    return render_template("patient/book.html", doctors=doctors)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=port, debug=debug)
