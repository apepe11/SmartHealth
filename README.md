# SmartHealth IoT - Cloud Application

Un sistema di **monitoraggio della salute** con IoT, machine learning e cloud computing, implementato interamente su dispositivi hardware reali (Edge Computing).

## 📋 Panoramica del Progetto

SmartHealth è una piattaforma IoT completa che integra:

- 🌡️ **Sensori IoT (Contiki-NG su nRF52840 Dongle)** per frequenza cardiaca, SpO₂ e temperatura.
- 🚨 **Attuatore IoT (nRF52840 Dongle)** come server CoAP puro per gestione allarmi visivi (LED RGB).
- ☁️ **Cloud Backend Python** per acquisizione dati (CoAP Observe), storage su MySQL e logica Closed-Loop.
- 📊 **Dashboard Tkinter** per visualizzazione real-time.
- 🤖 **Machine Learning (TinyML)** per la classificazione del rischio clinico eseguita direttamente sul nodo sensore (Random Forest via `emlearn`).

## 🗂️ Struttura del Progetto

```text
SmartHealth/
├── Cloud_Application/
│   ├── SmartHealthCloud.py          # Backend (Observe CoAP + MySQL + Closed-Loop su Attuatore)
│   ├── frontend/
│   │   ├── SmartHealthUI.py         # Frontend (dashboard Tkinter)
│   │   ├── coap_service.py          # Servizio lettura DB
│   │   ├── view_components.py       # Componenti UI
│   │   └── configuration_manager.py # Config database e gestione statica IP nodi
│   ├── backend/
│   │   ├── db_manager.py            # Gestore DB
│   │   └── db_setup.sql             # Schema database
│   └── requirements.txt
├── IoT_Nodes/                     
│   ├── sensor_nodes/               
│   │   ├── Makefile                # Script per la compilazione (target nrf52840)
│   │   ├── project_configuration.h # File di configurazione radio/canale
│   │   ├── res_vitals.c            # Implementazione risorsa CoAP /vitals (dati biologici)
│   │   ├── res_sampling.c          # Risorsa CoAP dedicata alla gestione dinamica del rate
│   │   ├── vitals_classifier.h     # Header file C contenente il modello Random Forest generato 
│   │   └── sensor.c                # Codice principale sensore, ML e gestione stress test hardware
│   └── actuator_nodes/            
│       ├── Makefile                # Script per la compilazione (target nrf52840)
│       ├── project_configuration.h # Direttive di configurazione radio/canale
│       ├── res_treshold.c          # Gestione risorsa CoAP /threshold
│       └── actuator.c              # Codice principale server CoAP per il controllo cromatico dei LED
├── Machine_Learning/               
│   ├── ML_model.ipynb              # Notebook Colab di training del modello
│   └── dataset/
│       └── smart_health_dataset.csv   # Dataset open-source estratto da Kaggle
└── Documentation/                  # Relazione e diagrammi architetturali
```


## ⚙️ Setup Iniziale (Guida per Ubuntu/Linux)

I seguenti passaggi illustrano come configurare l'ambiente da zero, installando i requisiti di sistema, il database locale e l'ambiente virtuale Python.

### 1 Installare i Prerequisiti di Sistema e attivazione MySQL
Per prima cosa, aggiorna i repository e installa Python, l'ambiente virtuale, la libreria grafica nativa per l'interfaccia (Tkinter) e il server MySQL:

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip python3-tk mysql-server mysql-client

sudo systemctl start mysql
sudo systemctl enable mysql
```
### 2 Configurare il Database MySQL

Crea il database.
```bash
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '1'; FLUSH PRIVILEGES;"

cd Cloud_Application
mysql -u root -p1 < db_setup.sql

```
**Credenziali di default**:
- User: `root`
- Password: `1`
- Database: `SmartHealthIoT`

> 💡 Se usi una password diversa, modifica `frontend/configuration_manager.py`

### 3 Creare l'Ambiente Virtuale Python


```bash
cd Cloud_Application
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure: venv\Scripts\activate  # Windows
```

### 2️⃣ Installare le Dipendenze

```bash
pip install --upgrade pip
pip install -r requirements.txt

