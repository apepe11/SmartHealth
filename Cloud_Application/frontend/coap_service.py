# coap_service.py
import mysql.connector
from configuration_manager import DB_CONFIG

class DataService:
    def __init__(self):
        self.config = DB_CONFIG

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    def get_latest_measurements(self):
        """Recupera l'ultimissimo dato salvato per ciascun sensore"""
        connection = self._get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Questa query prende l'ultimo record inserito per ogni sensore
        query = """
            SELECT m1.sensor_id, m1.heart_rate, m1.body_temperature, m1.spo2, m1.risk_score, m1.timestamp
            FROM Health_Measurements m1
            INNER JOIN (
                SELECT sensor_id, MAX(timestamp) as max_ts
                FROM Health_Measurements
                GROUP BY sensor_id
            ) m2 ON m1.sensor_id = m2.sensor_id AND m1.timestamp = m2.max_ts
        """
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Errore lettura DB: {e}")
            return []
        finally:
            cursor.close()
            connection.close()

    def get_history(self, sensor_id, limit=10):
        """Recupera la cronologia degli ultimi N dati di un sensore specifico"""
        connection = self._get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT heart_rate, body_temperature, spo2, risk_score, timestamp 
            FROM Health_Measurements 
            WHERE sensor_id = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        try:
            cursor.execute(query, (sensor_id, limit))
            return cursor.fetchall()
        except Exception as e:
            print(f"Errore lettura storico: {e}")
            return []
        finally:
            cursor.close()
            connection.close()