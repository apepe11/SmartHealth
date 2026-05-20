# view_components.py
import tkinter as tk
from tkinter import ttk

class SensorCard(tk.LabelFrame):
    def __init__(self, parent, sensor_name, sr_callback=None, t_callback=None):
        super().__init__(parent, text=sensor_name, font=("Arial", 12, "bold"), padx=10, pady=10)
        self.sensor_name = sensor_name
        self.sr_callback = sr_callback
        self.t_callback = t_callback
        
        # Visualizzazione parametri vitali
        self.lbl_hr = ttk.Label(self, text="Battito Cardiaco: -- bpm", font=("Arial", 11))
        self.lbl_hr.pack(anchor="w", pady=2)
        
        self.lbl_temp = ttk.Label(self, text="Temperatura Corporea: -- °C", font=("Arial", 11))
        self.lbl_temp.pack(anchor="w", pady=2)
        
        self.lbl_spo2 = ttk.Label(self, text="Ossigenazione (SpO2): -- %", font=("Arial", 11))
        self.lbl_spo2.pack(anchor="w", pady=2)
        
        self.lbl_risk = ttk.Label(self, text="Classe di Rischio: --", font=("Arial", 11, "bold"))
        self.lbl_risk.pack(anchor="w", pady=4)
        
        self.lbl_status = tk.Label(self, text="STATO: NESSUN DATO", bg="gray", fg="white", font=("Arial", 10, "bold"), width=20)
        self.lbl_status.pack(pady=5)
        
        # ==========================================
        # NUOVO PANNELLO DI CONTROLLO (USER INPUT LOGIC)
        # ==========================================
        ctrl_frame = ttk.LabelFrame(self, text="⚙️ Pannello di Controllo Comandi (CoAP PUT)")
        ctrl_frame.pack(fill="x", pady=10, padx=5)
        
        # Blocco 1: Frequenza di Campionamento
        ttk.Label(ctrl_frame, text="Sampling Rate (s):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_sr = ttk.Entry(ctrl_frame, width=6)
        self.entry_sr.insert(0, "5") # Valore di default
        self.entry_sr.grid(row=0, column=1, padx=5, pady=5)
        btn_send_sr = ttk.Button(ctrl_frame, text="Invia SR", command=self._on_sr_submit)
        btn_send_sr.grid(row=0, column=2, padx=5, pady=5)
        
        # Blocco 2: Soglia di Allarme dell'Attuatore
        ttk.Label(ctrl_frame, text="Soglia Rischio (0-2):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_t = ttk.Entry(ctrl_frame, width=6)
        self.entry_t.insert(0, "2") # Default allarme su classe critica 2
        self.entry_t.grid(row=1, column=1, padx=5, pady=5)
        btn_send_t = ttk.Button(ctrl_frame, text="Invia Soglia", command=self._on_t_submit)
        btn_send_t.grid(row=1, column=2, padx=5, pady=5)

    def _on_sr_submit(self):
        if self.sr_callback:
            val = self.entry_sr.get()
            if val.isdigit():
                self.sr_callback(int(val))

    def _on_t_submit(self):
        if self.t_callback:
            val = self.entry_t.get()
            if val.isdigit() and 0 <= int(val) <= 2:
                self.t_callback(int(val))

    def update_data(self, hr, body_temp, spo2, risk):
        """Aggiorna i testi e i colori della card in base ai dati reali"""
        self.lbl_hr.config(text=f"Battito Cardiaco: {hr} bpm")
        self.lbl_temp.config(text=f"Temperatura Corporea: {body_temp} °C")
        self.lbl_spo2.config(text=f"Ossigenazione (SpO2): {spo2} %")
        self.lbl_risk.config(text=f"Classe di Rischio TinyML: {int(risk)}")
        
        risk_class = int(risk)
        if risk_class == 2:
            self.lbl_status.config(text="🔴 EMERGENZA CRITICA", bg="red", fg="white")
        elif risk_class == 1:
            self.lbl_status.config(text="🟠 MONITORAGGIO", bg="dark orange", fg="white")
        else:
            self.lbl_status.config(text="🟢 PAZIENTE STABILE", bg="green", fg="white")