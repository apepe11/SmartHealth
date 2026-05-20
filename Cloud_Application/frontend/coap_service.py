# coap_service.py
import mysql.connector
import asyncio
import json
import threading
from aiocoap import *
from configuration_manager import DB_CONFIG

class DataService:
    def __init__(self):
        self.config = DB_CONFIG

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    def get_latest_measurements(self):
        """Recupera l'ultimissimo dato salvato per ciascun sensore"""
        connection = self._get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT m1.sensor_id, m1.heart_rate, m1.body_temperature, m1.spo2, m1.risk_score, m1.timestamp
            FROM Health_Measurements m1
            INNER JOIN (
                SELECT sensor_id, MAX(timestamp) as max_ts
                FROM Health_Measurements
                GROUP BY sensor_id
            ) m2 ON m1.sensor_id = m2.sensor_id AND m1.timestamp = m2.max_ts
        """
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Errore lettura DB: {e}")
            return []
        finally:
            cursor.close()
            connection.close()


class CoAPNetworkService:
    """Gestisce l'invio dei comandi di controllo (User Input) verso i nodi IoT"""
    
    def _run_async_put(self, ip, resource, payload):
        """Esegue la richiesta PUT in un ciclo asincrono isolato"""
        async def put_task():
            try:
                context = await Context.create_client_context()
                payload_bytes = json.dumps(payload).encode('utf-8')
                
                request = Message(code=PUT, payload=payload_bytes, uri=f"coap://[{ip}]/{resource}")
                request.opt.content_format = 50  # APPLICATION_JSON
                
                response = await context.request(request).response
                print(f"[✓ UI CoAP] PUT eseguita con successo su [{ip}]/{resource}. Risposta nodo: {response.code}")
            except Exception as e:
                print(f"[❌ UI CoAP ERRORE] Impossibile inviare PUT a [{ip}]/{resource}: {e}")
        
        asyncio.run(put_task())

    def send_new_sampling_rate(self, sensor_ip, new_rate):
        """Invia il nuovo sampling rate al sensore (Risorsa /sampling)"""
        payload = {"new_sr": int(new_rate)}
        print(f"[UI] Invio nuovo sampling rate ({new_rate}s) a {sensor_ip}...")
        # Spediamo il comando in un Thread separato per non bloccare la UI di Tkinter
        threading.Thread(target=self._run_async_put, args=(sensor_ip, "sampling", payload), daemon=True).start()

    def send_new_threshold(self, actuator_ip, new_threshold):
        """Invia la nuova soglia di allarme all'attuatore (Risorsa /threshold)"""
        payload = {"new_t": int(new_threshold)}
        print(f"[UI] Invio nuova soglia rischio ({new_threshold}) a {actuator_ip}...")
        threading.Thread(target=self._run_async_put, args=(actuator_ip, "threshold", payload), daemon=True).start()