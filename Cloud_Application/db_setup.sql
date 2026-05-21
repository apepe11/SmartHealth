CREATE DATABASE IF NOT EXISTS SmartHealthIoT;
USE SmartHealthIoT;

CREATE TABLE IF NOT EXISTS Health_Measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,                  -- ID del sensore associato nel file JSON
    heart_rate INT NOT NULL,                 -- Frequenza cardiaca (bpm)
    body_temperature INT NOT NULL,           -- Temperatura corporea (°C)
    spo2 INT NOT NULL,                       -- Saturazione dell'ossigeno (%)
    risk_score INT NOT NULL,                 -- Modificato in INT (Classe 0, 1, 2 dal TinyML)
    status VARCHAR(20) NOT NULL DEFAULT 'ONLINE', -- NUOVO: Traccia 'ONLINE' o 'NODE_FAILURE' [SOLO PROJECT]
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Indice per velocizzare le query di Grafana e della UI sui dati più recenti
    INDEX idx_sensor_timestamp (sensor_id, timestamp DESC)
);

-- Script di migrazione nel caso la tabella esistesse già senza la colonna status
ALTER TABLE Health_Measurements 
    ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'ONLINE' AFTER risk_score;

-- Nel caso in cui risk_score fosse stato creato originariamente come FLOAT, lo convertiamo in INT
ALTER TABLE Health_Measurements 
    MODIFY COLUMN risk_score INT NOT NULL;