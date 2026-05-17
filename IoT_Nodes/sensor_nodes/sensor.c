#include "contiki.h"
#include "coap-engine.h"
#include "sys/log.h"
#include "dev/button-hal.h"

#define LOG_MODULE "SmartHealth-Node"
#define LOG_LEVEL LOG_LEVEL_INFO

// Dichiarazione delle risorse esterne
extern coap_resource_t res_vitals;
extern coap_resource_t res_sampling;

// Frequenza di default in secondi
uint16_t current_sampling_rate = 5; 

PROCESS(smart_health_node, "Smart Health Sensor Node");
AUTOSTART_PROCESSES(&smart_health_node);

PROCESS_THREAD(smart_health_node, ev, data) {
    static struct etimer periodic_timer;

    PROCESS_BEGIN();

    LOG_INFO("Inizializzazione Nodo Smart Health...\n");
    
    // Attiva il motore CoAP e registra le risorse
    coap_activate_resource(&res_vitals, "vitals");
    coap_activate_resource(&res_sampling, "sampling");
    
    LOG_INFO("Risorse CoAP attivate: /vitals e /sampling\n");

    // Imposta il timer ciclico
    etimer_set(&periodic_timer, current_sampling_rate * CLOCK_SECOND);

    while(1) {
        PROCESS_WAIT_EVENT();

        // Se è scattato il timer
        if(ev == PROCESS_EVENT_TIMER && data == &periodic_timer) {
            LOG_INFO("Campionamento dati in corso... (Rate: %d sec)\n", current_sampling_rate);
            
            // Re-imposta il timer usando l'intervallo aggiornato
            etimer_set(&periodic_timer, current_sampling_rate * CLOCK_SECOND);
        }
        
        // Simula un'emergenza premendo il bottone fisico sul dongle
        if(ev == button_hal_press_event) {
            LOG_INFO("EMERGENZA: Pulsante premuto! Simulo picco cardiaco...\n");
        }
    }

    PROCESS_END();
}