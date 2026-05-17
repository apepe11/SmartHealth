from backend.db_manager import DBManager
from configuration_manager import ConfigManager
from coap_service import CoAPService
from view_components import ViewComponents

class SmartHealthApp:
    def __init__(self):
        self.db = DBManager()
        self.config = ConfigManager()
        self.view = ViewComponents()

    def display_menu(self):
        """Visualizza il menù principale."""
        print("\n" + "="*60)
        print("🏥 SMART HEALTH SYSTEM 🏥")
        print("Interfaccia Utente Cloud - Monitoraggio Pazienti IoT")
        print("="*60)
        print("\n1. Visualizza Sensori Paziente")
        print("2. Visualizza Attuatori/Allarmi")
        print("3. Cartella Clinica Digitale (Dati & ML)")
        print("4. Modifica Tempo Campionamento Sensore")
        print("5. Modifica Soglia Allarme Attuatore")
        print("0. Esci")
        print("="*60)

    def run(self):
        """Esegue l'applicazione con menù interattivo."""
        while True:
            self.display_menu()
            choice = input("\nScegli un'opzione: ").strip()
            
            if choice == "1":
                self.ui_show_sensors()
            elif choice == "2":
                self.ui_show_actuators()
            elif choice == "3":
                self.ui_show_measurements()
            elif choice == "4":
                self.ui_change_sampling()
            elif choice == "5":
                self.ui_change_threshold()
            elif choice == "0":
                print("\nChiusura applicazione...")
                break
            else:
                print("[Errore] Opzione non valida. Riprova.")
        
        self.db.close()  # Chiude la connessione a MySQL all'uscita

    def ui_show_sensors(self):
        self.view.render_sensors(self.config.get_sensors())
        input("\nPremi [Invio] per tornare al menù principale...")

    def ui_show_actuators(self):
        self.view.render_actuators(self.config.get_actuators())
        input("\nPremi [Invio] per tornare al menù principale...")

    def ui_show_measurements(self):
        records = self.db.fetch_latest_measurements()
        self.view.render_measurements(records)
        input("\nPremi [Invio] per tornare al menù principale...")

    def ui_change_sampling(self):
        self.view.render_sensors(self.config.get_sensors())
        try:
            s_id = int(input("\nInserisci l'ID del Sensore da riconfigurare: "))
            new_rate = int(input("Inserisci il nuovo intervallo di campionamento (in secondi): "))
            
            sensor = next((s for s in self.config.get_sensors() if s["id"] == s_id), None)
            if not sensor:
                print("[Errore] ID Sensore non valido.")
                return
            
            payload = {"new_sr": new_rate}
            if CoAPService.send_put_request(sensor["ip_address"], sensor["port"], "/sampling", payload):
                self.config.update_sensor_rate(s_id, new_rate)
                print("\n[✓ Successo] Dispositivo IoT aggiornato via CoAP e configurazione salvata!")
            else:
                print("\n[✗ Errore] Impossibile comunicare via CoAP con il sensore.")
        except ValueError:
            print("[Errore] Inserisci valori numerici validi.")
        input("\nPremi [Invio]...")

    def ui_change_threshold(self):
        self.view.render_actuators(self.config.get_actuators())
        try:
            a_id = int(input("\nInserisci l'ID dell'Attuatore/Allarme da configurare: "))
            new_th = float(input("Inserisci la nuova soglia di rischio ML (da 0.0 a 1.0, es: 0.85): "))
            
            actuator = next((a for a in self.config.get_actuators() if a["id"] == a_id), None)
            if not actuator:
                print("[Errore] ID Attuatore non valido.")
                return

            payload = {"new_t": str(int(new_th * 100))}
            if CoAPService.send_put_request(actuator["ip_address"], actuator["port"], "/threshold", payload):
                self.config.update_actuator_threshold(a_id, new_th)
                print("\n[✓ Successo] Soglia attuatore aggiornata via CoAP e configurazione salvata!")
            else:
                print("\n[✗ Errore] Impossibile comunicare via CoAP con l'attuatore.")
        except ValueError:
            print("[Errore] Inserisci valori numerici validi.")
        input("\nPremi [Invio]...")

if __name__ == "__main__":
    app = SmartHealthApp()
    app.run()