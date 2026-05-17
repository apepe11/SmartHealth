from rich.console import Console
from rich.table import Table

class ViewComponents:
    def __init__(self):
        self.console = Console()

    def render_sensors(self, sensors):
        table = Table(title="🏥 Monitor Pazienti Registrati (Sensori CoAP)", style="cyan", title_justify="left")
        table.add_column("Sensor ID", justify="center", style="bold")
        table.add_column("Nome Paziente", justify="left")
        table.add_column("Indirizzo IPv6/Porta", justify="center")
        table.add_column("Freq. Campionamento", justify="center")
        
        for s in sensors:
            table.add_row(str(s["id"]), s["patient_name"], f"[{s['ip_address']}]:{s['port']}", f"{s['sampling_rate']}s")
        
        self.console.print(table)

    def render_actuators(self, actuators):
        table = Table(title="🚨 Attuatori Medici Registrati (Allarmi)", style="magenta", title_justify="left")
        table.add_column("Actuator ID", justify="center", style="bold")
        table.add_column("ID Sensore Associato", justify="center")
        table.add_column("Tipo Attuatore", justify="left")
        table.add_column("Indirizzo IPv6/Porta", justify="center")
        table.add_column("Soglia Rischio (ML)", justify="center")
        
        for a in actuators:
            table.add_row(str(a["id"]), str(a["sensor_id"]), a["type"], f"[{a['ip_address']}]:{a['port']}", f"{a['threshold'] * 100}%")
        
        self.console.print(table)

    def render_measurements(self, records):
        table = Table(title="📊 Parametri Vitali & Analisi Edge AI in Tempo Reale", style="green", title_justify="left")
        table.add_column("Sensore ID", justify="center")
        table.add_column("Frequenza Cardiaca", justify="center")
        table.add_column("Saturazione SpO2", justify="center")
        table.add_column("Score Rischio ML", justify="center")
        table.add_column("Data/Ora Ricezione", justify="left")
        
        for r in records:
            risk_val = float(r[3])
            # Se lo score di rischio predetto dall'Edge AI supera l'80%, colora la riga di rosso lampeggiante
            risk_str = f"[red][bold]{risk_val:.2f} (CRITICO)[/bold][/red]" if risk_val >= 0.80 else f"[green]{risk_val:.2f}[/green]"
            
            table.add_row(str(r[0]), f"{r[1]} bpm", f"{r[2]} %", risk_str, str(r[4]))
            
        if not records:
            self.console.print("[yellow]Nessun dato clinico registrato nel database MySQL.[/yellow]")
        else:
            self.console.print(table)