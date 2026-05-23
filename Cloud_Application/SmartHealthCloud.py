import asyncio
import json
import re
import mysql.connector
from aiocoap import *

# classe per gestire la connessione con il db MYsql 
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


SENSOR_1_IP = "fd00::f6ce:36b9:a760:ecea"   # indirizzo IPv6 del sensore fisico 
ACTUATOR_IP = "fd01::202:2:2:2"  # indirizzo IPv6 del attuatore cooja 

db = MySQL()

# tiene traccia dell'ultimo stato dell'attuatore 
last_actuator_state = -1

async def update_actuator(sensor_name, new_risk_level):
    """Aggiorna dinamicamente la soglia dell'attuatore in base al rischio attuale (0, 1, 2)"""
    
    if new_risk_level == 2:
        print(f" EMERGENZA (Rischio 2) rilevata su {sensor_name}! Attivo LED ROSSO su {ACTUATOR_IP}...")
    elif new_risk_level == 1:
        print(f" ATTENZIONE (Rischio 1) rilevata su {sensor_name}. Attivo LED Giallo su {ACTUATOR_IP}...")
    else:
         print(f" SITUAZIONE NORMALE (Rischio 0) su {sensor_name}. Attivo LED VERDE su {ACTUATOR_IP}...")

    try:
        context = await Context.create_client_context()
        
        # invio il livello di rischio dinamico al attuatore 
        payload_data = {"new_t": new_risk_level} 
        payload_bytes = json.dumps(payload_data).encode('utf-8')
        
        request = Message(
            code=PUT, # PUT perchè stiamo aggiornando la soglia dell'attuatore
            payload=payload_bytes, 
            uri=f"coap://[{ACTUATOR_IP}]:5683/threshold"
        )
        request.opt.content_format = 50 
        
        response = await context.request(request).response
        print(f"Attuatore aggiornato con successo! (Risposta CoAP: {response.code})")
        
    except Exception as e:
        print(f"Impossibile contattare l'attuatore: {e}")

def handle_incoming_data(payload_text, sensor_name):
    """Esegue il parsing dei dati e il salvataggio sul Database MySQL"""
    global last_actuator_state
    
    try:
        data = json.loads(payload_text)
        hr = int(data.get('hr', 0))
        body_temperature = int(data.get('body_temperature', 0))
        spo2 = int(data.get('spo2', 0))
        
        # assegno rischio in base alla soglia
        risk_score = int(data.get('risk', 0))
        
        sensor_map = {'Sensori': 1}
        sensor_id = sensor_map.get(sensor_name, 0)
        
        #query per inserire i dati nel database
        query = "INSERT INTO Health_Measurements (sensor_id, heart_rate, body_temperature, spo2, risk_score) VALUES (%s, %s, %s, %s, %s)"
        success = db.query(query, (sensor_id, hr, body_temperature, spo2, risk_score))
        
        if success:
            print(f" DB Aggiornato -> Sensore: {sensor_name} | HR: {hr}, Temp: {body_temperature}, SpO2: {spo2}, Classe Rischio: {risk_score}")
            
        # aggiorno l'attuatore solo se la soglia cambia 
        if risk_score != last_actuator_state:
            asyncio.create_task(update_actuator(sensor_name, risk_score))
            last_actuator_state = risk_score
            
    except Exception as e:
        print(f"Errore nei dati da {sensor_name}: {e}")


async def observe_sensor(sensor_ip, sensor_name):
    """
        Implementa OBSERVE di CoAP:
        1. Si registra per osservare la risorsa /vitals del sensore
        2. Riceve notifiche push ogni volta che ci sono nuovi dati
        3. In caso di disconnessione, tenta automaticamente la riconnessione
    """
    while True:
        print(f"Gestisco sottoscrizione OBSERVE per {sensor_name} ({sensor_ip})...")
        
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
            print(f"\n Impossibile raggiungere {sensor_name}: {e}")
            
        print("--- Ritento la connessione tra 5 secondi... ---")
        await asyncio.sleep(5)



async def main():
    print("Avvio Smart Health Cloud Application...")
    
    # creo un task asincrono per osservare il dongle
    task_s1 = asyncio.create_task(observe_sensor(SENSOR_1_IP, "Sensori"))
    
    try:
        await asyncio.gather(task_s1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nChiusura dell'applicazione...")
        task_s1.cancel()
        await asyncio.gather(task_s1, return_exceptions=True)

if __name__ == '__main__':
    try:
        asyncio.run(main()) #avvio loop asincrono 
    except KeyboardInterrupt:
        pass
    finally:
        db.close()
        print("Uscita completata.")