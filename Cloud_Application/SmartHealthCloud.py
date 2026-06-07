import asyncio
import json
from aiocoap import *

from frontend.configuration_manager import DB_CONFIG, SENSORS_CONFIG
from frontend.db_manager import DBManager


active_sensor_ids = [config["id"] for config in SENSORS_CONFIG.values()]

db = DBManager(
    host=DB_CONFIG["host"],
    user=DB_CONFIG["user"],
    database=DB_CONFIG["database"],
    active_sensors=active_sensor_ids
)

last_sent_threshold = None
# funzione per inviare la PUT all'attuatore con il nuovo threshold
async def send_threshold_to_actuator(new_threshold, sensor_name="Sensori"):
    try:
        actuator_ip = SENSORS_CONFIG[sensor_name]["actuator_ip"]
        
        context = await Context.create_client_context()
        
        payload = json.dumps({"threshold": int(new_threshold)}).encode('utf-8')
        
        request = Message(code=PUT, payload=payload)
        request.set_request_uri(f"coap://[{actuator_ip}]:5683/threshold")
        
        print(f" Invio PUT /threshold. Valore: {new_threshold}")
        response = await context.request(request).response
        print(f" Risposta Ricevuta dall'Attuatore: {response.code}")
        return response
    except Exception as e:
        print(f" ❌ Errore durante l'invio della PUT all'attuatore: {e}")
        return None
# funzione per gestire i dati in arrivo dai sensori, aggiornare il DB e decidere se inviare nuovi threshold
def handle_incoming_data(payload_text, sensor_name):
    global last_sent_threshold
    try:
        data = json.loads(payload_text)
        hr = int(data.get('hr', 0))
        body_temperature = int(data.get('body_temperature', 0))
        spo2 = int(data.get('spo2', 0))
        risk_score = int(data.get('risk', 0))
        
        sensor_id = SENSORS_CONFIG[sensor_name]["id"]
        if 'sr' in data:
            db.update_sampling_rate(sensor_id, int(data['sr']))
        else:
            if sensor_id not in db.sampling_rates:
                db.update_sampling_rate(sensor_id, 5)
        
        if db.connect():
            try:
                cursor = db.connection.cursor()
                query = """
                    INSERT INTO Health_Measurements (sensor_id, heart_rate, body_temperature, spo2, risk_score, timestamp, status) 
                    VALUES (%s, %s, %s, %s, %s, NOW(), 'ONLINE')
                """
                cursor.execute(query, (sensor_id, hr, body_temperature, spo2, risk_score))
                cursor.close()
                print(f" 💾 Aggiorno DB | HR: {hr}, Temp: {body_temperature}, SpO2: {spo2}%, Rischio: {risk_score}")
                

                if risk_score >= 2:
                    target_threshold = 2 
                elif risk_score == 1:
                    target_threshold = 1  
                else:
                    target_threshold = 0  

                if target_threshold != last_sent_threshold:
                    if target_threshold == 2:
                        print(f" ⚠️ Rischio critico ({risk_score}).")
                    elif target_threshold == 1:
                        print(f" 🟡 Stato di attenzione ({risk_score}).")
                    else:
                        print(f" ✅ Parametri rientrati nella norma ({risk_score}).")
                    
                    last_sent_threshold = target_threshold
                    asyncio.create_task(send_threshold_to_actuator(target_threshold, sensor_name))
                
            except Exception as sql_err:
                print(f" ❌ Errore durante l'inserimento SQL: {sql_err}")
            
    except Exception as e:
        print(f" ❌ Errore nel parsing dei dati da {sensor_name}: {e}")
# funzione per osservare i dati dai sensori CoAP
async def observe_sensor(sensor_ip, sensor_name):
    while True:
        try:
            context = await Context.create_client_context()
            request = Message(code=GET, uri=f"coap://[{sensor_ip}]:5683/vitals", observe=0)
            protocol_request = context.request(request)
            
            first_response = await protocol_request.response
            payload_text = first_response.payload.decode('utf-8')
            print(f"\nPrimo Messaggio: {payload_text}")
            handle_incoming_data(payload_text, sensor_name)
            
            async for response in protocol_request.observation:
                payload_text = response.payload.decode('utf-8')
                print(f"\nSensore: {payload_text}")
                handle_incoming_data(payload_text, sensor_name)
                
        except asyncio.CancelledError:
            print(f"\n⏹️ Monitoraggio interrotto.")
            break
        except Exception as e:
            print(f"\n⚠️ Sensore non raggiungibile: {e}")
            
        print("🔄 Ritento la connessione tra 5 secondi...")
        await asyncio.sleep(5)

async def main():
    print("Avvio Smart Health Cloud")
    
    tasks = []
    for sensor_name, config in SENSORS_CONFIG.items():
        sensor_ip = config["sensor_ip"]
        tasks.append(asyncio.create_task(observe_sensor(sensor_ip, sensor_name)))
    
    try:
        await asyncio.gather(*tasks)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\n🛑 Chiusura dei servizi CoAP...")
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
        print("Uscita completata.")