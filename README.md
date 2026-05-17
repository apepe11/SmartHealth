# SmartHealth IoT - Cloud Application

Un sistema integrato di **monitoraggio remoto della salute** con IoT, machine learning e cloud computing.

## 📋 Panoramica del Progetto

- **IoT Sensor Nodes**: Contiki-NG - Raccolgono frequenza cardiaca, saturazione O₂ e calcolano il rischio clinico
- **IoT Actuator Node**: Contiki-NG - Riceve comandi CoAP dal cloud per attivare allarmi
- **Cloud Backend** (Python): Polling periodico dei sensori via CoAP, salvataggio su MySQL, logica di allarme
- **Cloud Frontend** (Python/Tkinter): Dashboard real-time che legge i dati dal database MySQL
- **Machine Learning**: Classificatore Python per l'analisi del rischio clinico (embedding su nodi)

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
│   ├── sensor_nodes/                # Firmware Contiki-NG (heart_rate + SpO2 + rischio)
│   └── actuator_nodes/              # Firmware Contiki-NG (allarme)
├── Machine_Learning/
│   ├── ML_model.ipynb               # Training classificatore
│   └── dataset/
│       └── smart_health_dataset.csv
└── Documentation/

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
cd backend
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

## 🚀 Avvio del Sistema

Il sistema ha **due moduli indipendenti** che vanno lanciati in **due terminali separati**:

### Terminal 1: Backend Cloud (Polling CoAP + MySQL)

```bash
cd Cloud_Application
source venv/bin/activate
python SmartHealthCloud.py
```

Questo avvia:
- Polling periodico dei sensori via CoAP (`fd00::202:2:2:2` e `fd00::203:3:3:3`)
- Salvataggio dati in MySQL ogni 5 secondi
- Logica di allarme quando rischio ≥ 0.50

**Output atteso**:
```
Avvio Smart Health Cloud Application (Multi-Node Polling)...
In ascolto tramite Polling periodico... (Premi Ctrl+C per uscire)
[DATO DAL SENSORE Sensore_1]: {...}
[✓] Dati salvati! (Sensore: Sensore_1 | HR: 75, SpO2: 98, Risk: 0.15)
```

### Terminal 2: Frontend Dashboard (UI Tkinter)

```bash
cd Cloud_Application/frontend
source venv/bin/activate
python SmartHealthUI.py
```

Questo avvia:
- Dashboard Tkinter con 2 card (Sensore 1 e 2)
- Aggiornamento dati in tempo reale (ogni 2 secondi)
- Indicatore visivo di stato (💚 stabile / ⚠️ emergenza)

## 📊 Flusso Dati

```
IoT Sensors (Contiki-NG)
    ↓ (CoAP)
Backend Python (SmartHealthCloud.py)
    ↓ (INSERT)
MySQL Database (SmartHealthIoT)
    ↓ (SELECT)
Frontend Dashboard (SmartHealthUI.py)
```

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
SENSOR_1_IP = "fd00::202:2:2:2"   # Nodo sensore 2
SENSOR_2_IP = "fd00::203:3:3:3"   # Nodo sensore 3
ACTUATOR_IP = "fd00::204:4:4:4"   # Nodo attuatore
```

## 🔧 Troubleshooting

| Problema | Soluzione |
|----------|-----------|
| `ModuleNotFoundError: mysql.connector` | Attiva il venv e installa `pip install -r requirements.txt` |
| `Access denied for user 'root'` | Verifica password MySQL (di default: `1`), cambia in `configuration_manager.py` |
| `Unknown database 'SmartHealthIoT'` | Esegui `mysql -u root -p1 < backend/db_setup.sql` |
| Frontend non mostra dati | Verifica che il backend sia in esecuzione e scriva nel DB |
| Timeout CoAP | Controlla che Cooja e il tunnel tunslip6 siano attivi |

## 📦 Note Importanti

- ⚠️ I nodi IoT devono essere simulati in **Cooja** (simulatore Contiki-NG)
- Per il tunnel IPv6 con Cooja, usa: `sudo tunslip6 -a 127.0.0.1 aaaa::1/64`
- Il database persiste tra avvii (usa `DROP DATABASE SmartHealthIoT;` per resettare)
- Password di default non dovrebbe essere usata in produzione

## 📚 Ulteriori Risorse

- [Contiki-NG Documentation](https://github.com/contiki-ng/contiki-ng)
- [CoAP Protocol (RFC 7252)](https://tools.ietf.org/html/rfc7252)
- [MySQL Documentation](https://dev.mysql.com/doc/)
