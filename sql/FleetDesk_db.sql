-- Fleet Tables

CREATE TABLE fleet_driver (
    dri_id SERIAL PRIMARY KEY,
    dri_first_name VARCHAR(100) NOT NULL,
    dri_last_name VARCHAR(100) NOT NULL,
    dri_license_number VARCHAR(50) NOT NULL UNIQUE,
    dri_phone VARCHAR(20) NOT NULL,
    dri_email VARCHAR(254) NOT NULL,
    dri_address TEXT NOT NULL,
    dri_license_expiry DATE NOT NULL,
    dri_date_joined DATE NOT NULL,
    dri_status VARCHAR(20) NOT NULL CHECK (dri_status = 'ACTIVE' OR dri_status = 'INACTIVE' OR dri_status = 'SUSPENDED'),
    dri_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dri_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fleet_vehicle (
    veh_id SERIAL PRIMARY KEY,
    veh_plate_number VARCHAR(20) NOT NULL UNIQUE,
    veh_registration VARCHAR(100) NOT NULL,
    veh_or_expiry DATE,
    veh_cr_expiry DATE,
    veh_cpc_expiry DATE,
    veh_type VARCHAR(20) NOT NULL,
    veh_brand VARCHAR(100) NOT NULL,
    veh_model VARCHAR(100) NOT NULL,
    veh_year INT NOT NULL,
    veh_mileage INT NOT NULL,
    veh_last_maintenance DATE,
    veh_status VARCHAR(20) NOT NULL CHECK (veh_status = 'AVAILABLE' OR veh_status = 'IN USE' OR veh_status = 'UNDER REPAIR' OR veh_status = 'RETIRED'),
    veh_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    veh_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fleet_contract (
    cont_id SERIAL PRIMARY KEY,
    cont_start_date DATE NOT NULL,
    cont_end_date DATE,
    cont_daily_rate DECIMAL(10,2) NOT NULL,
    cont_security_deposit DECIMAL(10,2) NOT NULL,
    cont_deposit_status VARCHAR(20) NOT NULL CHECK (cont_deposit_status = 'Held' OR cont_deposit_status = 'Returned' OR cont_deposit_status = 'Partial' OR cont_deposit_status = 'Forfeited'),
    cont_deposit_return_date DATE,
    cont_deposit_return_amount DECIMAL(10,2),
    cont_forfeiture_reason TEXT,
    cont_status VARCHAR(30) DEFAULT 'ACTIVE' CHECK (cont_status = 'ACTIVE' OR cont_status = 'EXPIRED' OR cont_status = 'TERMINATED' OR cont_status = 'RENEWED'),
    cont_termination_reason TEXT,
    cont_veh_handover_condition TEXT,
    cont_veh_return_condition TEXT,
    cont_return_date DATE,
    cont_damage_charges DECIMAL(10,2),
    cont_special_terms TEXT,
    cont_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cont_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dri_id INT NOT NULL,
    veh_id INT NOT NULL,
    FOREIGN KEY (dri_id) REFERENCES "driver"(dri_id),
    FOREIGN KEY (veh_id) REFERENCES "vehicle"(veh_id)
);

CREATE TABLE fleet_payment (
    pay_id SERIAL PRIMARY KEY,
    pay_amount DECIMAL(10,2) NOT NULL,
    pay_due_date DATE NOT NULL,
    pay_paid_date DATE,
    pay_amount_paid DECIMAL(10,2) NOT NULL,
    pay_balance DECIMAL(10,2) NOT NULL,
    pay_status VARCHAR(20) NOT NULL CHECK (pay_status = 'PENDING' OR pay_status = 'PAID' OR pay_status = 'OVERDUE' OR pay_status = 'PARTIAL'),
    pay_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pay_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cont_id INT NOT NULL,
    FOREIGN KEY (cont_id) REFERENCES "contract"(cont_id)
);

CREATE TABLE fleet_repair (
    rep_id SERIAL PRIMARY KEY,
    rep_date_finished DATE,
    rep_shop_name VARCHAR(200) NOT NULL,
    rep_total_cost DECIMAL(10,2) NOT NULL,
    rep_details TEXT NOT NULL,
    rep_checklist TEXT NOT NULL,
    rep_status VARCHAR(20) NOT NULL CHECK (rep_status = 'PENDING' OR rep_status = 'IN PROGRESS' OR rep_status = 'COMPLETED'),
    rep_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rep_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dri_id INT,
    veh_id INT NOT NULL,
    FOREIGN KEY (dri_id) REFERENCES "driver"(dri_id),
    FOREIGN KEY (veh_id) REFERENCES "vehicle"(veh_id)
);

CREATE TABLE fleet_repairreceipt (
    rr_id SERIAL PRIMARY KEY,
    rr_file VARCHAR(100) NOT NULL,
    rr_file_name VARCHAR(255) NOT NULL,
    rr_uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rep_id INT NOT NULL,
    FOREIGN KEY (rep_id) REFERENCES "repair"(rep_id)
);

CREATE TABLE fleet_notification (
    notif_id SERIAL PRIMARY KEY,
    notif_type VARCHAR(30) NOT NULL,
    notif_title VARCHAR(200) NOT NULL,
    notif_message TEXT NOT NULL,
    notif_severity VARCHAR(10) NOT NULL CHECK (notif_severity = 'LOW' OR notif_severity = 'MEDIUM' OR notif_severity = 'HIGH'),
    notif_is_read BOOLEAN NOT NULL DEFAULT FALSE,
    notif_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cont_id INT,
    dri_id INT,
    pay_id INT,
    veh_id INT,
    FOREIGN KEY (cont_id) REFERENCES "contract"(cont_id),
    FOREIGN KEY (dri_id) REFERENCES "driver"(dri_id),
    FOREIGN KEY (pay_id) REFERENCES "payment"(pay_id),
    FOREIGN KEY (veh_id) REFERENCES "vehicle"(veh_id)
);
