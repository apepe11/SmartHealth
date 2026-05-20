#include "contiki.h"
#include "coap-engine.h"
#include <stdio.h>

// Dichiariamo le variabili esterne gestite in sensor.c
extern int current_hr;
extern int current_spo2;
extern int current_temp;
extern int current_risk;

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

// EVENT_RESOURCE configurata correttamente con 7 argomenti (l'ultimo è NULL)
EVENT_RESOURCE(res_vitals,
         "title=\"Patient Vitals\";rt=\"Health\";obs",
         res_get_handler,
         NULL,
         NULL,
         NULL,
         NULL); // <--- Questo è il 7° argomento che mancava!

static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset) {
    
    int length = snprintf((char *)buffer, preferred_size, 
        "{\"hr\": %d, \"body_temperature\": %d, \"spo2\": %d, \"risk\": %d}", 
        current_hr, current_temp, current_spo2, current_risk);
        
    coap_set_header_content_format(response, APPLICATION_JSON);
    coap_set_payload(response, buffer, length);
}