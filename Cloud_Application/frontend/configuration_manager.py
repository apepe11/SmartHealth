# configuration_manager.py

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1",
    "database": "SmartHealthIoT"
}


SENSORS_CONFIG = {
    "Sensore_1": {
        "id": 1,
        "sensor_ip": "fd00::f6ce:36b9:a760:ecea",  # IP reale del Dongle Fisico (Corretto ✓)
        "actuator_ip": "fd00::202:2:2:2"          # MODIFICATO: IP globale dell'attuatore in Cooja
    }
}
