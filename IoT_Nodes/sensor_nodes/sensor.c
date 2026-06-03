#include "contiki.h"
#include "coap-engine.h"
#include "sys/log.h"
#include "dev/button-hal.h"
#include <stdlib.h> 

#include "net/routing/routing.h"

#if !CONTIKI_TARGET_COOJA
#include "nrfx.h"
#endif

#include "vitals_classifier.h" // Includo il modello di ML generato con emlearn

#define LOG_MODULE "SmartHealth-Node"
#define LOG_LEVEL LOG_LEVEL_INFO

extern coap_resource_t res_vitals;
extern coap_resource_t res_sampling;

// Parametri vitali inizializzati nei range corretti del dataset
int current_hr = 90;      
int current_spo2 = 98;    
int current_temp = 37;    // FIX: Inizializzato a 37 (fisiologico) invece di 34
int current_risk = 0;

// Rate attuale + variabile per il meccanismo adattivo
uint16_t current_sampling_rate = 5; 
static bool is_network_congested = false; 

int leggi_temperatura_hardware_nrf(void);

PROCESS(smart_health_node, "Smart Health Sensor Node");
AUTOSTART_PROCESSES(&smart_health_node);

PROCESS_THREAD(smart_health_node, ev, data) {
    static struct etimer periodic_timer;

    PROCESS_BEGIN();

    LOG_INFO("Inizializzazione Nodo Smart Health con ML...\n");
    
    // Attivo le risorse CoAP
    coap_activate_resource(&res_vitals, "vitals");
    coap_activate_resource(&res_sampling, "sampling");
    
    LOG_INFO("Risorse CoAP attivate: /vitals e /sampling\n");

    etimer_set(&periodic_timer, current_sampling_rate * CLOCK_SECOND);

    while(1) {
        PROCESS_WAIT_EVENT();

        // Timer periodico per aggiornare i parametri e notificare il Cloud
        if(ev == PROCESS_EVENT_TIMER && data == &periodic_timer) {
            
            #if CONTIKI_TARGET_COOJA
            // Genera una variazione di -1, 0, o +1 grado (Simulazione Cooja)
            int delta_temp = (rand() % 3) - 1; 
            current_temp += delta_temp;

            if(current_temp < 36) current_temp = 36;
            if(current_temp > 40) current_temp = 40;
            #else
            // HARDWARE REALE: Otteniamo il target termico dal chip
            int target_temp = leggi_temperatura_hardware_nrf();

            // Avvicinamento dolce al target hardware per stabilizzare i grafici su Grafana
            if(current_temp < target_temp && current_temp < 40) {
                current_temp += 1;
            } else if(current_temp > target_temp && current_temp > 36) {
                current_temp -= 1;
            } else {
                // Micro-oscillazione casuale sul target per mantenere vivo il dinamismo del segnale
                int micro_oscillation = (rand() % 3) - 1;
                current_temp += micro_oscillation;
            }

            // Vincoli di sicurezza clinica per il rispetto dei confini del dataset di training
            if(current_temp < 36) current_temp = 36;
            if(current_temp > 40) current_temp = 40;
            #endif

            // Frequenza Cardiaca: variazione controllata tra -3 e +3 bpm ad ogni ciclo
            int delta_hr = (rand() % 7) - 3; 
            current_hr += delta_hr;

            if(current_hr < 80) current_hr = 80;
            if(current_hr > 120) current_hr = 120;

            // Saturazione SpO2: variazione controllata tra -1 e +1 % ad ogni ciclo
            int delta_spo2 = (rand() % 3) - 1;
            current_spo2 += delta_spo2;

            if(current_spo2 < 88) current_spo2 = 88;
            if(current_spo2 > 100) current_spo2 = 100;

            // Preparazione delle feature per l'Edge Computing (TinyML)
            int16_t ml_features[3];
            ml_features[0] = (int16_t)current_hr;
            ml_features[1] = (int16_t)current_temp;
            ml_features[2] = (int16_t)current_spo2;

            // Esecuzione locale dell'inferenza tramite l'albero decisionale Random Forest
            current_risk = (int)vitals_rf_model_predict(ml_features, 3);

            LOG_INFO("Temp: %d C | HR: %d bpm | SpO2: %d%%\n", current_temp, current_hr, current_spo2);
            LOG_INFO("Esito Random Forest (Risk): %d\n", current_risk);
            
            // Notifica push via CoAP Observe alla Cloud Application
            coap_notify_observers(&res_vitals);
            
            etimer_set(&periodic_timer, current_sampling_rate * CLOCK_SECOND);
        }
        
        // Pressione del pulsante fisico per la simulazione della rete LLN congestionata
        if(ev == button_hal_press_event) {
            is_network_congested = !is_network_congested;
            
            if(is_network_congested) {
                LOG_INFO("STRESS TEST. Attivazione Meccanismo Adattivo (Rate = 20s)...\n");
                current_sampling_rate = 20; 
                etimer_set(&periodic_timer, current_sampling_rate * CLOCK_SECOND);
            } else {
                LOG_INFO("Rete tornata stabile. Disattivazione Meccanismo Adattivo (Rate = 5s).\n");
                current_sampling_rate = 5; 
                etimer_set(&periodic_timer, current_sampling_rate * CLOCK_SECOND);
            }
        }
    }

    PROCESS_END();
}

// Funzione interna per l'interfacciamento con i registri del chip nRF52840
int leggi_temperatura_hardware_nrf(void) {
#if CONTIKI_TARGET_COOJA
    static int simul_temp = 37;
    int delta_temp = (rand() % 3) - 1; 
    simul_temp += delta_temp;
    return simul_temp;
#else
    // Lettura dal registro hardware del chip nRF52840
    NRF_TEMP->EVENTS_DATARDY = 0;
    NRF_TEMP->TASKS_START = 1;
    while(NRF_TEMP->EVENTS_DATARDY == 0) {}
    NRF_TEMP->TASKS_STOP = 1;
    
    int32_t raw_temp = NRF_TEMP->TEMP;
    int celsius_effettivi = (int)(raw_temp / 4); 

    /*
     * NUOVA LOGICA ADATTIVA:
     * Il chip caldo si attesta solitamente tra 30°C e 33°C.
     * Sottraiamo 30 per azzerare la base di surriscaldamento del silicio.
     */
    int delta_hardware = celsius_effettivi - 30;
    if(delta_hardware < 0) delta_hardware = 0;
    if(delta_hardware > 2) delta_hardware = 2; // Limitiamo l'impatto dell'hardware puro a +2°C

    /* * Introduciamo una fluttuazione casuale più ampia (da 0 a 2) 
     * per simulare gli sbalzi febbrili reali del paziente.
     */
    int variazione_clinica = rand() % 3; // Genera 0, 1 o 2

    // Calcolo finale: Base sana (36) + variazione hardware (0-2) + variazione clinica (0-2)
    int temp_paziente = 36 + delta_hardware + variazione_clinica;
    
    return temp_paziente;
#endif
}