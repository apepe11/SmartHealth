# configuration_manager.py

DB_CONFIG = { # configurazioni per connessione al DB
    "host": "localhost",
    "user": "root",
    "password": "1",
    "database": "SmartHealthIoT"
}


SENSORS_CONFIG = {
    "Sensori": {
        "id": 1,
        "sensor_ip": "fd00::f6ce:36b9:a760:ecea",  # Ip del dongle che funge da sensore 
        "actuator_ip": "fd00::202:2:2:2"          # attuatore in cooja
    }
}
