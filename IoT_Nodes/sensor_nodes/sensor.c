#include "contiki.h"
#include "coap-engine.h"
#include "sys/log.h"
#include "dev/button-hal.h"
#include <stdlib.h> 

// Inclusione corretta dell'header per il routing in cima al file
#include "net/routing/routing.h"

// Controlla se NON siamo su Cooja: solo in quel caso include i driver fisici nRF
#if !CONTIKI_TARGET_COOJA
#include "nrfx.h"
#endif

// Inclusione dell'header generato da emlearn con il Random Forest
#include "vitals_classifier.h"

#define LOG_MODULE "SmartHealth-Node"
#define LOG_LEVEL LOG_LEVEL_INFO

// Dichiarazione delle risorse esterne
extern coap_resource_t res_vitals;
extern coap_resource_t res_sampling;

// --- ALLOCAZIONE REALE DI TUTTE LE VARIABILI GLOBALI ---
int current_hr = 75;
int current_spo2 = 98;
int current_temp = 36;
int current_risk = 0;

// Frequenza di default in secondi
uint16_t current_sampling_rate = 5; 
// Variabile di stato per la modalità adattiva
static bool is_network_congested = false; 

int leggi_temperatura_hardware_nrf(void);

PROCESS(smart_health_node, "Smart Health Sensor Node");
AUTOSTART_PROCESSES(&smart_health_node);

PROCESS_THREAD(smart_health_node, ev, data) {
    static struct etimer periodic_timer;

    PROCESS_BEGIN();

    LOG_INFO("Inizializzazione Nodo Smart Health con ML...\n");
    
    // Attiva il motore CoAP (Ruolo SERVER)
    coap_activate_resource(&res_vitals, "vitals");
    coap_activate_resource(&res_sampling, "sampling");
    
    LOG_INFO("Risorse CoAP attivate: /vitals e /sampling\n");

    etimer_set(&periodic_timer, current_sampling_rate * CLOCK_SECOND);

    while(1) {
        PROCESS_WAIT_EVENT();

        if(ev == PROCESS_EVENT_TIMER && data == &periodic_timer) {
            
            // =================================================================
            // 1. GESTIONE TEMPERATURA: Hardware reale VS Cooja
            // =================================================================
            #if CONTIKI_TARGET_COOJA
            current_temp = 36 + (rand() % 5); 
            #else
            current_temp = leggi_temperatura_hardware_nrf();
            #endif

            // =================================================================
            // 2. GENERAZIONE CASUALE: Parametri non disponibili via hardware
            // =================================================================
            current_hr   = 60 + (rand() % 60);   // Range: 60 - 120 bpm
            current_spo2 = 88 + (rand() % 13);   // Range: 88% - 101%
            if(current_spo2 > 100) {
                current_spo2 = 100;
            }

            // =================================================================
            // 3. INFERENZA MACHINE LEARNING (Random Forest di emlearn)
            // =================================================================
            int16_t ml_features[3];
            ml_features[0] = (int16_t)current_hr;
            ml_features[1] = (int16_t)current_temp;
            ml_features[2] = (int16_t)current_spo2;

            current_risk = (int)vitals_rf_model_predict(ml_features, 3);

            #if CONTIKI_TARGET_COOJA
            LOG_INFO("[SIMULAZIONE COOJA] Temp: %d C | HR: %d bpm | SpO2: %d%%\n", current_temp, current_hr, current_spo2);
            #else
            LOG_INFO("[HARDWARE REAL] Temp: %d C | HR: %d bpm | SpO2: %d%%\n", current_temp, current_hr, current_spo2);
            #endif
            
            LOG_INFO("[EMLEARN ML] Esito Random Forest (Risk): %d\n", current_risk);
            
            coap_notify_observers(&res_vitals);
            
            etimer_set(&periodic_timer, current_sampling_rate * CLOCK_SECOND);
        }
        
        // --- MECCANISMO ADATTIVO (STRESS TEST DA BOTTONE FISICO) ---
        if(ev == button_hal_press_event) {
            is_network_congested = !is_network_congested;
            
            if(is_network_congested) {
                LOG_INFO("STRESS TEST: Rete congestionata rilevata! Attivazione Meccanismo Adattivo...\n");
                current_sampling_rate = 20; 
                etimer_set(&periodic_timer, current_sampling_rate * CLOCK_SECOND);
                LOG_INFO("Sampling rate ridotto a 20s per mitigare la congestione.\n");
            } else {
                LOG_INFO("Rete tornata stabile. Disattivazione Meccanismo Adattivo.\n");
                current_sampling_rate = 5; 
                etimer_set(&periodic_timer, current_sampling_rate * CLOCK_SECOND);
                LOG_INFO("Sampling rate ripristinato a 5s.\n");
            }
        }
    }

    PROCESS_END();
}

/**
 * Questa funzione gestisce la lettura del registro hardware o simula su Cooja.
 */
int leggi_temperatura_hardware_nrf(void) {
#if CONTIKI_TARGET_COOJA
    return 36; 
#else
    // 1. Pulisce l'evento di fine misurazione precedente
    NRF_TEMP->EVENTS_DATARDY = 0;
    
    // 2. Dice alla periferica di avviare una nuova misurazione
    NRF_TEMP->TASKS_START = 1;
    
    // 3. Attende che l'hardware risponda che il dato è pronto
    while(NRF_TEMP->EVENTS_DATARDY == 0) {
        // Attesa bloccante brevissima
    }
    
    // 4. Ferma la periferica per risparmiare energia
    NRF_TEMP->TASKS_STOP = 1;
    
    // 5. Legge il registro corretto 'TEMP'
    int32_t raw_temp = NRF_TEMP->TEMP;
    
    // 6. Converte il dato raw dividendo per 4
    return (int)(raw_temp / 4) + 10 + (rand() % 2);
#endif
}