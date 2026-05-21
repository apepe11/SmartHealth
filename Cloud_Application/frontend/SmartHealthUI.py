# SmartHealthUI.py
import tkinter as tk
from tkinter import ttk
from db_manager import DBManager 
from coap_service import CoAPNetworkService
from view_components import SensorCard
from configuration_manager import SENSORS_CONFIG

class SmartHealthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Health Monitor - Dashboard")
        self.root.geometry("650x450")
        
        self.data_service = DBManager()
        self.coap_net_service = CoAPNetworkService()
        
        # Titolo Principale
        title_lbl = ttk.Label(root, text="🏥 Smart Health Monitor - Control Panel", font=("Arial", 16, "bold"))
        title_lbl.pack(pady=15)
        
        self.cards_frame = ttk.Frame(root)
        self.cards_frame.pack(padx=20, pady=10, fill="x")
        
        # Passiamo le funzioni di callback alla scheda per collegare i bottoni della UI a CoAP
        self.sensor_cards = {
            "Sensore_1": SensorCard(
                self.cards_frame, 
                "Patient Monitor",
                sr_callback=self.handle_change_sampling_rate,
            )
        }
        
        self.sensor_cards["Sensore_1"].pack(padx=15, pady=10, fill="both", expand=True)
        self.cards_frame.columnconfigure(0, weight=1)
        
        self.status_bar = ttk.Label(root, text="Automatic update active (DB Polling 1s)...", font=("Arial", 9, "italic"))
        self.status_bar.pack(side="bottom", pady=10)
        
        self.refresh_data()

    def handle_change_sampling_rate(self, new_rate):
        """Callback azionata quando l'utente preme 'Invia SR' nella scheda"""
        sensor_ip = SENSORS_CONFIG["Sensore_1"]["sensor_ip"]
        sensor_id = SENSORS_CONFIG["Sensore_1"]["id"]
        
        # Aggiorna il sampling rate nel DBManager per il timeout dinamico
        self.data_service.update_sampling_rate(sensor_id, new_rate)
        
        # Invia il comando CoAP al sensore
        self.coap_net_service.send_new_sampling_rate(sensor_ip, new_rate)

    def refresh_data(self):
        """Interroga il DB ed esegue il riallineamento dei widget grafici"""
        latest_records = self.data_service.fetch_latest_measurements() 
        sensor_map = {1: "Sensore_1"}

        if not latest_records:
            # No records found - show sensor missing for all sensors
            for sensor_key in self.sensor_cards:
                self.sensor_cards[sensor_key].update_data(None, None, None, None, "SENSOR_MISSING")
        else:
            for record in latest_records:
                # Controllo robusto: se record è un dizionario usa .get(), altrimenti estrai per indice (tupla)
                if isinstance(record, dict):
                    sensor_id = record.get("sensor_id")
                    hr = record.get("heart_rate", 0)
                    body_temp = record.get("body_temperature", 0)
                    spo2 = record.get("spo2", 0)
                    risk = record.get("risk_score", 0)
                    status = record.get("status", "ONLINE")
                else:
                    # Se è arrivata una tupla, estraiamo i dati in base all'ordine della query SQL
                    sensor_id = record[0]
                    hr = record[1]
                    body_temp = record[2]
                    spo2 = record[3]
                    risk = record[4]
                    status = record[6] if len(record) > 6 else "ONLINE"

                sensor_key = sensor_map.get(sensor_id)
                if sensor_key and sensor_key in self.sensor_cards:
                    # Fornisce i parametri inclusa la connettività di rete alla view grafica
                    self.sensor_cards[sensor_key].update_data(hr, body_temp, spo2, risk, status)
            
            # Check for sensors that are not in the results (missing completely)
            found_sensors = set()
            for record in latest_records:
                if isinstance(record, dict):
                    found_sensors.add(record.get("sensor_id"))
                else:
                    found_sensors.add(record[0])
            
            for sensor_id, sensor_key in sensor_map.items():
                if sensor_id not in found_sensors:
                    self.sensor_cards[sensor_key].update_data(None, None, None, None, "SENSOR_MISSING")

        # Riesegue il polling ogni secondo per rendere la UI reattiva in tempo reale
        self.root.after(1000, self.refresh_data)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHealthApp(root)
    root.mainloop()