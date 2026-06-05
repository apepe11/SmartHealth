CREATE DATABASE IF NOT EXISTS SmartHealthIoT;
USE SmartHealthIoT;

CREATE TABLE IF NOT EXISTS Health_Measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,                  -- ID del sensore associato nel file JSON
    heart_rate INT NOT NULL,                 -- Frequenza cardiaca (bpm)
    body_temperature INT NOT NULL,           -- Temperatura corporea (°C)
    spo2 INT NOT NULL,                       -- Saturazione dell'ossigeno (%)
    risk_score INT NOT NULL,                 -- classe di rischio (0-3)
    status VARCHAR(20) NOT NULL DEFAULT 'ONLINE', -- stato del sensore (ONLINE/OFFLINE)
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- indicie per velocizzare le query di Grafana e della UI sui dati più recenti
    INDEX idx_sensor_timestamp (sensor_id, timestamp DESC)
);

CREATE USER IF NOT EXISTS 'smarthealth'@'localhost' IDENTIFIED BY '1';
GRANT ALL PRIVILEGES ON SmartHealthIoT.* TO 'smarthealth'@'localhost';
FLUSH PRIVILEGES;
