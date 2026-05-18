CREATE DATABASE IF NOT EXISTS SmartHealthIoT;
USE SmartHealthIoT;


CREATE TABLE IF NOT EXISTS Health_Measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,                  -- ID del sensore associato nel file JSON
    heart_rate INT NOT NULL,                 -- Frequenza cardiaca (bpm)
    body_temperature INT NOT NULL,           -- Temperatura corporea (°C)
    spo2 INT NOT NULL,                       -- Saturazione dell'ossigeno (%)
    risk_score FLOAT NOT NULL,               -- Valore di rischio (0.0 a 1.0) calcolato dal ML sul nodo
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Indice per velocizzare le query di Grafana e della CLI sui dati più recenti
    INDEX idx_sensor_timestamp (sensor_id, timestamp DESC)
);

-- Se la tabella esiste già, assicuriamoci che la colonna body_temperature sia presente
ALTER TABLE Health_Measurements
    ADD COLUMN IF NOT EXISTS body_temperature INT NOT NULL DEFAULT 0 AFTER heart_rate;