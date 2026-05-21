USE hospital_db;

-- Add login fields to doctors
ALTER TABLE doctors 
  ADD COLUMN IF NOT EXISTS license_number VARCHAR(50) UNIQUE,
  ADD COLUMN IF NOT EXISTS password VARCHAR(255) DEFAULT 'doctor123';

-- Add login fields to patients  
ALTER TABLE patients
  ADD COLUMN IF NOT EXISTS email VARCHAR(100) UNIQUE,
  ADD COLUMN IF NOT EXISTS password VARCHAR(255) DEFAULT 'patient123';

-- Update sample doctors with license numbers
UPDATE doctors SET license_number='LIC-CARD-001', password='doctor123' WHERE doctor_id=1;
UPDATE doctors SET license_number='LIC-NEUR-002', password='doctor123' WHERE doctor_id=2;
UPDATE doctors SET license_number='LIC-ORTH-003', password='doctor123' WHERE doctor_id=3;
UPDATE doctors SET license_number='LIC-PEDI-004', password='doctor123' WHERE doctor_id=4;
UPDATE doctors SET license_number='LIC-GENM-005', password='doctor123' WHERE doctor_id=5;
UPDATE doctors SET license_number='LIC-CARD-006', password='doctor123' WHERE doctor_id=6;

-- Update sample patients with emails
UPDATE patients SET email='arjun@email.com',   password='patient123' WHERE patient_id=1;
UPDATE patients SET email='meera@email.com',   password='patient123' WHERE patient_id=2;
UPDATE patients SET email='suresh@email.com',  password='patient123' WHERE patient_id=3;
UPDATE patients SET email='lakshmi@email.com', password='patient123' WHERE patient_id=4;
UPDATE patients SET email='ravi@email.com',    password='patient123' WHERE patient_id=5;
UPDATE patients SET email='deepa@email.com',   password='patient123' WHERE patient_id=6;
