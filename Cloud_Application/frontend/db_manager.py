import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

class DBManager:
    def __init__(self, host="localhost", user="root", database="SmartHealthIoT", active_sensors=None):
        self.config = {
            'host': host,
            'user': user,
            'password': "1",
            'database': database
        }
        self.connection = None
        self.min_timeout = 10  # timeout per sensore in assenza di dati
        self.sampling_rates = {}  # memorizza i sampling rate per sensore
        # lista dei sensori attivi (se None, prendi tutti)
        self.active_sensors = active_sensors or [1] 

    def connect(self):
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
                self.connection.autocommit = True
            return True
        except Error as e:
            print(f" Connessione fallita: {e}")
            return False

    def update_sampling_rate(self, sensor_id, rate_seconds):
        """Aggiorna il sampling rate per un sensore specifico"""
        if sensor_id in self.active_sensors:
            self.sampling_rates[sensor_id] = rate_seconds
            print(f" Sensor {sensor_id} sampling rate updated to {rate_seconds}s")

    def fetch_latest_measurements(self):
        """
        Recupera l'ultimissimo record salvato per OGNI sensore attivo.
        Include la colonna 'status' e verifica il timeout del sensore.
        Il timeout è dinamico: max(10 secondi, 2 * sampling_rate)
        """
        if not self.connect():
            return []
        try:
            cursor = self.connection.cursor(buffered=True, dictionary=True)
            
            # filtra solo i sensori attivi
            placeholders = ','.join(['%s'] * len(self.active_sensors))
            query = f"""
                SELECT m1.sensor_id, m1.heart_rate, m1.body_temperature, m1.spo2, m1.risk_score, m1.timestamp, m1.status
                FROM Health_Measurements m1
                INNER JOIN (
                    SELECT sensor_id, MAX(timestamp) as max_ts
                    FROM Health_Measurements
                    WHERE sensor_id IN ({placeholders})
                    GROUP BY sensor_id
                ) m2 ON m1.sensor_id = m2.sensor_id AND m1.timestamp = m2.max_ts
            """
            
            cursor.execute(query, tuple(self.active_sensors))
            results = cursor.fetchall()
            
            # verifico timeout e aggiorno lo status dei sensori 
            for record in results:
                sensor_id = record.get("sensor_id")
                last_timestamp = record.get("timestamp")
                
                if last_timestamp:
                  
                    sampling_rate = self.sampling_rates.get(sensor_id, 5)

                    # timeout dinamico: max(min_timeout, 2 * sampling_rate)
                    timeout = max(self.min_timeout, sampling_rate * 2)
                    time_diff = datetime.now() - last_timestamp
                    
                    # se il tempo trascorso dall'ultimo dato supera il timeout, segna il sensore come MISSING
                    if time_diff > timedelta(seconds=timeout):
                        record["status"] = "SENSOR_MISSING"
                        print(f" Sensor {sensor_id} MISSING: no data for {time_diff.total_seconds():.0f}s (timeout={timeout}s, SR={sampling_rate}s)")
            
            cursor.close()
            return results
        except Error as e:
            print(f" Impossibile recuperare gli ultimi dati: {e}")
            return []

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()