# SmartHealth IoT - Cloud Application

Un sistema di **monitoraggio della salute** con IoT, machine learning e cloud computing.

## 📋 Panoramica del Progetto

SmartHealth è una piattaforma IoT completa che integra:

- 🌡️ **Sensori IoT (Contiki-NG su NRF52840)** per frequenza cardiaca, SpO₂ e rischio clinico
- 🚨 **Attuatore IoT** per gestione allarmi via CoAP
- ☁️ **Cloud Backend Python** per acquisizione dati e storage su MySQL
- 📊 **Dashboard Tkinter** per visualizzazione real-time
- 🤖 **Machine Learning** per classificazione del rischio clinico

## 🗂️ Struttura del Progetto

```
SmartHealth/
├── Cloud_Application/
│   ├── SmartHealthCloud.py          # Backend (polling CoAP + MySQL)
│   ├── frontend/
│   │   ├── SmartHealthUI.py         # Frontend (dashboard Tkinter)
│   │   ├── coap_service.py          # Servizio lettura DB
│   │   ├── view_components.py       # Componenti UI
│   │   └── configuration_manager.py # Config database
│   ├── backend/
│   │   ├── db_manager.py            # Gestore DB
│   │   └── db_setup.sql             # Schema database
│   ├── nodes_configuration.json     # Configurazione sensori
│   └── requirements.txt
├── IoT_Nodes/
│   ├── sensor_nodes/               
│   │   ├── Makefile
│   │   ├── project_configuration.h
│   │   ├── res_vitals.c
│   │   ├── res_sampling.c
│   │   ├── vitals_classifier.h
│   │   └── sensor.c
│   └── actuator_nodes/             
│   │   ├── Makefile
│   │   ├── project_configuration.h
│   │   ├── res_treshold.c
│   │   └── actuator.c
├── Machine_Learning/
│   ├── ML_model.ipynb               # Training classificatore
│   └── dataset/
│       └── smart_health_dataset.csv
├── SimulazioneCooja/                # File simulazione Cooja
└── Documentation/
```

## ⚙️ Setup Iniziale

### 1️⃣ Creare l'Ambiente Virtuale Python

```bash
cd Cloud_Application
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure: venv\Scripts\activate  # Windows
```

### 2️⃣ Installare le Dipendenze

```bash
pip install -r requirements.txt
```

Le dipendenze includono:
- `mysql-connector-python`: Connessione al database MySQL
- `rich`: Output formattato in terminale
- `pandas`, `scikit-learn`: ML e data processing
- `emlearn`: Embedding ML per microcontroller

### 3️⃣ Configurare il Database MySQL

Prima assicurati che MySQL sia in esecuzione, poi:

```bash
cd Cloud_Application
mysql -u root -p1 < db_setup.sql
```

Questo crea:
- **Database**: `SmartHealthIoT`
- **Tabella**: `Health_Measurements` (sensor_id, heart_rate, spo2, risk_score, timestamp)

**Credenziali di default**:
- User: `root`
- Password: `1`
- Database: `SmartHealthIoT`

> 💡 Se usi una password diversa, modifica `frontend/configuration_manager.py`

## 🚀 Avvio del Sistema (Hardware Reale + Cooja)

Il sistema richiede l'avvio sequenziale di più componenti. Segui i passi nell'ordine indicato.

### Passo 1️⃣ — Collegare i Dongle Fisici

Collega i dongle NRF52840 alle porte USB del PC. Verifica che siano riconosciuti dal sistema (es. `/dev/ttyACM0`, `/dev/ttyACM1`, ...). I dongle fisici devono essere flashati con sensor.c e border-router.c.

### Passo 2️⃣ — Avviare il Border Router sul Dongle

Dalla cartella del border router, flasha e connetti il dongle come router di confine IPv6:

```bash
cd contiki-ng/examples/rpl-border-router
make TARGET=nrf52840 BOARD=dongle connect-router PORT=/dev/ttyACM0 
```
(l'ultimo parametro dipende dal tipo di pc).
Questo configura il dongle come border router RPL e rende raggiungibile la rete dei nodi IoT.

Se connettiamo anche il sensore precedentemente flashato, si creerà da DODAG.

### Passo 3️⃣ — Avviare Cooja e Caricare la Simulazione

```bash
cd contiki-ng/tools/cooja
./gradlew run
```
Apri il simulatore **Cooja** e carica il file di simulazione presente nella cartella `SimulazioneCooja/`. Seleziona il file `.csc` dalla finestra di apertura di Cooja.

### Passo 4️⃣ — Avviare la Simulazione in Cooja

Una volta caricata la simulazione, premi **Start** in Cooja per avviare i nodi virtuali (sensori e attuatore).

### Passo 5️⃣ — Avviare il Tunnel IPv6 (tunslip6)

In un terminale dedicato, avvia il tunnel IPv6 tra il PC e la rete Cooja tramite `tunslip6`:

```bash
cd /contiki-ng/tools/serial-io
sudo ./tunslip6 -a 127.0.0.1 -p 60001 fd01::1/64 -t tun1
```

Tieni questo terminale ed anche tutti i terminali aperti fin'ora per tutta la durata del sistema. Il tunnel permette al backend Python di comunicare via CoAP con i nodi della simulazione.

### Passo 6️⃣ — Attivare il Virtual Environment

Apri un nuovo terminale,  attiva il virtual environment e spostati nella cartella `Cloud_Application`:

```bash
source venv/bin/activate
cd Cloud_Application
```

Il prompt dovrebbe diventare simile a:
```
(venv) [user@host Cloud_Application]$
```

### Passo 7️⃣ — Avviare il Backend Cloud

```bash
python SmartHealthCloud.py
```
**Output atteso**:
```
Avvio Smart Health Cloud Application (Polling Sensore)...
In ascolto tramite Polling periodico... (Premi Ctrl+C per uscire)
[DATO DAL SENSORE Sensore_1]: {...}
[✓] Dati salvati! (Sensore: Sensore_1 | HR: 75, SpO2: 98, Risk: 0.15)
```

### Passo 8️⃣ — Avviare il Frontend Dashboard

Apri un ulteriore terminale, attiva l'ambiente venv , spostati nella cartella `frontend`  e avvia la dashboard:

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
ACTUATOR_IP = "fd01::202:2:2:2"
```

## 📦 Note Importanti

- In cooja vengono simulati un LBR e un attuatore. Dal punto di vista dell'hardware abbiamo anche qui un LBR ed un sensore
- Il border router fisico (dongle NRF52840) deve essere collegato **prima** di avviare Cooja
- Il database persiste tra avvii (usa `DROP DATABASE SmartHealthIoT;` per resettare)
- La password di default non dovrebbe essere usata in produzione