```

## 🚀 Avvio del Sistema (Hardware Reale + Cooja)

Il sistema richiede l'avvio sequenziale di più componenti. Segui i passi nell'ordine indicato.

### Passo 1 — Collegare i Dongle Fisici

Collega i dongle NRF52840 alle porte USB del PC. Verifica che siano riconosciuti dal sistema (es. `/dev/ttyACM0`, `/dev/ttyACM1`, ...). I dongle fisici devono essere flashati con sensor.c , actuator.c e border-router.c. con (es. con attuatore):
```bash
make TARGET=nrf52840 BOARD=dongle actuator.dfu-upload PORT=/dev/ttyACMx
```

### Passo 2 — Avviare il Border Router sul Dongle

Dalla cartella del border router, flasha e connetti il dongle come router di confine IPv6:

```bash
cd contiki-ng/examples/rpl-border-router
make TARGET=nrf52840 BOARD=dongle connect-router PORT=/dev/ttyACM0 
```
(l'ultimo parametro dipende dal tipo di pc).
Questo configura il dongle come border router RPL e rende raggiungibile la rete dei nodi IoT.

Se connettiamo anche il sensore e l'attuatore precedentemente flashato, si creerà la DODAG.


### Passo 3 — Collegare gli altri due dongle


### Passo 4 — Attivare il Virtual Environment

Apri un nuovo terminale, attiva il virtual environment e spostati nella cartella `Cloud_Application`:

```bash
source venv/bin/activate
cd Cloud_Application
```

Il prompt dovrebbe diventare simile a:
```
(venv) [user@host Cloud_Application]$
```

### Passo 6 — Avviare il Backend Cloud

```bash
python SmartHealthCloud.py
```
**Output atteso**:
```
[NOTIFICA DA Sensori]: {"hr": 97, "body_temperature": 40, "spo2": 90, "risk": 2}
 💾 DB Aggiornato -> Sensore: Sensori | HR: 97, Temp: 40, SpO2: 90, Rischio: 2
 🚨 EMERGENZA (Rischio 2) rilevata su Sensori! Attivo LED ROSSO su fd00::f6ce:36a6:c68f:cb04...
 🟢 Attuatore aggiornato con successo! (Risposta CoAP: 2.04 Changed)
```

### Passo 8️⃣ — Avviare il Frontend Dashboard

Apri un ulteriore terminale, attiva l'ambiente venv , spostati nella cartella `CloudApplication/frontend`  e avvia la dashboard:

```bash
source venv/bin/activate
cd Cloud_Application/frontend
python SmartHealthUI.py
```
Questo avvia:
- Aggiornamento dati in tempo reale. Con un pannello è possibile controllare il rate (min 1s)
- Indicatore visivo di stato (💚 stabile / ⚠️ emergenza)


## 🛠️ Configurazione

Modifica `Cloud_Application/frontend/configuration_manager.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1",  # Cambia qui se necessario
    "database": "SmartHealthIoT"
}
```

Modifica gli IP dei sensori in `Cloud_Application/SmartHealthCloud.py`:

```python
SENSOR_1_IP = "fd00::f6ce:36b9:a760:ecea"   
ACTUATOR_IP = "fd00::f6ce:36a6:c68f:cb04"
```

## Accuratezza modello ML 
## 🧠 Accuratezza modello ML (TinyML)

```text
--- REPORT DI ACCURATEZZA TINYML ---
              precision    recall  f1-score   support

           0       1.00      1.00      1.00       215
           1       1.00      0.90      0.95       473
           2       0.91      1.00      0.95       494

    accuracy                           0.96      1182
   macro avg       0.97      0.97      0.97      1182
weighted avg       0.96      0.96      0.96      1182
```

## 📦 Note Importanti

- Il database persiste tra avvii (usa `DROP DATABASE SmartHealthIoT;` per resettare)
- La password di default è 1
