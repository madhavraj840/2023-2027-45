-- Sprint 3 (Backend + API + DB) — Database Development (10/8/26 – 22/8/26)
CREATE DATABASE IF NOT EXISTS hmpi;
USE hmpi;

CREATE TABLE users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(100) NOT NULL,
  email         VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE datasets (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT,
  file_name   VARCHAR(255) NOT NULL,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- One row per water sample; metal concentrations in mg/L
CREATE TABLE samples (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  dataset_id  INT,
  location    VARCHAR(150),
  latitude    DECIMAL(9,6),
  longitude   DECIMAL(9,6),
  sample_date DATE,
  as_mgl DOUBLE, cd_mgl DOUBLE, cr_mgl DOUBLE, cu_mgl DOUBLE, fe_mgl DOUBLE,
  pb_mgl DOUBLE, mn_mgl DOUBLE, ni_mgl DOUBLE, zn_mgl DOUBLE, hg_mgl DOUBLE,
  FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
);

CREATE TABLE results (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  sample_id   INT NOT NULL,
  hpi         DOUBLE,
  npi         DOUBLE,
  hpi_class   VARCHAR(50),
  predicted   BOOLEAN DEFAULT FALSE,  -- TRUE when produced by the ML model
  computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE
);
