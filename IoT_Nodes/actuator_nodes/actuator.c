#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "contiki.h"
#include "coap-engine.h"
#include "coap-blocking-api.h"
#include "coap-observe-client.h"
#include "os/dev/leds.h"
#include "sys/log.h"

#define LOG_MODULE "SmartHealth-Actuator"
#define LOG_LEVEL LOG_LEVEL_INFO

// Indirizzo IP del Sensore (In Cooja di solito fd00::202:2:2:2 per il nodo 2)
// POTRAI CAMBIARLO UNA VOLTA CREATA LA RETE COOJA
#define SENSOR_EP "coap://[fd00::202:0002:0002:0002]:5683"
#define OBSERVE_URI "/vitals"

extern coap_resource_t res_threshold;
float alarm_threshold = 0.85; // Soglia di rischio default

PROCESS(actuator_node, "Smart Health Actuator Node");
AUTOSTART_PROCESSES(&actuator_node);

// Handler chiamato automaticamente ogni volta che il sensore pubblica nuovi dati
static void notification_callback(coap_observee_t *obs, void *notification, coap_notification_flag_t flag) {
    int len = 0;
    const uint8_t *payload = NULL;

    if(notification) {
        len = coap_get_payload(notification, &payload);
    }
    
    if(len > 0) {
        char data[128];
        memcpy(data, payload, len);
        data[len] = '\0';
        
        LOG_INFO("Dati Paziente Ricevuti: %s\n", data);

        // Estrazione bruta del "risk" dal JSON per evitare librerie pesanti
        char *ptr = strstr(data, "\"risk\":");
        if(ptr != NULL) {
            float current_risk = atof(ptr + 7);
            
            // LOGICA DELL'ALLARME MEDICO
            if(current_risk >= alarm_threshold) {
                LOG_INFO("[ALLARME] Rischio %.2f supera soglia %.2f! ATTIVAZIONE SIRENA/LED ROSSO\n", current_risk, alarm_threshold);
                leds_on(LEDS_RED);
                leds_off(LEDS_GREEN);
            } else {
                LOG_INFO("[OK] Rischio %.2f sotto controllo.\n", current_risk);
                leds_off(LEDS_RED);
                leds_on(LEDS_GREEN);
            }
        }
    }
}

PROCESS_THREAD(actuator_node, ev, data) {
    static coap_endpoint_t sensor_endpoint;

    PROCESS_BEGIN();

    LOG_INFO("Inizializzazione Nodo Attuatore...\n");
    
    // Attiva la risorsa per ricevere comandi dal Cloud Python
    coap_activate_resource(&res_threshold, "threshold");

    // Accende il LED Verde (Sistema attivo e pronto)
    leds_on(LEDS_GREEN);

    // Aspetta un paio di secondi per dare tempo alla rete RPL di formarsi
    static struct etimer et;
    etimer_set(&et, 5 * CLOCK_SECOND);
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));

    // Si iscrive alla risorsa /vitals del nodo Sensore
    LOG_INFO("Avvio Observe verso %s%s\n", SENSOR_EP, OBSERVE_URI);
    coap_endpoint_parse(SENSOR_EP, strlen(SENSOR_EP), &sensor_endpoint);
    
    // ECCO LA FUNZIONE CHE MANCAVA (senza la variabile obs davanti)
    coap_obs_request_registration(&sensor_endpoint, OBSERVE_URI, notification_callback, NULL);

    while(1) {
        PROCESS_YIELD();
    }

    PROCESS_END();
}