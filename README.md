# SmartHealth

SmartHealth is an integrated IoT and machine learning project for remote health monitoring.

## Project overview

- IoT sensor node(s) collect vital signs and send measurements to the network.
- IoT actuator node(s) receive control commands and can trigger alerts or actions.
- A Python cloud application stores readings in a database and provides a user interface.
- A machine learning workflow trains a classifier from synthetic vital-sign data and exports the model for embedded use.

## Repository structure

- `Cloud_Application/`: Python UI, configuration, database setup, and CoAP service helpers.
- `IoT_Nodes/`: Contiki-NG firmware for sensor and actuator nodes.
- `Machine_Learning/`: Notebook workflow, dataset generation, and ML model export.
- `Documentation/`: Project documentation and notes.

## Setup guide

1. Create a Python virtual environment:
   - `python3 -m venv venv`
   - `source venv/bin/activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Initialize the database:
   - `cd Cloud_Application/backend`
   - `mysql -u root -p < db_setup.sql`
4. Run the UI:
   - `python Cloud_Application/SmartHealthUI.py`

> Note: `venv/` is intentionally excluded from version control.
