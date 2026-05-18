# view_components.py
import tkinter as tk
from tkinter import ttk

class SensorCard(tk.LabelFrame):
    def __init__(self, parent, sensor_name):
        super().__init__(parent, text=sensor_name, font=("Arial", 12, "bold"), padx=10, pady=10)
        self.sensor_name = sensor_name
        
        # Label per i parametri vitali
        self.lbl_hr = ttk.Label(self, text="Battito Cardiaco: -- bpm", font=("Arial", 11))
        self.lbl_hr.pack(anchor="w", pady=2)
        
        self.lbl_temp = ttk.Label(self, text="Temperatura Corporea: -- °C", font=("Arial", 11))
        self.lbl_temp.pack(anchor="w", pady=2)
        
        self.lbl_spo2 = ttk.Label(self, text="Ossigenazione (SpO2): -- %", font=("Arial", 11))
        self.lbl_spo2.pack(anchor="w", pady=2)
        
        self.lbl_risk = ttk.Label(self, text="Rischio Clinico: --", font=("Arial", 11, "bold"))
        self.lbl_risk.pack(anchor="w", pady=4)
        
        self.lbl_status = tk.Label(self, text="STATO: NESSUN DATO", bg="gray", fg="white", font=("Arial", 10, "bold"), width=20)
        self.lbl_status.pack(pady=5)

    def update_data(self, hr, body_temp, spo2, risk):
        """Aggiorna i testi e i colori della card in base ai dati reali"""
        self.lbl_hr.config(text=f"Battito Cardiaco: {hr} bpm")
        self.lbl_temp.config(text=f"Temperatura Corporea: {body_temp} °C")
        self.lbl_spo2.config(text=f"Ossigenazione (SpO2): {spo2} %")
        self.lbl_risk.config(text=f"Classe di Rischio: {int(risk)}") # Mostriamo 0, 1 o 2
        
        # Logica a 3 CLASSI del TinyML
        risk_class = int(risk)
        if risk_class == 2:
            self.lbl_status.config(text="🔴 EMERGENZA CRITICA", bg="red", fg="white")
            self.config(fg="red") 
        elif risk_class == 1:
            self.lbl_status.config(text="🟠 MONITORAGGIO", bg="dark orange", fg="white")
            self.config(fg="dark orange")
        else:
            self.lbl_status.config(text="🟢 PAZIENTE STABILE", bg="green", fg="white")
            self.config(fg="green")