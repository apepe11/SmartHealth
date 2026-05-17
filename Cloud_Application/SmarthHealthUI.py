from consolemenu import ConsoleMenu, MenuFormatBuilder, MenuBorderStyleType
from consolemenu.items import FunctionItem
from db_manager import DBManager
from config_manager import ConfigManager
from coap_service import CoAPService
from view_components import ViewComponents

class SmartHealthApp:
    def __init__(self):
        self.db = DBManager()
        self.config = ConfigManager()
        self.view = ViewComponents()
        self.__setup_menu()

    def __setup_menu(self):
        # Stile estetico robusto per il terminale
        fmt = MenuFormatBuilder().set_border_style_type(MenuBorderStyleType.HEAVY_BORDER) \
                                 .set_title_align('center').set_subtitle_align('center')
        
        self.menu = ConsoleMenu(
            "🏥 SMART HEALTH SYSTEM 🏥", 
            "Interfaccia Utente Cloud - Monitoraggio Pazienti IoT", 
            formatter=fmt
        )
        
        # Binding delle funzioni ai bottoni del menù
        self.menu.append_item(FunctionItem("Visualizza Sensori Paziente", self.ui_show_sensors))
        self.menu.append_item(FunctionItem("Visualizza Attuatori/Allarmi", self.ui_show_actuators))
        self.menu.append_item(FunctionItem("Cartella Clinica Digitale (Dati & ML)", self.ui_show_measurements))
        self.menu.append_item(FunctionItem("Modifica Tempo Campionamento Sensore", self.ui_change_sampling))
        self.menu.append_item(FunctionItem("Modifica Soglia Allarme Attuatore", self.ui_change_threshold))

    def run(self):
        self.menu.show()
        self.db.close() # Chiude la connessione a MySQL all'uscita

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
            
            # Cerca il sensore locale per prendere IP e Porta
            sensor = next((s for s in self.config.get_sensors() if s["id"] == s_id), None)
            if not sensor:
                print("[Errore] ID Sensore non valido.")
                return
            
            # Chiamata CoAP di rete verso la risorsa "/sampling" del nodo Contiki
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

            # Chiamata CoAP di rete verso la risorsa "/threshold" dell'attuatore Contiki
            # Convertiamo in percentuale intera (es: 85) per renderlo più leggero per il pacchetto CoAP in C
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