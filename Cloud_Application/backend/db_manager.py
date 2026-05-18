import mysql.connector
from mysql.connector import Error

class DBManager:
    def __init__(self, host="localhost", user="root", database="SmartHealthIoT"):
        self.config = {
            'host': host,
            'user': user,
            'password': "1",
            'database': database
        }
        self.connection = None

    def connect(self):
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.config)
            return True
        except Error as e:
            print(f"[Errore Database] Connessione fallita: {e}")
            return False

    def fetch_latest_measurements(self, limit=20):
        if not self.connect():
            return []
        try:
            cursor = self.connection.cursor(buffered=True)
            query = "SELECT sensor_id, heart_rate, body_temperature, spo2, risk_score, timestamp FROM Health_Measurements ORDER BY timestamp DESC LIMIT %s"
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"[Errore Database] Impossibile recuperare dati: {e}")
            return []

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()