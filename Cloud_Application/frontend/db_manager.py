import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
try:
    from .configuration_manager import DB_CONFIG
except Exception:
    from configuration_manager import DB_CONFIG

class DBManager:
    def __init__(self, host=None, user=None, database=None, active_sensors=None):
        self.config = {
            'host': host or DB_CONFIG["host"],
            'user': user or DB_CONFIG["user"],
            'password': DB_CONFIG["password"],
            'database': database or DB_CONFIG["database"]
        }
        self.connection = None
        self.min_timeout = 10  
        self.sampling_rates = {}  
        self.active_sensors = active_sensors or [1]
        self.last_missing_recorded = {}  # per evitare di scrivere troppi record MISSING

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

    def insert_missing_record(self, sensor_id, timeout_seconds, sampling_rate):
        now = datetime.now()
        
        # evito di scrivere record MISSING troppo frequentemente per lo stesso sensore
        last_missing = self.last_missing_recorded.get(sensor_id)
        if last_missing and (now - last_missing).total_seconds() < 30:
            return False
        
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO Health_Measurements (sensor_id, heart_rate, body_temperature, spo2, risk_score, status, timestamp) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            # valori fittizi: -1 per risk_score indica che è un evento di missing
            cursor.execute(query, (
                sensor_id, 
                0,      # heart_rate = 0 (n/a)
                0,      # body_temperature = 0 (n/a)
                0,      # spo2 = 0 (n/a)
                -1,     # risk_score = -1 (special value per MISSING)
                'SENSOR_MISSING',
                now
            ))
            cursor.close()
            self.last_missing_recorded[sensor_id] = now
            print(f"   📝 Inserito record SENSOR_MISSING per sensore {sensor_id} nel DB")
            return True
        except Error as e:
            print(f"   ❌ Errore inserimento record MISSING: {e}")
            return False

    def fetch_latest_measurements(self):
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
                        # se l'ultimo record non è già MISSING, nuovo record
                        if record.get("status") != "SENSOR_MISSING":
                            self.insert_missing_record(sensor_id, timeout, sampling_rate)
                        record["status"] = "SENSOR_MISSING"
                        print(f" Sensor {sensor_id} MISSING: no data for {time_diff.total_seconds():.0f}s (timeout={timeout}s, SR={sampling_rate}s)")
                    else:
                        # Il sensore è tornato ONLINE dopo un missing
                        if record.get("status") == "SENSOR_MISSING":
                            print(f" Sensor {sensor_id} tornato ONLINE dopo {(datetime.now() - last_timestamp).total_seconds():.0f}s")
            
            
            for sensor_id in self.active_sensors:
                sensor_in_results = any(r.get("sensor_id") == sensor_id for r in results)
                if not sensor_in_results:
                    self.insert_missing_record(sensor_id, self.min_timeout, 5)
                    # creo un record fittizio da restituire
                    results.append({
                        "sensor_id": sensor_id,
                        "heart_rate": 0,
                        "body_temperature": 0,
                        "spo2": 0,
                        "risk_score": -1,
                        "status": "SENSOR_MISSING",
                        "timestamp": datetime.now()
                    })
            
            cursor.close()
            return results
        except Error as e:
            print(f" Impossibile recuperare gli ultimi dati: {e}")
            return []

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()