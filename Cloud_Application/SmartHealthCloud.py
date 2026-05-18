import asyncio
import json
import re
import mysql.connector
from aiocoap import *

# ==========================================
# 1. CLASSE MYSQL (La tua struttura originale)
# ==========================================
class MySQL:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"          
        self.password = "1"  # La tua password
        self.database = "SmartHealthIoT"  # Il tuo Database
        
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
# 2. INDIRIZZI IP DELLA RETE COOJA
# ==========================================
SENSOR_1_IP = "fd00::202:2:2:2"   # Nodo 2
SENSOR_2_IP = "fd00::203:3:3:3"   # Nodo 3
ACTUATOR_IP = "fd00::204:4:4:4"   # Nodo 4

db = MySQL()

# ==========================================
# 3. LOGICA DI RETE E GESTIONE DATI
# ==========================================
async def trigger_alarm(sensor_name):
    """Abbassa la soglia dell'attuatore tramite PUT per forzare l'attivazione dell'allarme"""
    print(f"⚠️ EMERGENZA RILEVATA SU {sensor_name}! Modifico la soglia dell'attuatore {ACTUATOR_IP}...")
    try:
        context = await Context.create_client_context()
        
        # 1. Prepariamo il payload JSON che l'attuatore si aspetta: impostiamo la soglia a 0 (allarme immediato)
        payload_data = {"new_t": 0}
        payload_bytes = json.dumps(payload_data).encode('utf-8')
        
        # 2. Cambiamo il codice in PUT e l'URI sulla risorsa corretta "/threshold"
        request = Message(
            code=PUT, 
            payload=payload_bytes, 
            uri=f"coap://[{ACTUATOR_IP}]/threshold"
        )
        # Specifichiamo che stiamo inviando un JSON
        request.opt.content_format = 50 
        
        response = await context.request(request).response
        print(f"[✓] Soglia aggiornata sull'attuatore! (Risposta CoAP: {response.code})")
        
    except Exception as e:
        print(f"[❌ ERRORE] Impossibile contattare l'attuatore: {e}")

def handle_incoming_data(payload_text, sensor_name):
    """Esegue il parsing dei dati e il salvataggio sul Database MySQL"""
    try:
        # Alcuni nodi inviano il valore di rischio con la virgola decimale: 0,15
        payload_text = re.sub(r'(?<=\d),(?=\d)', '.', payload_text)
        data = json.loads(payload_text)
        hr = int(data.get('hr', 0))
        body_temperature = int(data.get('body_temperature', 0))
        spo2 = int(data.get('spo2', 0))
        risk_score = float(data.get('risk', 0.0))
        sensor_map = {
            'Sensore_1': 1,
            'Sensore_2': 2
        }
        sensor_id = sensor_map.get(sensor_name, 0)
        
        query = "INSERT INTO Health_Measurements (sensor_id, heart_rate, body_temperature, spo2, risk_score) VALUES (%s, %s, %s, %s, %s)"
        success = db.query(query, (sensor_id, hr, body_temperature, spo2, risk_score))
        
        if success:
            print(f"[✓] Dati salvati! (Sensore: {sensor_name} | HR: {hr}, Temp: {body_temperature}, SpO2: {spo2}, Risk: {risk_score})")
            
        if int(risk_score) == 2:
            asyncio.create_task(trigger_alarm(sensor_name))
            
    except Exception as e:
        print(f"[❌ ERRORE PARSING] Errore nei dati da {sensor_name}: {e}")

async def poll_sensor(sensor_ip, sensor_name):
    """Interroga periodicamente il sensore tramite richieste GET (Polling)"""
    print(f"Avviato monitoraggio periodico per {sensor_name} ({sensor_ip})...")
    
    while True:
        try:
            context = await Context.create_client_context()
            # Richiesta GET standard alla risorsa /vitals
            request = Message(code=GET, uri=f"coap://[{sensor_ip}]/vitals")
            
            # Invio della richiesta con un timeout massimo di 3 secondi per evitare blocchi pendenti
            response = await asyncio.wait_for(context.request(request).response, timeout=3.0)
            
            payload_text = response.payload.decode('utf-8')
            print(f"\n[DATO DAL SENSORE {sensor_name}]: {payload_text}")
            handle_incoming_data(payload_text, sensor_name)
                
        except asyncio.TimeoutError:
            print(f"[⚠️ TIMEOUT] Nessuna risposta da {sensor_name} ({sensor_ip}) - Controlla Cooja o il tunnel tunslip6.")
        except asyncio.CancelledError:
            print(f"Monitoraggio interrotto per {sensor_name}.")
            break
        except Exception as e:
            print(f"[❌ ERRORE CONNESSIOINE] Errore temporaneo con {sensor_name}: {e}")
        
        # Aspetta 5 secondi prima di effettuare la prossima richiesta (Frequenza di campionamento)
        await asyncio.sleep(5)

# ==========================================
# 4. MAIN LOOP ASINCRONO (POLLING IN PARALLELO)
# ==========================================
async def main():
    print("Avvio Smart Health Cloud Application (Multi-Node Polling)...")
    print("Sviluppato nativamente per Python 3.14 + aiocoap")
    print("In ascolto tramite Polling periodico... (Premi Ctrl+C per uscire)\n")
    
    # Avviamo i due cicli di interrogazione concorrenti in parallelo
    task_s1 = asyncio.create_task(poll_sensor(SENSOR_1_IP, "Sensore_1"))
    task_s2 = asyncio.create_task(poll_sensor(SENSOR_2_IP, "Sensore_2"))
    
    try:
        await asyncio.gather(task_s1, task_s2)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nChiusura dell'applicazione...")
        task_s1.cancel()
        task_s2.cancel()
        await asyncio.gather(task_s1, task_s2, return_exceptions=True)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        db.close()
        print("Uscita completata.")