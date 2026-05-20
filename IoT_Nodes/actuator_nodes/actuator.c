#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "contiki.h"
#include "coap-engine.h"
#include "coap-blocking-api.h"
#include "coap-observe-client.h"
#include "os/dev/leds.h"
#include "sys/log.h"
#include "net/routing/routing.h" // Inclusione fondamentale per NETSTACK_ROUTING

#define LOG_MODULE "SmartHealth-Actuator"
#define LOG_LEVEL LOG_LEVEL_INFO

// ATTENZIONE: Assicurati che questo IPv6 corrisponda SEMPRE a quello del sensore!
#define SENSOR_EP "coap://[fd00::f6ce:36b9:a760:ecea]:5683"
#define OBSERVE_URI "vitals" // Nome della risorsa CoAP sul sensore

extern coap_resource_t res_threshold;

// Soglia di allarme: 0 = Sano, 1 = Attenzione, 2 = Emergenza
int alarm_threshold = 2;

// Struttura dati per memorizzare l'endpoint del sensore e la sessione d'osservazione
static coap_endpoint_t server_ep;
static coap_observee_t *obs_session = NULL;

PROCESS(actuator_node, "Smart Health Actuator Node");
AUTOSTART_PROCESSES(&actuator_node);

// Callback che si attiva OGNI VOLTA che il sensore nRF invia dati freschi
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
        
        LOG_INFO("Dati Paziente Ricevuti dal Sensore: %s\n", data);

        // Estrazione del valore di "risk" inviato nel JSON
        char *ptr = strstr(data, "\"risk\":");
        if(ptr != NULL) {
            // Estrae l'intero saltando i caratteri di '"risk":'
            int current_risk = atoi(ptr + 7); 
            
            // LOGICA DI CONTROLLO HARDWARE DEI LED (Rischio vs Soglia)
            if(current_risk >= alarm_threshold) {
                LOG_INFO("[ALLARME] Rischio rilevato (%d) >= Soglia impostata (%d)! LED ROSSO!\n", current_risk, alarm_threshold);
                leds_on(LEDS_RED);
                leds_off(LEDS_GREEN);
            } else {
                LOG_INFO("[OK] Rischio rilevato (%d) < Soglia impostata (%d). LED VERDE.\n", current_risk, alarm_threshold);
                leds_off(LEDS_RED);
                leds_on(LEDS_GREEN);
            }
        }
    }
}

PROCESS_THREAD(actuator_node, ev, data) {
    static struct etimer rpl_check_timer;
    PROCESS_BEGIN();

    LOG_INFO("Inizializzazione Nodo Attuatore...\n");
    
    // 1. ATTIVA LA RISORSA COAP LOCALE (Per permettere a Python di fare le PUT)
    coap_activate_resource(&res_threshold, "threshold");
    LOG_INFO("Risorsa /threshold attivata per il controllo remoto Python.\n");

    // Inizializza lo stato dei LED all'avvio
    leds_off(LEDS_RED);
    leds_on(LEDS_GREEN);

    // 2. ATTESA CONNESSIONE ALLA RETE MESH RPL
    etimer_set(&rpl_check_timer, CLOCK_SECOND * 5);
    while(!NETSTACK_ROUTING.node_is_reachable()) {
        LOG_INFO("In attesa di una rotta RPL valida...\n");
        PROCESS_WAIT_EVENT_UNTIL(ev == PROCESS_EVENT_TIMER && data == &rpl_check_timer);
        etimer_reset(&rpl_check_timer);
    }

    LOG_INFO("Rete RPL connessa con successo!\n");
    
    // 3. PARSING DELL'INDIRIZZO IPV6 DEL SENSORE
    if(coap_endpoint_parse(SENSOR_EP, strlen(SENSOR_EP), &server_ep) == 0) {
        LOG_ERR("ERRORE CRITICO: Impossibile fare il parsing dell'IP del sensore!\n");
        PROCESS_EXIT();
    }

    // 4. RICHIESTA REALE DI OBSERVE CON LA FUNZIONE NATIVA REALE DEL TUO BRANCH
    LOG_INFO("Sottoscrizione alla risorsa CoAP: %s/%s\n", SENSOR_EP, OBSERVE_URI);
    
    // Questa è la chiamata ufficiale supportata dalla tua libreria coap-observe-client.h
    obs_session = coap_obs_request_registration(&server_ep, OBSERVE_URI, notification_callback, NULL);
    
    if(obs_session == NULL) {
        LOG_ERR("Richiesta Observe fallita all'avvio.\n");
    } else {
        LOG_INFO("Sottoscrizione avviata con successo!\n");
    }

    // Mantieni il processo vivo per ascoltare eventi di rete e modifiche Python
    while(1) {
        PROCESS_YIELD();
    }

    PROCESS_END();
}