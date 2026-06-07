import asyncio
import json
import threading
from aiocoap import *
from configuration_manager import DB_CONFIG, SENSORS_CONFIG
from db_manager import DBManager

active_ids = [cfg["id"] for cfg in SENSORS_CONFIG.values()]
db_shared = DBManager(active_sensors=active_ids)

class DataService:
    def get_latest_measurements(self):
        return db_shared.fetch_latest_measurements()


class CoAPNetworkService:  
    def _run_async_put(self, ip, resource, payload):
        async def put_task():
            try:
                context = await Context.create_client_context()
                payload_bytes = json.dumps(payload).encode('utf-8')
                
                request = Message(code=PUT, payload=payload_bytes, uri=f"coap://[{ip}]/{resource}")
                request.opt.content_format = 50 
                
                response = await context.request(request).response
                print(f" PUT eseguita con successo. Risposta nodo: {response.code}")
            except Exception as e:
                print(f" Impossibile inviare PUT a [{ip}]/{resource}: {e}")
        
        asyncio.run(put_task())

    def send_new_sampling_rate(self, sensor_ip, new_rate):
        payload = {"new_sr": int(new_rate)}
        print(f" Invio nuovo sampling rate ({new_rate}s) a {sensor_ip}...")
        
        for s_name, cfg in SENSORS_CONFIG.items():
            if cfg["sensor_ip"] == sensor_ip:
                db_shared.update_sampling_rate(cfg["id"], int(new_rate))

        threading.Thread(target=self._run_async_put, args=(sensor_ip, "sampling", payload), daemon=True).start()