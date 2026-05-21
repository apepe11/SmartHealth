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
ACTUATOR_IP = "fd01::202:2:2:2"

db = MySQL()

# Variabile per tenere traccia dell'ultimo stato dell'attuatore (evita invii inutili)
last_actuator_state = -1

# ==========================================
# 3. LOGICA DI RETE E GESTIONE DATI
# ==========================================
async def update_actuator(sensor_name, new_risk_level):
    """Aggiorna dinamicamente la soglia dell'attuatore in base al rischio attuale (0, 1, 2)"""
    
    if new_risk_level == 2:
        print(f"⚠️ EMERGENZA (Rischio 2) rilevata su {sensor_name}! Attivo LED ROSSO su {ACTUATOR_IP}...")
    elif new_risk_level == 1:
        print(f"⚠️ ATTENZIONE (Rischio 1) rilevata su {sensor_name}. Aggiorno l'attuatore a rischio medio...")
    else:
         print(f"✅ SITUAZIONE NORMALE (Rischio 0) su {sensor_name}. Ripristino LED VERDE su {ACTUATOR_IP}...")

    try:
        context = await Context.create_client_context()
        
        # Inviamo il livello di rischio dinamico (0, 1, o 2)
        payload_data = {"new_t": new_risk_level} 
        payload_bytes = json.dumps(payload_data).encode('utf-8')
        
        request = Message(
            code=PUT, 
            payload=payload_bytes, 
            uri=f"coap://[{ACTUATOR_IP}]:5683/threshold"
        )
        request.opt.content_format = 50 # APPLICATION_JSON
        
        response = await context.request(request).response
        print(f"[✓] Attuatore aggiornato con successo! (Risposta CoAP: {response.code})")
        
    except Exception as e:
        print(f"[❌ ERRORE] Impossibile contattare l'attuatore: {e}")

def handle_incoming_data(payload_text, sensor_name):
    """Esegue il parsing dei dati e il salvataggio sul Database MySQL"""
    global last_actuator_state
    
    try:
        data = json.loads(payload_text)
        hr = int(data.get('hr', 0))
        body_temperature = int(data.get('body_temperature', 0))
        spo2 = int(data.get('spo2', 0))
        
        # Il rischio è un intero (Classe 0, 1, 2) generato dal TinyML
        risk_score = int(data.get('risk', 0))
        
        sensor_map = {'Sensore_1': 1}
        sensor_id = sensor_map.get(sensor_name, 0)
        
        query = "INSERT INTO Health_Measurements (sensor_id, heart_rate, body_temperature, spo2, risk_score) VALUES (%s, %s, %s, %s, %s)"
        success = db.query(query, (sensor_id, hr, body_temperature, spo2, risk_score))
        
        if success:
            print(f"[✓] DB Aggiornato -> Sensore: {sensor_name} | HR: {hr}, Temp: {body_temperature}, SpO2: {spo2}, Classe Rischio: {risk_score}")
            
        # 🔴 LOGICA DINAMICA: Aggiorna l'attuatore SOLO se il livello di rischio è cambiato
        if risk_score != last_actuator_state:
            asyncio.create_task(update_actuator(sensor_name, risk_score))
            last_actuator_state = risk_score
            
    except Exception as e:
        print(f"[❌ ERRORE PARSING] Errore nei dati da {sensor_name}: {e}")

# ==========================================
# 🔴 FUNZIONE: OSSERVAZIONE ASINCRONA
# ==========================================
async def observe_sensor(sensor_ip, sensor_name):
    """Si iscrive alla risorsa /vitals del sensore sfruttando il pattern Observe di CoAP"""
    
    while True:
        print(f"Avvio/Ripristino sottoscrizione OBSERVE per {sensor_name} ({sensor_ip})...")
        
        try:
            context = await Context.create_client_context()
            
            request = Message(code=GET, uri=f"coap://[{sensor_ip}]/vitals", observe=0)
            protocol_request = context.request(request)
            
            first_response = await protocol_request.response
            payload_text = first_response.payload.decode('utf-8')
            print(f"\n[PRIMA RISPOSTA COAP DA {sensor_name}]: {payload_text}")
            handle_incoming_data(payload_text, sensor_name)
            
            async for response in protocol_request.observation:
                payload_text = response.payload.decode('utf-8')
                print(f"\n[NOTIFICA COAP DA {sensor_name}]: {payload_text}")
                handle_incoming_data(payload_text, sensor_name)
                
        except asyncio.CancelledError:
            print(f"\nMonitoraggio Observe interrotto volontariamente per {sensor_name}.")
            break
        except Exception as e:
            print(f"\n[❌ ERRORE DI RETE] Impossibile raggiungere {sensor_name}: {e}")
            
        print("--- Ritento la connessione tra 5 secondi... ---")
        await asyncio.sleep(5)


# ==========================================
# 4. MAIN LOOP ASINCRONO
# ==========================================
async def main():
    print("Avvio Smart Health Cloud Application (CoAP Observe Mode)...")
    print("Sviluppato in conformità con i requisiti del corso IoT 2026")
    print("In ascolto asincrono delle notifiche dei sensori... (Premi Ctrl+C per uscire)\n")
    
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