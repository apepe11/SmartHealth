import tkinter as tk
from tkinter import ttk


class SensorCard(tk.LabelFrame):
    def __init__(self, parent, sensor_name, sr_callback=None):
        super().__init__(
            parent,
            text=f"📡 {sensor_name}",
            font=("Arial", 13, "bold"),
            padx=15,
            pady=15,
            bg="white",
            fg="#333333",
            relief="groove",
            borderwidth=2
        )

        self.sensor_name = sensor_name
        self.sr_callback = sr_callback

        bg_color = "white"
        font_title = ("Arial", 12, "bold")
        font_value = ("Arial", 18, "bold")
        font_normal = ("Arial", 10)

        # HEART RATE
        hr_frame = tk.Frame(self, bg=bg_color, relief="solid", borderwidth=1)
        hr_frame.pack(fill="x", pady=3)

        tk.Label(
            hr_frame, 
            text="❤️  HEART RATE", 
            font=font_title, 
            bg=bg_color,
            fg="#555555"
        ).pack(pady=(8, 2))

        self.lbl_hr = tk.Label(
            hr_frame, 
            text="-- bpm", 
            font=font_value, 
            bg=bg_color,
            fg="#333333"
        )
        self.lbl_hr.pack(pady=(0, 8))

        # BODY TEMPERATURE
        temp_frame = tk.Frame(self, bg=bg_color, relief="solid", borderwidth=1)
        temp_frame.pack(fill="x", pady=3)

        tk.Label(
            temp_frame, 
            text="🌡️  BODY TEMPERATURE", 
            font=font_title, 
            bg=bg_color,
            fg="#555555"
        ).pack(pady=(8, 2))

        self.lbl_temp = tk.Label(
            temp_frame, 
            text="-- °C", 
            font=font_value, 
            bg=bg_color,
            fg="#333333"
        )
        self.lbl_temp.pack(pady=(0, 8))

        # OXYGEN SATURATION
        spo2_frame = tk.Frame(self, bg=bg_color, relief="solid", borderwidth=1)
        spo2_frame.pack(fill="x", pady=3)

        tk.Label(
            spo2_frame, 
            text="🫁  OXYGEN SATURATION", 
            font=font_title, 
            bg=bg_color,
            fg="#555555"
        ).pack(pady=(8, 2))

        self.lbl_spo2 = tk.Label(
            spo2_frame, 
            text="-- %", 
            font=font_value, 
            bg=bg_color,
            fg="#333333"
        )
        self.lbl_spo2.pack(pady=(0, 8))

        # RISK LEVEL
        risk_frame = tk.Frame(self, bg=bg_color, relief="solid", borderwidth=1)
        risk_frame.pack(fill="x", pady=5)

        tk.Label(
            risk_frame, 
            text="⚠️  RISK LEVEL", 
            font=font_title, 
            bg=bg_color,
            fg="#555555"
        ).pack(pady=(8, 2))

        self.lbl_risk = tk.Label(
            risk_frame, 
            text="--", 
            font=("Arial", 22, "bold"), 
            bg=bg_color,
            fg="#333333"
        )
        self.lbl_risk.pack(pady=(0, 8))

        # STATUS
        self.lbl_status = tk.Label(
            self,
            text="STATUS: WAITING",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#666666",
            relief="solid",
            borderwidth=1,
            pady=8
        )
        self.lbl_status.pack(fill="x", pady=8)

        # SAMPLING RATE CONTROL
        ctrl_frame = tk.LabelFrame(
            self,
            text="⚙️  CONTROL PANEL",
            font=("Arial", 11, "bold"),
            bg=bg_color,
            fg="#333333",
            relief="groove",
            borderwidth=2,
            padx=12,
            pady=12
        )
        ctrl_frame.pack(fill="x", pady=5)

        # Explanation
        tk.Label(
            ctrl_frame,
            text="Set how often the sensor sends\ndata to the server:",
            font=("Arial", 9),
            bg=bg_color,
            fg="#666666",
            justify="left"
        ).pack(anchor="w", pady=(0, 8))

        # Frame for input and button
        input_frame = tk.Frame(ctrl_frame, bg=bg_color)
        input_frame.pack(fill="x")

        # Label "Interval"
        tk.Label(
            input_frame,
            text="Interval:",
            font=("Arial", 10, "bold"),
            bg=bg_color
        ).pack(side="left", padx=(0, 5))

        # Entry for value
        self.entry_sr = tk.Entry(
            input_frame,
            width=5,
            font=("Arial", 14, "bold"),
            justify="center",
            relief="solid",
            borderwidth=1,
            bg="white"
        )
        self.entry_sr.insert(0, "5")
        self.entry_sr.pack(side="left", padx=(0, 5))

        # Label "s"
        tk.Label(
            input_frame,
            text="s",
            font=("Arial", 10, "bold"),
            bg=bg_color
        ).pack(side="left", padx=(0, 15))

        # Send button
        self.btn_send = tk.Button(
            input_frame,
            text="SEND",
            command=self._on_sr_submit,
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=4,
            cursor="hand2",
            relief="raised",
            borderwidth=1
        )
        self.btn_send.pack(side="left")

        # Feedback label
        self.lbl_feedback = tk.Label(
            ctrl_frame,
            text="",
            font=("Arial", 9, "bold"),
            bg=bg_color,
            fg="#4CAF50"
        )
        self.lbl_feedback.pack(anchor="w", pady=(8, 0))

    def _on_sr_submit(self):
        """Send new sampling rate"""
        value = self.entry_sr.get()
        
        # Validation
        if not value.isdigit():
            self.lbl_feedback.config(text=" Please enter a number!", fg="red")
            return
        
        rate = int(value)
        if rate < 1:
            self.lbl_feedback.config(text=" Minimum 1 second!", fg="red")
            return
        
        if rate > 3600:
            self.lbl_feedback.config(text=" Maximum 3600 seconds!", fg="red")
            return
        
        # Send callback
        if self.sr_callback:
            self.sr_callback(rate)
            self.lbl_feedback.config(
                text=f"✅ OK! Sampling rate set to {rate} seconds",
                fg="green"
            )
            
            # Visual effect on button
            self.btn_send.config(bg="#45a049", text="✓ SENT")
            self.after(1500, lambda: self.btn_send.config(bg="#4CAF50", text="SEND"))

    def update_data(self, hr, body_temp, spo2, risk, status="ONLINE"):
        """Update values and status"""
        
        # Handle SENSOR_MISSING state
        if status == "SENSOR_MISSING":
            self.lbl_hr.config(text="-- bpm", fg="#999999")
            self.lbl_temp.config(text="-- °C", fg="#999999")
            self.lbl_spo2.config(text="-- %", fg="#999999")
            self.lbl_risk.config(text="NO DATA", fg="#999999")
            self.lbl_status.config(
                text="❌ SENSOR NOT PRESENT - NO MEASUREMENT AVAILABLE",
                bg="#9E9E9E",
                fg="white",
                font=("Arial", 11, "bold")
            )
            # Disable control panel when sensor is missing
            self.btn_send.config(state="disabled", bg="#cccccc")
            self.entry_sr.config(state="disabled", bg="#f0f0f0")
            return
        
        # Re-enable controls if sensor comes back online
        self.btn_send.config(state="normal", bg="#4CAF50")
        self.entry_sr.config(state="normal", bg="white")

        if status == "NODE_FAILURE":
            self.lbl_hr.config(text="-- bpm", fg="#999999")
            self.lbl_temp.config(text="-- °C", fg="#999999")
            self.lbl_spo2.config(text="-- %", fg="#999999")
            self.lbl_risk.config(text="UNAVAILABLE", fg="#999999")
            self.lbl_status.config(
                text="🚨 STATUS: NODE OFFLINE",
                bg="#666666",
                fg="white"
            )
            return

        # Format values
        hr_text = f"{int(hr)} bpm" if hr else "-- bpm"
        temp_text = f"{float(body_temp):.1f} °C" if body_temp else "-- °C"
        spo2_text = f"{int(spo2)} %" if spo2 else "-- %"

        self.lbl_hr.config(text=hr_text, fg="#333333")
        self.lbl_temp.config(text=temp_text, fg="#333333")
        self.lbl_spo2.config(text=spo2_text, fg="#333333")

        # Risk management
        risk_level = int(float(risk))
        
        if risk_level == 0:
            self.lbl_risk.config(text="NORMAL", fg="#4CAF50")
            self.lbl_status.config(
                text="🟢 STATUS: PATIENT STABLE",
                bg="#4CAF50",
                fg="white"
            )
        elif risk_level == 1:
            self.lbl_risk.config(text="WARNING", fg="#FF9800")
            self.lbl_status.config(
                text="🟡 STATUS: ATTENTION REQUIRED",
                bg="#FF9800",
                fg="white"
            )
        else:
            self.lbl_risk.config(text="CRITICAL", fg="#f44336")
            self.lbl_status.config(
                text="🔴 STATUS: EMERGENCY!",
                bg="#f44336",
                fg="white"
            )



if __name__ == "__main__":
    root = tk.Tk()
    root.title("Patient Monitor")
    root.configure(bg="#f5f5f5")
    
    def callback(val):
        print(f" Sampling rate changed to {val} seconds")
    
    # Create card
    card = SensorCard(root, "Patient 01", callback)
    card.pack(padx=20, pady=20, fill="both", expand=True)
    
    # Test with data
    card.update_data(75, 36.8, 98, 0)
    
    root.mainloop()