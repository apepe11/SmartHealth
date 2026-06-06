DB_CONFIG = { # configurazioni per connessione al DB
    "host": "localhost",
    # Use a dedicated DB user for the application instead of root
    "user": "smarthealth",
    "password": "1",
    "database": "SmartHealthIoT"
}


SENSORS_CONFIG = {
    "Sensori": {
        "id": 1,
        "sensor_ip": "fd00::f6ce:36b9:a760:ecea",  # IP del dongle che funge da sensore 
        "actuator_ip": "fd00::f6ce:36a6:c68f:cb04"    # IP dell'attuatore fisico 
    }
}
