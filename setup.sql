-- ============================================
--   HOSPITAL MANAGEMENT SYSTEM - MySQL Schema
-- ============================================

CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;

-- ─── DEPARTMENTS ───────────────────────────
CREATE TABLE IF NOT EXISTS departments (
    dept_id     INT AUTO_INCREMENT PRIMARY KEY,
    dept_name   VARCHAR(100) NOT NULL UNIQUE,
    location    VARCHAR(100),
    head_doctor VARCHAR(100)
);

-- ─── DOCTORS ───────────────────────────────
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id       INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    specialization  VARCHAR(100),
    phone           VARCHAR(15),
    email           VARCHAR(100) UNIQUE,
    dept_id         INT,
    available_days  VARCHAR(100) DEFAULT 'Mon-Fri',
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE SET NULL
);

-- ─── PATIENTS ──────────────────────────────
CREATE TABLE IF NOT EXISTS patients (
    patient_id  INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    age         INT CHECK (age > 0 AND age < 150),
    gender      ENUM('Male', 'Female', 'Other'),
    phone       VARCHAR(15),
    address     TEXT,
    blood_group VARCHAR(5),
    admitted_on DATE DEFAULT (CURRENT_DATE)
);

-- ─── APPOINTMENTS ──────────────────────────
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id  INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT NOT NULL,
    doctor_id       INT NOT NULL,
    appt_date       DATE NOT NULL,
    appt_time       TIME NOT NULL,
    status          ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    notes           TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)   ON DELETE CASCADE
);

-- ─── MEDICAL RECORDS ───────────────────────
CREATE TABLE IF NOT EXISTS medical_records (
    record_id   INT AUTO_INCREMENT PRIMARY KEY,
    patient_id  INT NOT NULL,
    doctor_id   INT NOT NULL,
    diagnosis   TEXT,
    treatment   TEXT,
    prescription TEXT,
    record_date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)   ON DELETE CASCADE
);

-- ─── BILLING ───────────────────────────────
CREATE TABLE IF NOT EXISTS billing (
    bill_id         INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT NOT NULL,
    appointment_id  INT,
    amount          DECIMAL(10,2) NOT NULL,
    paid            BOOLEAN DEFAULT FALSE,
    bill_date       DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (patient_id)     REFERENCES patients(patient_id)         ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE SET NULL
);

-- ─── SAMPLE DATA ───────────────────────────

INSERT INTO departments (dept_name, location, head_doctor) VALUES
('Cardiology',    'Block A, Floor 1', 'Dr. Ramesh Iyer'),
('Neurology',     'Block B, Floor 2', 'Dr. Priya Sharma'),
('Orthopedics',   'Block C, Floor 1', 'Dr. Anil Mehta'),
('Pediatrics',    'Block A, Floor 3', 'Dr. Sunita Rao'),
('General Medicine', 'Block D, Floor 1', 'Dr. Vikram Nair');

INSERT INTO doctors (name, specialization, phone, email, dept_id, available_days) VALUES
('Dr. Ramesh Iyer',   'Cardiologist',      '9876543210', 'ramesh@hospital.com',  1, 'Mon-Sat'),
('Dr. Priya Sharma',  'Neurologist',       '9876543211', 'priya@hospital.com',   2, 'Mon-Fri'),
('Dr. Anil Mehta',    'Orthopedic Surgeon','9876543212', 'anil@hospital.com',    3, 'Tue-Sat'),
('Dr. Sunita Rao',    'Pediatrician',      '9876543213', 'sunita@hospital.com',  4, 'Mon-Fri'),
('Dr. Vikram Nair',   'General Physician', '9876543214', 'vikram@hospital.com',  5, 'Mon-Sat'),
('Dr. Kavitha Menon', 'Cardiologist',      '9876543215', 'kavitha@hospital.com', 1, 'Mon-Wed');

INSERT INTO patients (name, age, gender, phone, address, blood_group, admitted_on) VALUES
('Arjun Kumar',    34, 'Male',   '9123456780', 'Koramangala, Bengaluru', 'O+',  '2024-01-10'),
('Meera Pillai',   28, 'Female', '9123456781', 'Indiranagar, Bengaluru', 'A+',  '2024-02-15'),
('Suresh Reddy',   55, 'Male',   '9123456782', 'Whitefield, Bengaluru',  'B-',  '2024-03-20'),
('Lakshmi Devi',   45, 'Female', '9123456783', 'Jayanagar, Bengaluru',   'AB+', '2024-03-25'),
('Ravi Shankar',   67, 'Male',   '9123456784', 'HSR Layout, Bengaluru',  'O-',  '2024-04-01'),
('Deepa Nair',     32, 'Female', '9123456785', 'BTM Layout, Bengaluru',  'A-',  '2024-04-10');

INSERT INTO appointments (patient_id, doctor_id, appt_date, appt_time, status, notes) VALUES
(1, 1, '2024-05-01', '10:00:00', 'Completed',  'Routine heart checkup'),
(2, 2, '2024-05-02', '11:00:00', 'Completed',  'Migraine follow-up'),
(3, 3, '2024-05-03', '09:30:00', 'Completed',  'Knee pain evaluation'),
(4, 5, '2024-05-05', '14:00:00', 'Scheduled',  'Fever and fatigue'),
(5, 1, '2024-05-06', '10:30:00', 'Scheduled',  'ECG and stress test'),
(6, 4, '2024-05-07', '12:00:00', 'Cancelled',  'Child immunization');

INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment, prescription, record_date) VALUES
(1, 1, 'Hypertension Stage 1', 'Lifestyle changes, medication', 'Amlodipine 5mg daily', '2024-05-01'),
(2, 2, 'Chronic Migraine',     'Preventive therapy',           'Topiramate 25mg',      '2024-05-02'),
(3, 3, 'Osteoarthritis',       'Physiotherapy + medication',   'Diclofenac gel, Calcium supplements', '2024-05-03');

INSERT INTO billing (patient_id, appointment_id, amount, paid, bill_date) VALUES
(1, 1, 1500.00, TRUE,  '2024-05-01'),
(2, 2, 1200.00, TRUE,  '2024-05-02'),
(3, 3, 2500.00, FALSE, '2024-05-03'),
(4, 4,  800.00, FALSE, '2024-05-05');
