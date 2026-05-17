import json
import os

class ConfigManager:
    def __init__(self, filepath="nodes_configuration.json"):
        self.filepath = filepath
        self.config = {"sensors": [], "actuators": []}
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.config = json.load(f)
            except json.JSONDecodeError:
                print(f"[Errore Config] File {self.filepath} corrotto. Caricato template vuoto.")
        else:
            self.save()

    def save(self):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"[Errore Config] Impossibile salvare il file: {e}")

    def get_sensors(self):
        return self.config.get("sensors", [])

    def get_actuators(self):
        return self.config.get("actuators", [])

    def update_sensor_rate(self, sensor_id, new_rate):
        for sensor in self.config.get("sensors", []):
            if sensor["id"] == sensor_id:
                sensor["sampling_rate"] = new_rate
                self.save()
                return True
        return False

    def update_actuator_threshold(self, actuator_id, new_threshold):
        for act in self.config.get("actuators", []):
            if act["id"] == actuator_id:
                act["threshold"] = new_threshold
                self.save()
                return True
        return False