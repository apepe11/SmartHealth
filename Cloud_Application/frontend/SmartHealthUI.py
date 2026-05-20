# SmartHealthUI.py
import tkinter as tk
from tkinter import ttk
from coap_service import DataService, CoAPNetworkService
from view_components import SensorCard
from configuration_manager import SENSORS_CONFIG

class SmartHealthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Health Monitor - Dashboard")
        self.root.geometry("650x450")
        
        # Inizializziamo i servizi (Database + Rete CoAP)
        self.data_service = DataService()
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
                "Monitoraggio Regionale Paziente",
                sr_callback=self.handle_change_sampling_rate,
                t_callback=self.handle_change_threshold
            )
        }
        
        self.sensor_cards["Sensore_1"].pack(padx=15, pady=10, fill="both", expand=True)
        self.cards_frame.columnconfigure(0, weight=1)
        
        self.status_bar = ttk.Label(root, text="Aggiornamento automatico attivo (DB Polling 2s)...", font=("Arial", 9, "italic"))
        self.status_bar.pack(side="bottom", pady=10)
        
        self.refresh_data()

    def handle_change_sampling_rate(self, new_rate):
        """Callback azionata quando l'utente preme 'Invia SR' nella scheda"""
        sensor_ip = SENSORS_CONFIG["Sensore_1"]["sensor_ip"]
        self.coap_net_service.send_new_sampling_rate(sensor_ip, new_rate)

    def handle_change_threshold(self, new_threshold):
        """Callback azionata quando l'utente preme 'Invia Soglia' nella scheda"""
        actuator_ip = SENSORS_CONFIG["Sensore_1"]["actuator_ip"]
        self.coap_net_service.send_new_threshold(actuator_ip, new_threshold)

    def refresh_data(self):
        """Interroga il DB ed esegue il riallineamento dei widget grafici"""
        latest_records = self.data_service.get_latest_measurements()
        sensor_map = {1: "Sensore_1"}

        for record in latest_records:
            sensor_id = record.get("sensor_id")
            sensor_key = sensor_map.get(sensor_id)
            if sensor_key and sensor_key in self.sensor_cards:
                hr = record.get("heart_rate", 0)
                body_temp = record.get("body_temperature", 0)
                spo2 = record.get("spo2", 0)
                risk = record.get("risk_score", 0)
                
                self.sensor_cards[sensor_key].update_data(hr, body_temp, spo2, risk)
                
        self.root.after(2000, self.refresh_data)

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHealthApp(root)
    root.mainloop()