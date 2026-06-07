import tkinter as tk
from tkinter import ttk
import json

try:
    from .db_manager import DBManager
    from .coap_service import CoAPNetworkService
    from .view_components import SensorCard
    from .configuration_manager import SENSORS_CONFIG
except Exception:
    from db_manager import DBManager
    from coap_service import CoAPNetworkService
    from view_components import SensorCard
    from configuration_manager import SENSORS_CONFIG


class SmartHealthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Health Monitor - Dashboard")
        self.root.geometry("850x680") 
        
        self.data_service = DBManager()
        self.coap_net_service = CoAPNetworkService()
        
        title_lbl = ttk.Label(root, text="🏥 Smart Health Monitor - Control Panel", font=("Arial", 16, "bold"))
        title_lbl.pack(pady=15)
        
        self.cards_frame = ttk.Frame(root)
        self.cards_frame.pack(padx=20, pady=10, fill="x")
        self.cards_frame.columnconfigure(0, weight=1)
        
        self.sensor_cards = {
            "Sensori": SensorCard(
                self.cards_frame, 
                "Patient Vital Sign Monitor",
                sr_callback=self.handle_change_sampling_rate,
            )
        }
        self.sensor_cards["Sensori"].pack(padx=15, pady=10, fill="both", expand=True)
        

        actuator_section = ttk.LabelFrame(root, text="🚨 Hardware Actuator Status (Dongle LED)")
        actuator_section.pack(padx=35, pady=15, fill="x")
        

        state_frame = ttk.Frame(actuator_section)
        state_frame.pack(padx=10, pady=15, fill="x")
        
        self.lbl_current_threshold = ttk.Label(state_frame, text="Current Actuator Threshold: N/A", font=("Arial", 11, "bold"))
        self.lbl_current_threshold.pack(side="left", padx=10)
        
        self.status_bar = ttk.Label(root, text="Automatic update active (DB Polling 1s)...", font=("Arial", 9, "italic"))
        self.status_bar.pack(side="bottom", pady=10)
        
        self.refresh_data()
    # callback per cambio sampling rate da GUI
    def handle_change_sampling_rate(self, new_rate):
        sensor_ip = SENSORS_CONFIG["Sensori"]["sensor_ip"]
        sensor_id = SENSORS_CONFIG["Sensori"]["id"]
        
        self.data_service.update_sampling_rate(sensor_id, new_rate)
        self.coap_net_service.send_new_sampling_rate(sensor_ip, new_rate)
    # funzione per aggiornare i dati visualizzati nelle card, chiamata periodicamente
    def refresh_data(self):
        latest_records = self.data_service.fetch_latest_measurements() 
        sensor_map = {1: "Sensori"}

        if not latest_records:
            for sensor_key in self.sensor_cards:
                self.sensor_cards[sensor_key].update_data(None, None, None, None, "SENSOR_MISSING")
        else:
            for record in latest_records:
                if isinstance(record, dict):
                    sensor_id = record.get("sensor_id")
                    hr = record.get("heart_rate", 0)
                    body_temp = record.get("body_temperature", 0)
                    spo2 = record.get("spo2", 0)
                    risk = record.get("risk_score", 0)
                    status = record.get("status", "ONLINE")
                else:
                    sensor_id = record[0]
                    hr = record[1]
                    body_temp = record[2]
                    spo2 = record[3]
                    risk = record[4]
                    status = record[6] if len(record) > 6 else "ONLINE"

                sensor_key = sensor_map.get(sensor_id)
                if sensor_key and sensor_key in self.sensor_cards:
                    self.sensor_cards[sensor_key].update_data(hr, body_temp, spo2, risk, status)
                    

                    if risk >= 2:
                        self.lbl_current_threshold.config(text="Actuator State: Threshold 2 [AUTOMATIC FORCED - RED LED]", foreground="red")
                    elif risk == 1:
                        self.lbl_current_threshold.config(text="Actuator State: Threshold 1 [AUTOMATIC FORCED - BLUE LED]", foreground="blue")
                    else:
                        self.lbl_current_threshold.config(text="Actuator State: Threshold 0 [AUTOMATIC FORCED - GREEN LED]", foreground="green")
            
            found_sensors = set()
            for record in latest_records:
                if isinstance(record, dict):
                    found_sensors.add(record.get("sensor_id"))
                else:
                    found_sensors.add(record[0])
            
            for sensor_id, sensor_key in sensor_map.items():
                if sensor_id not in found_sensors:
                    self.sensor_cards[sensor_key].update_data(None, None, None, None, "SENSOR_MISSING")

        self.root.after(1000, self.refresh_data)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHealthApp(root)
    root.mainloop()