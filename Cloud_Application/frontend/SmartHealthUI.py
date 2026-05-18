# SmartHealthUI.py
import tkinter as tk
from tkinter import ttk
from coap_service import DataService
from view_components import SensorCard

class SmartHealthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Health Monitor - Dashboard")
        self.root.geometry("600x400")
        
        # Inizializziamo il servizio dati che legge da MySQL
        self.data_service = DataService()
        
        # Titolo Principale
        title_lbl = ttk.Label(root, text="🏥 Sistema Cloud di Monitoraggio Pazienti", font=("Arial", 16, "bold"))
        title_lbl.pack(pady=15)
        
        # Contenitore delle Card dei Sensori
        self.cards_frame = ttk.Frame(root)
        self.cards_frame.pack(padx=20, pady=10, fill="x")
        
        # Creiamo un dizionario per mappare le card in base al nome del sensore
        self.sensor_cards = {
            "Sensore_1": SensorCard(self.cards_frame, "Sensore 1 (Letto A)"),
            "Sensore_2": SensorCard(self.cards_frame, "Sensore 2 (Letto B)")
        }
        
        # Grigliamo le card affiancate
        self.sensor_cards["Sensore_1"].grid(row=0, column=0, padx=15, sticky="nsew")
        self.sensor_cards["Sensore_2"].grid(row=0, column=1, padx=15, sticky="nsew")
        
        self.cards_frame.columnconfigure(0, weight=1)
        self.cards_frame.columnconfigure(1, weight=1)
        
        # Label informativa di aggiornamento
        self.status_bar = ttk.Label(root, text="Aggiornamento automatico attivo (ogni 2s)...", font=("Arial", 9, "italic"))
        self.status_bar.pack(side="bottom", pady=10)
        
        # Avvia il ciclo infinito di Polling sul DB
        self.refresh_data()

    def refresh_data(self):
        """Interroga il DB ed esegue il refresh della UI"""
        # Recupera gli ultimi record scritti dal backend
        latest_records = self.data_service.get_latest_measurements()
        
        sensor_map = {
            1: "Sensore_1",
            2: "Sensore_2"
        }

        for record in latest_records:
            sensor_id = record.get("sensor_id")
            sensor_key = sensor_map.get(sensor_id)
            if sensor_key and sensor_key in self.sensor_cards:
                hr = record.get("heart_rate", 0)
                body_temp = record.get("body_temperature", 0)
                spo2 = record.get("spo2", 0)
                risk = record.get("risk_score", 0.0)
                
                # Aggiorna la card specifica
                self.sensor_cards[sensor_key].update_data(hr, body_temp, spo2, risk)
                
        # Pianifica la prossima esecuzione tra 2000 millisecondi (2 secondi)
        self.root.after(2000, self.refresh_data)

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartHealthApp(root)
    root.mainloop()