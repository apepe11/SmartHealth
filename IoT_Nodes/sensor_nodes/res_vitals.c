#include "contiki.h"
#include "coap-engine.h"
#include <stdio.h>

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

RESOURCE(res_vitals,
         "title=\"Patient Vitals\";rt=\"Health\"",
         res_get_handler,
         NULL,
         NULL,
         NULL);

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset) {
    
    // Valori statici di base (Paziente sano)
    int hr = 75;
    int spo2 = 98;
    float risk_score = 0.15; 

    // Trucco per i test: usiamo una variabile statica per contare le richieste.
    // Ogni 5 richieste (GET), simuliamo una situazione clinica di stress.
    static int request_counter = 0;
    request_counter++;
    
    if(request_counter % 5 == 0) {
        hr = 120;           // Tachicardia
        spo2 = 88;          // Ipossia
        risk_score = 0.92;  // Rischio Critico (Sostituisce il ML per ora)
    }

    // Formatta i dati in una stringa JSON
    int length = snprintf((char *)buffer, preferred_size, 
        "{\"hr\": %d, \"spo2\": %d, \"risk\": %.2f}", 
        hr, spo2, risk_score);
        
    coap_set_header_content_format(response, APPLICATION_JSON);
    coap_set_payload(response, buffer, length);
}