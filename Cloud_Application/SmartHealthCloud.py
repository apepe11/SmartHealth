import asyncio
import json
import re
import mysql.connector
from aiocoap import *

# ==========================================
# 1. CLASSE MYSQL (CORRETTA)
# ==========================================
class MySQL:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"          
        self.password = "1"  
        self.database = "SmartHealthIoT"  
        
        self.connection = mysql.connector.connect(
            host=self.host, user=self.user, password=self.password, database=self.database 
        )
        if not self.connection.is_connected():
            raise Exception("Connessione MySQL fallita")
        
    def query(self, query_text, query_values=None):
        try:
            cursor = self.connection.cursor(buffered=True) 
            cursor.execute(query_text, query_values)
            self.connection.commit()
            cursor.close() 
            return True
        except mysql.connector.Error as err:
            print("Errore MySQL: ", err)
            return False 
    
    def close(self):
        self.connection.close()

# ==========================================
# 2. INDIRIZZI IP DELLA RETE MISTA (HARDWARE + COOJA)
# ==========================================

SENSOR_1_IP = "fd00::f6ce:36b9:a760:ecea"   
# Questo va bene per l'attuatore dentro Cooja
# CORRETTO: Usiamo l'indirizzo globale instradato tramite l'interfaccia tun0 di tunslip6
ACTUATOR_IP = "fd00::202:2:2:2"

db = MySQL()

# ==========================================
# 3. LOGICA DI RETE E GESTIONE DATI
# ==========================================
async def trigger_alarm(sensor_name):
    """Abbassa la soglia dell'attuatore tramite PUT per forzare l'attivazione dell'allarme"""
    print(f"⚠️ EMERGENZA RILEVATA SU {sensor_name}! Modifico la soglia dell'attuatore {ACTUATOR_IP} alla classe di rischio massima...")
    try:
        context = await Context.create_client_context()
        
        # Inviamo la soglia d'allarme come intero (Classe 0, 1 o 2). Impostando 0 scatta per qualsiasi anomalia.
        payload_data = {"new_t": 0}
        payload_bytes = json.dumps(payload_data).encode('utf-8')
        
        request = Message(
            code=PUT, 
            payload=payload_bytes, 
            uri=f"coap://[{ACTUATOR_IP}]:5683/threshold"
        )
        request.opt.content_format = 50 # APPLICATION_JSON
        
        response = await context.request(request).response
        print(f"[✓] Soglia aggiornata sull'attuatore! (Risposta CoAP: {response.code})")
        
    except Exception as e:
        print(f"[❌ ERRORE] Impossibile contattare l'attuatore: {e}")

def handle_incoming_data(payload_text, sensor_name):
    """Esegue il parsing dei dati e il salvataggio sul Database MySQL"""
    try:
        data = json.loads(payload_text)
        hr = int(data.get('hr', 0))
        body_temperature = int(data.get('body_temperature', 0))
        spo2 = int(data.get('spo2', 0))
        
        # 🔴 CORREZIONE: Il rischio ora è un intero (Classe 0, 1, 2) generato dal TinyML
        risk_score = int(data.get('risk', 0))
        
        sensor_map = {'Sensore_1': 1}
        sensor_id = sensor_map.get(sensor_name, 0)
        
        query = "INSERT INTO Health_Measurements (sensor_id, heart_rate, body_temperature, spo2, risk_score) VALUES (%s, %s, %s, %s, %s)"
        success = db.query(query, (sensor_id, hr, body_temperature, spo2, risk_score))
        
        if success:
            print(f"[✓] Dati salvati nel DB! (Sensore: {sensor_name} | HR: {hr}, Temp: {body_temperature}, SpO2: {spo2}, Classe Rischio: {risk_score})")
            
        # Se il modello TinyML a bordo del sensore restituisce la classe 2 (Emergenza), allertiamo l'attuatore
        if risk_score == 2:
            asyncio.create_task(trigger_alarm(sensor_name))
            
    except Exception as e:
        print(f"[❌ ERRORE PARSING] Errore nei dati da {sensor_name}: {e}")

# ==========================================
# 🔴 FUNZIONE: OSSERVAZIONE ASINCRONA (CORRETTA)
# ==========================================
async def observe_sensor(sensor_ip, sensor_name):
    """Si iscrive alla risorsa /vitals del sensore sfruttando il pattern Observe di CoAP"""
    
    # Il ciclo while True mantiene in vita l'app anche se il sensore si disconnette! (Fault Tolerance)
    while True:
        print(f"Avvio/Ripristino sottoscrizione OBSERVE per {sensor_name} ({sensor_ip})...")
        
        try:
            context = await Context.create_client_context()
            
            # Creiamo una richiesta GET con l'opzione observe abilitata
            request = Message(code=GET, uri=f"coap://[{sensor_ip}]/vitals", observe=0)
            
            protocol_request = context.request(request)
            
            # 1. 🔴 CORREZIONE: Dobbiamo attendere esplicitamente la PRIMA risposta!
            first_response = await protocol_request.response
            payload_text = first_response.payload.decode('utf-8')
            print(f"\n[PRIMA RISPOSTA COAP DA {sensor_name}]: {payload_text}")
            handle_incoming_data(payload_text, sensor_name)
            
            # 2. Ora che l'Observe è confermato, restiamo in ascolto dei pacchetti futuri
            async for response in protocol_request.observation:
                payload_text = response.payload.decode('utf-8')
                print(f"\n[NOTIFICA COAP DA {sensor_name}]: {payload_text}")
                handle_incoming_data(payload_text, sensor_name)
                
        except asyncio.CancelledError:
            print(f"\nMonitoraggio Observe interrotto volontariamente per {sensor_name}.")
            break
        except Exception as e:
            # Se l'IP non è raggiungibile o il nodo è spento, catturiamo l'errore qui
            print(f"\n[❌ ERRORE DI RETE] Impossibile raggiungere {sensor_name}: {e}")
            
        # 3. 🔴 MECCANISMO DI RECOVERY: Aspetta 5 secondi e poi ritenta!
        print("--- Ritento la connessione tra 5 secondi... ---")
        await asyncio.sleep(5)


# ==========================================
# 4. MAIN LOOP ASINCRONO (SOTTOCCRIZIONE)
# ==========================================
async def main():
    print("Avvio Smart Health Cloud Application (CoAP Observe Mode)...")
    print("Sviluppato in conformità con i requisiti del corso IoT 2026")
    print("In ascolto asincrono delle notifiche dei sensori... (Premi Ctrl+C per uscire)\n")
    
    # Avviamo il task di osservazione (Il cloud non fa richieste continue, aspetta le notifiche)
    task_s1 = asyncio.create_task(observe_sensor(SENSOR_1_IP, "Sensore_1"))
    
    try:
        await asyncio.gather(task_s1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nChiusura dell'applicazione...")
        task_s1.cancel()
        await asyncio.gather(task_s1, return_exceptions=True)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        db.close()
        print("Uscita completata.")