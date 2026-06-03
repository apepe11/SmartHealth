import asyncio
import json
import mysql.connector
from aiocoap import *

# Importo le configurazioni dal file esterno situato nella cartella frontend
from frontend.configuration_manager import DB_CONFIG, SENSORS_CONFIG

# Classe per gestire la connessione con il db MySQL 
class MySQL:
    def __init__(self):
        # Utilizzo i valori presi da DB_CONFIG
        self.host = DB_CONFIG["host"]
        self.user = DB_CONFIG["user"]          
        self.password = DB_CONFIG["password"]  
        self.database = DB_CONFIG["database"]  
        
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

db = MySQL()

async def update_actuator(sensor_name, new_risk_level):
    """Invia il comando CoAP PUT all'attuatore fisico per aggiornare i LED"""
    
    # Recupero l'IP dell'attuatore associato a questo sensore dal file di configurazione
    actuator_ip = SENSORS_CONFIG[sensor_name]["actuator_ip"]
    
    if new_risk_level == 2:
        print(f" 🚨 EMERGENZA (Rischio 2) rilevata su {sensor_name}! Attivo LED ROSSO su {actuator_ip}...")
    elif new_risk_level == 1:
        print(f" ⚠️ ATTENZIONE (Rischio 1) rilevata su {sensor_name}. Attivo LED GIALLO su {actuator_ip}...")
    else:
        print(f" ✅ SITUAZIONE NORMALE (Rischio 0) su {sensor_name}. Attivo LED VERDE su {actuator_ip}...")

    try:
        context = await Context.create_client_context()
        
        # Preparo il payload JSON per l'attuatore
        payload_data = {"new_t": new_risk_level} 
        payload_bytes = json.dumps(payload_data).encode('utf-8')
        
        request = Message(
            code=PUT,
            payload=payload_bytes, 
            uri=f"coap://[{actuator_ip}]:5683/threshold"
        )
        request.opt.content_format = 50 # application/json
        
        response = await context.request(request).response
        print(f" 🟢 Attuatore aggiornato con successo! (Risposta CoAP: {response.code})")
        
    except Exception as e:
        print(f" 🔴 Impossibile contattare l'attuatore: {e}")

def handle_incoming_data(payload_text, sensor_name):
    """Esegue il parsing dei dati, salva su DB e innesca la logica Closed-Loop"""
    
    try:
        data = json.loads(payload_text)
        hr = int(data.get('hr', 0))
        body_temperature = int(data.get('body_temperature', 0))
        spo2 = int(data.get('spo2', 0))
        risk_score = int(data.get('risk', 0))
        
        # Recupero l'ID del sensore dal file di configurazione
        sensor_id = SENSORS_CONFIG[sensor_name]["id"]
        
        # Salva nel database
        query = "INSERT INTO Health_Measurements (sensor_id, heart_rate, body_temperature, spo2, risk_score) VALUES (%s, %s, %s, %s, %s)"
        success = db.query(query, (sensor_id, hr, body_temperature, spo2, risk_score))
        
        if success:
            print(f" 💾 DB Aggiornato -> Sensore: {sensor_name} | HR: {hr}, Temp: {body_temperature}, SpO2: {spo2}, Rischio: {risk_score}")
            
        # ⚠️ CLOSED-LOOP ATTIVO: Invia il comando all'attuatore a OGNI lettura.
        asyncio.create_task(update_actuator(sensor_name, risk_score))
            
    except Exception as e:
        print(f" ❌ Errore nel parsing dei dati da {sensor_name}: {e}")

async def observe_sensor(sensor_ip, sensor_name):
    """Sottoscrizione CoAP Observe verso il sensore fisico"""
    while True:
        print(f"\n⏳ Avvio sottoscrizione OBSERVE per {sensor_name} ({sensor_ip})...")
        
        try:
            context = await Context.create_client_context()
            
            # Porta esplicita per evitare conflitti di routing
            request = Message(code=GET, uri=f"coap://[{sensor_ip}]:5683/vitals", observe=0)
            protocol_request = context.request(request)
            
            first_response = await protocol_request.response
            payload_text = first_response.payload.decode('utf-8')
            print(f"\n[PRIMA LETTURA DA {sensor_name}]: {payload_text}")
            handle_incoming_data(payload_text, sensor_name)
            
            async for response in protocol_request.observation:
                payload_text = response.payload.decode('utf-8')
                print(f"\n[NOTIFICA DA {sensor_name}]: {payload_text}")
                handle_incoming_data(payload_text, sensor_name)
                
        except asyncio.CancelledError:
            print(f"\n⏹️ Monitoraggio interrotto volontariamente per {sensor_name}.")
            break
        except Exception as e:
            print(f"\n⚠️ Rete instabile o sensore {sensor_name} non raggiungibile: {e}")
            
        print("🔄 Ritento la connessione tra 5 secondi...")
        await asyncio.sleep(5)

async def main():
    print("🚀 Avvio Smart Health Cloud Application...")
    
    # Creazione dinamica dei task in base a quanti sensori ci sono in SENSORS_CONFIG
    tasks = []
    for sensor_name, config in SENSORS_CONFIG.items():
        sensor_ip = config["sensor_ip"]
        tasks.append(asyncio.create_task(observe_sensor(sensor_ip, sensor_name)))
    
    try:
        await asyncio.gather(*tasks)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n🛑 Chiusura dell'applicazione...")
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        db.close()
        print("✅ Uscita completata.")